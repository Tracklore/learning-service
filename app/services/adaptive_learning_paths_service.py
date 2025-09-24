"""
Adaptive learning paths service for creating personalized learning experiences based on user progress.
"""

from typing import List, Dict, Optional
from app.models.curriculum_model import Curriculum, Module
from app.models.progress_model import UserProgress, ProgressAnalytics
from app.services.curriculum_service import generate_curriculum, find_relevant_content_via_semantic_search, recommend_content_for_user_weaknesses
from app.services.progress_service import progress_service
from app.services.vector_db_service import vector_db_service
from app.llm.embeddings import embedding_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

class AdaptiveLearningService:
    """Service for creating adaptive learning paths based on user progress."""
    
    def __init__(self):
        """Initialize the Adaptive Learning Service."""
        self.user_learning_paths = {}
    
    def generate_adaptive_curriculum(
        self, 
        user_id: str, 
        subject: str, 
        current_path: str = "newbie"
    ) -> Curriculum:
        """
        Generate a personalized curriculum based on user progress and performance.
        
        Args:
            user_id: The ID of the user
            subject: The subject for the curriculum
            current_path: The current skill level path (newbie, amateur, pro)
            
        Returns:
            Personalized Curriculum object
        """
        # Get user progress
        user_progress = progress_service.get_user_progress(user_id, subject)
        if not user_progress:
            # If no progress exists, create a basic curriculum
            logger.info(f"No progress found for user {user_id}, generating basic curriculum for {subject}")
            return generate_curriculum(subject, current_path)
        
        # Get progress analytics
        analytics = progress_service.get_progress_analytics(user_id, subject)
        
        # Determine next appropriate path based on performance
        adjusted_path = self._determine_appropriate_path(user_progress, analytics, current_path)
        
        # Generate curriculum with adjusted path
        curriculum = generate_curriculum(subject, adjusted_path, user_id)
        
        # Adjust module sequence based on user's weak areas
        curriculum.modules = self._adjust_module_sequence(
            curriculum.modules, 
            user_progress.weaknesses, 
            user_progress.strengths
        )
        
        # Add remedial modules if needed
        if user_progress.weaknesses:
            curriculum.modules = self._add_remedial_modules(
                curriculum.modules, 
                user_progress.weaknesses,
                subject
            )
        
        # Add acceleration modules if user is excelling
        if (user_progress.overall_score and user_progress.overall_score > 85) or user_progress.learning_pace == "fast":
            curriculum.modules = self._add_acceleration_modules(
                curriculum.modules,
                subject
            )
        
        # Use semantic search to find additional relevant content based on user's progress
        try:
            # Find content that addresses weaknesses
            if user_progress.weaknesses:
                for weakness in user_progress.weaknesses[:2]:  # Limit to first 2 weaknesses
                    relevant_modules = find_relevant_content_via_semantic_search(
                        query=f"content to improve understanding of {weakness}",
                        subject=subject,
                        top_k=2
                    )
                    # Add relevant modules to the curriculum
                    for module in relevant_modules:
                        if module not in curriculum.modules:
                            curriculum.modules.append(module)
            
            # Find additional content for strengths to build on them
            if user_progress.strengths:
                for strength in user_progress.strengths[:2]:  # Limit to first 2 strengths
                    relevant_modules = find_relevant_content_via_semantic_search(
                        query=f"advanced content about {strength}",
                        subject=subject,
                        top_k=1
                    )
                    # Add relevant modules to the curriculum
                    for module in relevant_modules:
                        if module not in curriculum.modules:
                            curriculum.modules.append(module)
        except Exception as e:
            logger.error(f"Error finding additional content for user {user_id}: {e}")
        
        return curriculum
    
    def _determine_appropriate_path(
        self, 
        user_progress: UserProgress, 
        analytics: Optional[ProgressAnalytics], 
        current_path: str
    ) -> str:
        """
        Determine the appropriate learning path based on user performance.
        
        Args:
            user_progress: User's progress information
            analytics: Progress analytics
            current_path: Current path (newbie, amateur, pro)
            
        Returns:
            Appropriate path level
        """
        # Default to current path
        adjusted_path = current_path
        
        # If we have analytics, use them to determine appropriate path
        if analytics:
            if analytics.learning_velocity > 2.0 and user_progress.overall_score and user_progress.overall_score > 80:
                # User is learning quickly and scoring well, accelerate
                if current_path == "newbie":
                    adjusted_path = "amateur"
                elif current_path == "amateur":
                    adjusted_path = "pro"
            elif user_progress.overall_score and user_progress.overall_score < 60:
                # User is struggling, slow down
                if current_path == "pro":
                    adjusted_path = "amateur"
                elif current_path == "amateur":
                    adjusted_path = "newbie"
        
        return adjusted_path
    
    def _adjust_module_sequence(
        self, 
        modules: List[Module], 
        weaknesses: List[str], 
        strengths: List[str]
    ) -> List[Module]:
        """
        Adjust the sequence of modules based on user's strengths and weaknesses.
        
        Args:
            modules: List of modules to adjust
            weaknesses: List of topics the user struggles with
            strengths: List of topics the user excels at
            
        Returns:
            Adjusted list of modules
        """
        # Create lists for different types of modules
        weakness_modules = []
        strength_modules = []
        other_modules = []
        
        for module in modules:
            is_weakness = any(w.lower() in module.title.lower() for w in weaknesses)
            is_strength = any(s.lower() in module.title.lower() for s in strengths)
            
            if is_weakness:
                weakness_modules.append(module)
            elif is_strength:
                strength_modules.append(module)
            else:
                other_modules.append(module)
        
        # Prioritize modules on weak areas
        return weakness_modules + other_modules + strength_modules
    
    def _add_remedial_modules(
        self, 
        modules: List[Module], 
        weaknesses: List[str],
        subject: str
    ) -> List[Module]:
        """
        Add remedial modules for areas where the user is struggling.
        
        Args:
            modules: List of existing modules
            weaknesses: List of weak areas
            subject: The subject
            
        Returns:
            Updated list of modules with remedial content
        """
        if not weaknesses:
            return modules
        
        remedial_modules = []
        for weakness in weaknesses:
            remedial_module = Module(
                module_id=f"remedial_{subject}_{weakness.replace(' ', '_').lower()}",
                title=f"Remedial: {weakness}",
                type="lesson",
                difficulty="easy",
                estimated_time_min=30,
                resources=[f"resource_for_{weakness.lower().replace(' ', '_')}"]
            )
            remedial_modules.append(remedial_module)
        
        # Add remedial modules at the beginning of the curriculum
        return remedial_modules + modules
    
    def _add_acceleration_modules(
        self, 
        modules: List[Module],
        subject: str
    ) -> List[Module]:
        """
        Add acceleration modules for high-performing users.
        
        Args:
            modules: List of existing modules
            subject: The subject
            
        Returns:
            Updated list of modules with additional content
        """
        # Add challenge modules at the end
        challenge_module = Module(
            module_id=f"challenge_{subject}_advanced",
            title="Challenge Problems",
            type="project",
            difficulty="hard",
            estimated_time_min=60,
            resources=[f"advanced_{subject}_resources"]
        )
        
        return modules + [challenge_module]


# Global instance of the adaptive learning service
adaptive_learning_service = AdaptiveLearningService()