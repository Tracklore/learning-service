"""
Adaptive learning service for lesson path adaptation based on user performance.
"""

import logging
from typing import Dict, Any, List, Optional
from app.services.evaluation_service import evaluation_service
from app.services.teaching_service import teaching_service
from app.llm.teaching_llm import teaching_llm

# Configure logging
logger = logging.getLogger(__name__)

class AdaptiveLearningService:
    """Service for adaptive learning path based on user performance."""
    
    def __init__(self):
        """Initialize the Adaptive Learning Service."""
        self.learning_paths = {}  # Store adaptive learning paths for users
        self.concept_difficulty = {}  # Track difficulty of concepts for each user
    
    def adapt_lesson_path(
        self, 
        user_id: str, 
        subject: str, 
        topic: str, 
        current_step: int, 
        total_steps: int
    ) -> Dict[str, Any]:
        """
        Adapt the lesson path based on user's performance.
        
        Args:
            user_id: The ID of the user
            subject: The subject being taught
            topic: The topic within the subject
            current_step: Current step in the lesson
            total_steps: Total steps in the lesson
            
        Returns:
            Dictionary containing adaptation recommendations.
        """
        # Get user's performance summary
        performance_summary = evaluation_service.get_user_performance_summary(user_id)
        
        # Calculate topic-specific performance
        topic_performance = self._calculate_topic_performance(performance_summary, topic)
        
        # Determine if user needs remedial content or can accelerate
        if topic_performance < 0.6:  # Below 60% accuracy
            # User is struggling, recommend remedial content
            adaptation = self._remedial_content_adaptation(
                user_id, subject, topic, current_step, total_steps, performance_summary
            )
        elif topic_performance > 0.85:  # Above 85% accuracy
            # User is excelling, recommend acceleration
            adaptation = self._acceleration_adaptation(
                user_id, subject, topic, current_step, total_steps, performance_summary
            )
        else:
            # Performance is adequate, continue normal path
            adaptation = self._normal_path_adaptation(
                user_id, subject, topic, current_step, total_steps, performance_summary
            )
        
        # Store the adaptation for the user
        if user_id not in self.learning_paths:
            self.learning_paths[user_id] = []
        
        self.learning_paths[user_id].append(adaptation)
        
        return adaptation
    
    def _calculate_topic_performance(self, performance_summary: Dict[str, Any], topic: str) -> float:
        """Calculate the performance for a specific topic."""
        if topic in performance_summary["subject_performance"]:
            return performance_summary["subject_performance"][topic]["accuracy_percentage"] / 100
        else:
            # If topic-specific data is not available, use overall accuracy
            return performance_summary["accuracy_percentage"] / 100
    
    def _remedial_content_adaptation(
        self, 
        user_id: str, 
        subject: str, 
        topic: str, 
        current_step: int, 
        total_steps: int, 
        performance_summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate adaptation for users who need remedial content."""
        try:
            # Get remedial content from LLM
            remedial_content = teaching_llm.update_lesson_complexity(
                subject=subject,
                topic=topic,
                concept=topic,
                current_user_performance="poor",
                tutor_persona=performance_summary.get("tutor_persona", {})
            )
            
            return {
                "adaptation_type": "remedial",
                "message": "Based on your performance, we're providing additional foundational content to strengthen your understanding.",
                "recommended_action": "Review remedial content before proceeding",
                "remedial_content": remedial_content["content"],
                "recommendations": remedial_content["recommendation"],
                "continue_path": False,  # Don't continue with normal path
                "next_step": "remedial_content"
            }
        except Exception as e:
            logger.error(f"Error generating remedial adaptation for user {user_id}: {e}")
            return {
                "adaptation_type": "remedial",
                "message": "It seems you're struggling with this topic. Consider reviewing basic concepts before continuing.",
                "recommended_action": "Review basic materials",
                "remedial_content": "",
                "recommendations": ["Spend more time on practice questions", "Review foundational concepts"],
                "continue_path": False,
                "next_step": "remedial_content"
            }
    
    def _acceleration_adaptation(
        self, 
        user_id: str, 
        subject: str, 
        topic: str, 
        current_step: int, 
        total_steps: int, 
        performance_summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate adaptation for users who can accelerate."""
        try:
            # Get advanced content from LLM
            advanced_content = teaching_llm.update_lesson_complexity(
                subject=subject,
                topic=topic,
                concept=topic,
                current_user_performance="good",
                tutor_persona=performance_summary.get("tutor_persona", {})
            )
            
            # Calculate if user can skip steps
            steps_to_skip = min(2, total_steps - current_step)  # Skip up to 2 steps
            new_step = min(current_step + steps_to_skip, total_steps)
            
            return {
                "adaptation_type": "acceleration",
                "message": "Based on your excellent performance, we're accelerating your learning path.",
                "recommended_action": f"Skip to step {new_step} or continue with advanced content",
                "advanced_content": advanced_content["content"],
                "recommendations": advanced_content["recommendation"],
                "continue_path": True,
                "next_step": new_step,
                "steps_skipped": steps_to_skip
            }
        except Exception as e:
            logger.error(f"Error generating acceleration adaptation for user {user_id}: {e}")
            return {
                "adaptation_type": "acceleration",
                "message": "You're performing well! You may accelerate through this content.",
                "recommended_action": "Continue to next step",
                "advanced_content": "",
                "recommendations": ["You can move to more challenging material", "Consider exploring advanced topics"],
                "continue_path": True,
                "next_step": current_step + 1,
                "steps_skipped": 0
            }
    
    def _normal_path_adaptation(
        self, 
        user_id: str, 
        subject: str, 
        topic: str, 
        current_step: int, 
        total_steps: int, 
        performance_summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate adaptation for users following normal path."""
        return {
            "adaptation_type": "normal",
            "message": "Your performance is on track. Continue with the normal learning path.",
            "recommended_action": "Proceed to the next step",
            "advanced_content": "",
            "recommendations": ["Keep up the good work", "Continue with regular practice"],
            "continue_path": True,
            "next_step": current_step + 1,
            "steps_skipped": 0
        }
    
    def get_user_adaptation_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get the adaptation history for a user."""
        return self.learning_paths.get(user_id, [])
    
    def suggest_concept_practice(
        self, 
        user_id: str, 
        subject: str, 
        topic: str, 
        concept: str
    ) -> Dict[str, Any]:
        """
        Suggest additional practice for a specific concept based on user performance.
        
        Args:
            user_id: The ID of the user
            subject: The subject being taught
            topic: The topic within the subject
            concept: The specific concept needing practice
            
        Returns:
            Dictionary containing practice recommendations.
        """
        # Get user's performance on this concept
        performance_summary = evaluation_service.get_user_performance_summary(user_id)
        
        # Look for performance related to this specific concept
        concept_performance = self._find_concept_performance(performance_summary, concept)
        
        if concept_performance and concept_performance["accuracy"] < 0.6:
            # Performance is low, suggest more practice
            suggestion = {
                "concept": concept,
                "needs_practice": True,
                "recommended_sessions": 3,
                "message": f"You seem to be struggling with {concept}. Additional practice would be beneficial.",
                "practice_types": ["drill exercises", "interactive questions", "review materials"],
                "difficulty_level": "simplified"
            }
        else:
            # Performance is adequate
            suggestion = {
                "concept": concept,
                "needs_practice": False,
                "recommended_sessions": 1,
                "message": f"Your understanding of {concept} is adequate. Continue with the normal path.",
                "practice_types": ["review questions", "application exercises"],
                "difficulty_level": "moderate"
            }
        
        return suggestion
    
    def _find_concept_performance(self, performance_summary: Dict[str, Any], concept: str) -> Optional[Dict[str, Any]]:
        """Find performance data for a specific concept."""
        for entry in performance_summary.get("recent_performance", []):
            if entry.get("concept", "").lower() == concept.lower():
                return {
                    "accuracy": entry.get("score", 0) / 100 if entry.get("score") else 0,
                    "timestamp": entry.get("timestamp")
                }
        return None


# Global instance
adaptive_learning_service = AdaptiveLearningService()