"""
Progress service for tracking and managing user learning progress.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from app.models.progress_model import (
    LessonProgress,
    ModuleProgress,
    UserProgress,
    ProgressUpdateRequest,
    ProgressAnalytics,
    KnowledgeEmbedding
)
from app.llm.progress_analytics_llm import progress_analytics_llm
from app.services.knowledge_state_embeddings_service import knowledge_state_embeddings_service
from app.services.vector_db_service import vector_db_service
from app.llm.embeddings import embedding_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

class ProgressService:
    """Service for managing user progress tracking."""
    
    def __init__(self):
        """Initialize the Progress Service with in-memory storage."""
        self.lesson_progress: Dict[str, LessonProgress] = {}  # Key: f"{user_id}:{lesson_id}"
        self.module_progress: Dict[str, ModuleProgress] = {}  # Key: f"{user_id}:{module_id}"
        self.user_progress: Dict[str, UserProgress] = {}  # Key: f"{user_id}:{subject}"
        self.analytics_cache: Dict[str, ProgressAnalytics] = {}  # Key: f"{user_id}:{subject}"
    
    def update_progress(self, request: ProgressUpdateRequest) -> UserProgress:
        """
        Update user's progress for a lesson or module.
        
        Args:
            request: Progress update request containing user ID and progress details.
            
        Returns:
            Updated UserProgress object.
        """
        # Update lesson progress if lesson_id is provided
        if request.lesson_id:
            lesson_key = f"{request.user_id}:{request.lesson_id}"
            lesson_progress = self.lesson_progress.get(lesson_key)
            
            if not lesson_progress:
                lesson_progress = LessonProgress(
                    lesson_id=request.lesson_id,
                    user_id=request.user_id
                )
            
            # Update lesson-specific properties
            if request.completed is not None:
                lesson_progress.completed = request.completed
            if request.score is not None:
                lesson_progress.score = request.score
            if request.time_spent_seconds is not None:
                lesson_progress.time_spent_seconds = request.time_spent_seconds
            if request.repeated_mistakes is not None:
                lesson_progress.repeated_mistakes = request.repeated_mistakes
            if request.notes is not None:
                lesson_progress.notes = request.notes
            
            lesson_progress.attempts += 1
            lesson_progress.last_interaction = datetime.now()
            
            # Store the updated lesson progress
            self.lesson_progress[lesson_key] = lesson_progress
        
        # Update module progress if module_id is provided
        if request.module_id:
            module_key = f"{request.user_id}:{request.module_id}"
            module_progress = self.module_progress.get(module_key)
            
            if not module_progress:
                module_progress = ModuleProgress(
                    module_id=request.module_id,
                    user_id=request.user_id
                )
            
            # Update module-specific properties
            if request.completed is not None:
                module_progress.completed = request.completed
            if request.time_spent_seconds is not None:
                if module_progress.time_spent_seconds is None:
                    module_progress.time_spent_seconds = 0
                module_progress.time_spent_seconds += request.time_spent_seconds
            if request.lesson_id and request.completed:
                if request.lesson_id not in module_progress.lessons_completed:
                    module_progress.lessons_completed.append(request.lesson_id)
            
            # Update module dates
            if module_progress.start_date is None:
                module_progress.start_date = datetime.now()
            if request.completed:
                module_progress.completion_date = datetime.now()
            
            # Store the updated module progress
            self.module_progress[module_key] = module_progress
        
        # Update user's overall progress
        user_key = f"{request.user_id}:{request.subject}"
        user_progress = self.user_progress.get(user_key)
        
        if not user_progress:
            user_progress = UserProgress(
                user_id=request.user_id,
                subject=request.subject
            )
        
        # Update user progress based on the changes
        user_progress.last_accessed = datetime.now()
        
        # Count completed lessons and modules
        user_lesson_progress = [
            lp for lp in self.lesson_progress.values() 
            if lp.user_id == request.user_id
        ]
        
        user_progress.total_lessons_completed = len([
            lp for lp in user_lesson_progress 
            if lp.completed
        ])
        
        user_progress.total_modules_completed = len([
            mp for mp in self.module_progress.values() 
            if mp.user_id == request.user_id and mp.completed
        ])
        
        # Calculate overall score
        completed_lessons = [
            lp for lp in user_lesson_progress 
            if lp.completed and lp.score is not None
        ]
        
        if completed_lessons:
            user_progress.overall_score = sum(lp.score for lp in completed_lessons) / len(completed_lessons)
        else:
            user_progress.overall_score = None
        
        # Update time spent
        if request.time_spent_seconds:
            user_progress.time_spent_total_seconds += request.time_spent_seconds
        
        # Update current lesson/module
        if request.lesson_id:
            user_progress.current_lesson_id = request.lesson_id
        if request.module_id:
            user_progress.current_module_id = request.module_id
        
        # Identify strengths and weaknesses based on performance
        if completed_lessons:
            # Calculate average score per concept/topic
            concept_scores = {}
            for lesson in completed_lessons:
                # Extract concept/topic from lesson_id or use a mapping
                concept = lesson.lesson_id.split('_')[1] if '_' in lesson.lesson_id else lesson.lesson_id
                if concept not in concept_scores:
                    concept_scores[concept] = []
                concept_scores[concept].append(lesson.score)
            
            # Determine strengths and weaknesses
            user_progress.strengths = []
            user_progress.weaknesses = []
            
            for concept, scores in concept_scores.items():
                avg_score = sum(scores) / len(scores)
                if avg_score >= 80:
                    if concept not in user_progress.strengths:
                        user_progress.strengths.append(concept)
                elif avg_score < 65:  # Adjust threshold as needed
                    if concept not in user_progress.weaknesses:
                        user_progress.weaknesses.append(concept)
        
        # Calculate completion percentage based on completed lessons
        # This would be enhanced in a real system with curriculum-specific data
        total_possible_lessons = 10  # This should come from curriculum data
        if total_possible_lessons > 0:
            user_progress.completion_percentage = min(
                (user_progress.total_lessons_completed / total_possible_lessons) * 100, 
                100
            )
        else:
            user_progress.completion_percentage = 0.0
        
        # Store the updated user progress
        self.user_progress[user_key] = user_progress
        
        # Invalidate analytics cache
        analytics_key = f"{request.user_id}:{request.subject}"
        if analytics_key in self.analytics_cache:
            del self.analytics_cache[analytics_key]
        
        # Generate and store user knowledge embedding in vector database
        try:
            # Create a textual representation of the user's progress for embedding
            progress_text = (f"User {user_progress.user_id} progress in {user_progress.subject}. "
                           f"Completed {user_progress.total_lessons_completed} lessons, "
                           f"with overall score of {user_progress.overall_score}. "
                           f"Strengths: {', '.join(user_progress.strengths)}. "
                           f"Weaknesses: {', '.join(user_progress.weaknesses)}. "
                           f"Learning pace: {user_progress.learning_pace}.")
            
            # Generate embedding for the user's knowledge state
            knowledge_embedding = embedding_service.generate_embedding(progress_text)
            
            # Store in vector database
            success = vector_db_service.upsert_user_knowledge_state(
                user_id=user_progress.user_id,
                knowledge_embedding=knowledge_embedding,
                subject=user_progress.subject
            )
            
            if success:
                logger.info(f"Stored knowledge embedding for user {user_progress.user_id} in subject {user_progress.subject}")
            else:
                logger.error(f"Failed to store knowledge embedding for user {user_progress.user_id}")
                
        except Exception as e:
            logger.error(f"Error storing user knowledge embedding for user {user_progress.user_id}: {e}")
        
        return user_progress
    
    def get_user_progress(self, user_id: str, subject: str) -> Optional[UserProgress]:
        """
        Get a user's progress for a specific subject.
        
        Args:
            user_id: The ID of the user.
            subject: The subject to retrieve progress for.
            
        Returns:
            UserProgress object if found, None otherwise.
        """
        user_key = f"{user_id}:{subject}"
        return self.user_progress.get(user_key)
    
    def get_progress_analytics(self, user_id: str, subject: str) -> Optional[ProgressAnalytics]:
        """
        Get detailed analytics for a user's progress in a specific subject.
        
        Args:
            user_id: The ID of the user.
            subject: The subject to retrieve analytics for.
            
        Returns:
            ProgressAnalytics object if found, None otherwise.
        """
        # Check cache first
        cache_key = f"{user_id}:{subject}"
        if cache_key in self.analytics_cache:
            return self.analytics_cache[cache_key]
        
        # Get user progress
        user_progress = self.get_user_progress(user_id, subject)
        if not user_progress:
            return None
        
        # Get all lessons for this user
        user_lessons = [
            lp for lp in self.lesson_progress.values()
            if lp.user_id == user_id
        ]
        
        # Get all scores for accuracy trend
        scores = [(lp.last_interaction, lp.score) for lp in user_lessons if lp.score is not None and lp.last_interaction]
        scores.sort(key=lambda x: x[0])
        
        # Get time spent for trend
        time_spent = [(lp.last_interaction, lp.time_spent_seconds) for lp in user_lessons if lp.time_spent_seconds and lp.last_interaction]
        time_spent.sort(key=lambda x: x[0])
        
        # Determine weak and strong areas based on scores
        weak_areas = set()
        strong_areas = set()
        
        # For this example, we'll identify lessons by their IDs and scores
        for lesson in user_lessons:
            if lesson.score is not None:
                if lesson.score < 70:  # Below 70% considered weak
                    weak_areas.add(lesson.lesson_id)
                elif lesson.score > 85:  # Above 85% considered strong
                    strong_areas.add(lesson.lesson_id)
        
        # Calculate learning velocity (lessons per day)
        if user_lessons and user_progress.last_accessed and user_progress.overall_score:
            first_interaction = min((lp.last_interaction for lp in user_lessons if lp.last_interaction), default=None)
            if first_interaction and user_progress.last_accessed > first_interaction:
                days_active = (user_progress.last_accessed - first_interaction).days
                if days_active > 0:
                    learning_velocity = len(user_lessons) / days_active
                else:
                    learning_velocity = len(user_lessons)  # At least 1 if same day
            else:
                learning_velocity = 1.0  # Default value
        else:
            learning_velocity = 1.0  # Default value
        
        # Estimate completion days (simplified)
        remaining_lessons = 10 - user_progress.total_lessons_completed  # Assuming 10 lessons total
        if learning_velocity > 0:
            estimated_completion_days = int(remaining_lessons / learning_velocity)
        else:
            estimated_completion_days = 30  # Default estimate
        
        # Create analytics object
        analytics = ProgressAnalytics(
            user_id=user_id,
            subject=subject,
            learning_velocity=learning_velocity,
            accuracy_trend=[{"date": str(date), "score": score} for date, score in scores],
            time_spent_trend=[{"date": str(date), "seconds": seconds} for date, seconds in time_spent],
            weak_areas=list(weak_areas),
            strong_areas=list(strong_areas),
            estimated_completion_days=estimated_completion_days
        )
        
        # Cache the analytics
        self.analytics_cache[cache_key] = analytics
        
        return analytics
    
    def get_advanced_analytics(self, user_id: str, subject: str) -> Optional[Dict[str, Any]]:
        """
        Get advanced analytics for a user's progress using LLM analysis.
        
        Args:
            user_id: The ID of the user.
            subject: The subject to retrieve advanced analytics for.
            
        Returns:
            Dictionary with advanced analytics from LLM.
        """
        # Get the basic analytics
        basic_analytics = self.get_progress_analytics(user_id, subject)
        if not basic_analytics:
            return None
        
        # Get the user progress data
        user_progress = self.get_user_progress(user_id, subject)
        if not user_progress:
            return None
        
        # Combine data for LLM analysis
        progress_data = {
            "user_id": user_id,
            "subject": subject,
            "basic_analytics": basic_analytics.__dict__ if hasattr(basic_analytics, '__dict__') else basic_analytics,
            "user_progress": user_progress.__dict__ if hasattr(user_progress, '__dict__') else user_progress
        }
        
        # Get LLM-based analysis
        analysis = progress_analytics_llm.analyze_learning_patterns(
            user_id=user_id,
            subject=subject,
            progress_data=progress_data
        )
        
        return analysis
    
    def get_personalized_insights(self, user_id: str, subject: str) -> Optional[Dict[str, Any]]:
        """
        Get personalized insights for a user based on their progress.
        
        Args:
            user_id: The ID of the user.
            subject: The subject to retrieve insights for.
            
        Returns:
            Dictionary with personalized insights from LLM.
        """
        # Get the user progress data
        user_progress = self.get_user_progress(user_id, subject)
        if not user_progress:
            return None
        
        # Prepare progress data for LLM
        progress_data = {
            "user_id": user_id,
            "subject": subject,
            "user_progress": user_progress.__dict__ if hasattr(user_progress, '__dict__') else user_progress
        }
        
        # Get LLM-based insights
        insights = progress_analytics_llm.get_personalized_insights(
            user_id=user_id,
            subject=subject,
            progress_data=progress_data
        )
        
        return insights
    
    def reset_user_progress(self, user_id: str, subject: str) -> bool:
        """
        Reset a user's progress for a specific subject.
        
        Args:
            user_id: The ID of the user.
            subject: The subject to reset progress for.
            
        Returns:
            True if reset was successful, False otherwise.
        """
        user_key = f"{user_id}:{subject}"
        
        if user_key not in self.user_progress:
            return False
        
        # Remove user progress
        del self.user_progress[user_key]
        
        # Remove related lesson progress
        lessons_to_remove = [
            key for key in self.lesson_progress.keys() 
            if key.startswith(f"{user_id}:")
        ]
        for key in lessons_to_remove:
            del self.lesson_progress[key]
        
        # Remove related module progress
        modules_to_remove = [
            key for key in self.module_progress.keys() 
            if key.startswith(f"{user_id}:")
        ]
        for key in modules_to_remove:
            del self.module_progress[key]
        
        # Remove from analytics cache
        analytics_key = f"{user_id}:{subject}"
        if analytics_key in self.analytics_cache:
            del self.analytics_cache[analytics_key]
        
        return True


# Global instance of the progress service
progress_service = ProgressService()