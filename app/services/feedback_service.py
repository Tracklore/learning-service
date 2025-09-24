"""
Feedback service for collecting, processing, and managing user feedback.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
from app.models.feedback_model import (
    FeedbackSubmission, 
    FeedbackResponse, 
    FeedbackAnalytics, 
    CurriculumFeedback,
    InteractionLog
)
from app.services.curriculum_service import generate_curriculum
from app.services.adaptive_learning_paths_service import adaptive_learning_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

from collections import deque

class FeedbackService:
    """Service for managing user feedback collection and processing."""
    
    def __init__(self):
        """Initialize the Feedback Service with in-memory storage."""
        self.feedback_submissions: Dict[str, FeedbackSubmission] = {}
        self.curriculum_feedback: Dict[str, CurriculumFeedback] = {}
        self.interaction_logs: Dict[str, InteractionLog] = {}
        self.feedback_analytics: Dict[str, FeedbackAnalytics] = {}  # Key: subject
        
        # For optimization: cache for user sentiment trends
        self.sentiment_cache: Dict[str, Dict[str, Any]] = {}
        self.analytics_cache_ttl = 300  # 5 minutes TTL for analytics cache
        self.last_analytics_update: Dict[str, datetime] = {}
        
        # Batch processing queue for performance
        self.feedback_queue = deque()
        self.batch_processing_enabled = True
    
    def submit_feedback(self, feedback: FeedbackSubmission) -> FeedbackResponse:\n        \"\"\"\n        Submit feedback from a user.\n        \n        Args:\n            feedback: Feedback submission with user feedback details.\n            \n        Returns:\n            FeedbackResponse confirming submission.\n        \"\"\"\n        feedback_id = str(uuid.uuid4())\n        \n        # Store the feedback submission\n        self.feedback_submissions[feedback_id] = feedback\n        \n        # Update analytics\n        self._update_analytics(feedback)\n        \n        # Trigger curriculum adjustment based on feedback if applicable\n        self._process_feedback_for_curriculum_adjustment(feedback)\n        \n        response = FeedbackResponse(\n            feedback_id=feedback_id,\n            message=\"Feedback submitted successfully\",\n            user_id=feedback.user_id,\n            timestamp=datetime.now()\n        )\n        \n        logger.info(f\"Feedback submitted for user {feedback.user_id}, type: {feedback.feedback_type}\")\n        return response\n    \n    def _process_feedback_for_curriculum_adjustment(self, feedback: FeedbackSubmission):\n        \"\"\"\n        Process feedback to trigger curriculum adjustments.\n        \n        Args:\n            feedback: The feedback submission to process\n        \"\"\"\n        # If feedback indicates difficulty issues, adjust the learning path\n        if (feedback.difficulty_rating is not None and feedback.difficulty_rating < 3) or \\\n           (feedback.rating is not None and feedback.rating < 3):\n            # Student finds content too difficult or overall experience poor\n            logger.info(f\"Processing curriculum adjustment for user {feedback.user_id} due to low ratings\")\n            \n            # Trigger adaptive learning path adjustment\n            try:\n                # This would trigger regeneration of the curriculum with adjusted difficulty\n                # In a real implementation, this might queue a task or trigger a change in the user's path\n                logger.info(f\"Curriculum adjustment triggered for user {feedback.user_id}\")\n            except Exception as e:\n                logger.error(f\"Error processing curriculum adjustment for user {feedback.user_id}: {e}\")\n        \n        # If feedback includes specific suggestions, consider them for content improvement\n        if feedback.suggestions:\n            logger.info(f\"Processing suggestions for user {feedback.user_id}: {feedback.suggestions}\")\n            # In a real implementation, these suggestions could be stored and used to improve content\n    \n    def adjust_curriculum_based_on_feedback(self, user_id: str, subject: str) -> bool:\n        \"\"\"\n        Adjust curriculum based on user feedback.\n        \n        Args:\n            user_id: The ID of the user\n            subject: The subject to adjust curriculum for\n            \n        Returns:\n            True if adjustment was successful\n        \"\"\"\n        # Get all feedback for this user and subject\n        user_feedback = [\n            fb for fb in self.feedback_submissions.values()\n            if fb.user_id == user_id and fb.subject == subject\n        ]\n        \n        if not user_feedback:\n            logger.warning(f\"No feedback found for user {user_id} in subject {subject}\")\n            return False\n        \n        # Analyze feedback to determine adjustment\n        avg_rating = 0\n        low_ratings = 0\n        high_ratings = 0\n        total_feedback = len(user_feedback)\n        \n        for fb in user_feedback:\n            rating = fb.rating or fb.content_rating or fb.difficulty_rating or fb.tutor_rating\n            if rating:\n                avg_rating += rating\n                if rating <= 2:\n                    low_ratings += 1\n                elif rating >= 4:\n                    high_ratings += 1\n        \n        if total_feedback > 0:\n            avg_rating /= total_feedback\n        else:\n            return False\n        \n        # If average rating is low, consider slowing down the pace or adding remedial content\n        if avg_rating < 3.0:\n            logger.info(f\"Adjusting curriculum for user {user_id} due to low average rating ({avg_rating})\")\n            # In a real system, this would adjust the user's curriculum path\n            # This could involve switching to a slower path, adding more practice, etc.\n            return True\n        elif avg_rating > 4.0:\n            logger.info(f\"User {user_id} performing well, possibly accelerating path\")\n            # In a real system, this could trigger acceleration\n            return True\n        else:\n            logger.info(f\"Curriculum for user {user_id} is appropriate, no adjustment needed\")\n            return True
    
    def submit_curriculum_feedback(self, curriculum_feedback: CurriculumFeedback) -> FeedbackResponse:
        """
        Submit feedback about a curriculum.
        
        Args:
            curriculum_feedback: Feedback about curriculum effectiveness.
            
        Returns:
            FeedbackResponse confirming submission.
        """
        feedback_id = str(uuid.uuid4())
        
        # Store the curriculum feedback
        self.curriculum_feedback[feedback_id] = curriculum_feedback
        
        response = FeedbackResponse(
            feedback_id=feedback_id,
            message="Curriculum feedback submitted successfully",
            user_id=curriculum_feedback.user_id,
            timestamp=datetime.now()
        )
        
        logger.info(f"Curriculum feedback submitted for user {curriculum_feedback.user_id}, curriculum {curriculum_feedback.curriculum_id}")
        return response
    
    def get_feedback_analytics(self, subject: str) -> Optional[FeedbackAnalytics]:
        """
        Get aggregated feedback analytics for a subject.
        
        Args:
            subject: The subject to get analytics for.
            
        Returns:
            FeedbackAnalytics object if found, None otherwise.
        """
        return self.feedback_analytics.get(subject)
    
    def _update_analytics(self, feedback: FeedbackSubmission):
        """
        Update feedback analytics based on new feedback.
        
        Args:
            feedback: New feedback submission.
        """
        subject = feedback.subject
        
        # Get existing analytics or create new one
        if subject not in self.feedback_analytics:
            self.feedback_analytics[subject] = FeedbackAnalytics(
                subject=subject,
                average_rating=0.0,
                total_feedback=0,
                positive_feedback=0,
                negative_feedback=0,
                common_suggestions=[],
                rating_distribution={1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                top_feedback_topics=[],
                timestamp=datetime.now()
            )
        
        analytics = self.feedback_analytics[subject]
        
        # Update counts
        analytics.total_feedback += 1
        
        # Update ratings and classifications
        rating = feedback.rating or feedback.content_rating or feedback.difficulty_rating or feedback.tutor_rating
        if rating:
            analytics.rating_distribution[rating] += 1
            
            # Update average
            total_rating = sum(rating * count for rating, count in analytics.rating_distribution.items())
            analytics.average_rating = total_rating / analytics.total_feedback
            
            # Classify as positive/negative
            if rating >= 4:
                analytics.positive_feedback += 1
            elif rating <= 2:
                analytics.negative_feedback += 1
        
        # Update common suggestions
        if feedback.suggestions:
            for suggestion in feedback.suggestions:
                if suggestion not in analytics.common_suggestions:
                    analytics.common_suggestions.append(suggestion)
        
        # Update feedback topics based on feedback type
        if feedback.feedback_type not in analytics.top_feedback_topics:
            analytics.top_feedback_topics.append(feedback.feedback_type)
        
        # Update emotional states analysis if provided
        if feedback.emotional_state:
            # In a real implementation, we might track emotional trends
            pass
                
        # Update timestamp
        analytics.timestamp = datetime.now()
    
    def get_user_sentiment_trend(self, user_id: str) -> Dict[str, Any]:
        """
        Get the sentiment trend for a user based on their feedback.
        Uses caching for optimization.
        
        Args:
            user_id: The ID of the user.
            
        Returns:
            Dictionary with sentiment analysis.
        """
        # Check cache first
        if user_id in self.sentiment_cache:
            cached_data = self.sentiment_cache[user_id]
            # Check if cache is still valid (less than 10 minutes old)
            cache_time = cached_data.get("cached_at", datetime.min)
            if (datetime.now() - cache_time).seconds < 600:  # 10 minutes
                logger.debug(f"Returning cached sentiment for user {user_id}")
                return cached_data["data"]
        
        user_feedback = self.get_user_feedback_history(user_id)
        
        if not user_feedback:
            result = {
                "user_id": user_id,
                "sentiment_trend": [],
                "overall_sentiment": "neutral",
                "emotional_states": {}
            }
            # Cache the result
            self.sentiment_cache[user_id] = {
                "data": result,
                "cached_at": datetime.now()
            }
            return result
        
        # Analyze sentiment trend
        sentiment_trend = []
        emotional_states_count = {}
        
        for feedback in user_feedback:
            rating = feedback.rating or feedback.content_rating or feedback.difficulty_rating or feedback.tutor_rating
            if rating:
                sentiment_trend.append({
                    "timestamp": feedback.timestamp,
                    "rating": rating,
                    "sentiment": "positive" if rating >= 4 else ("negative" if rating <= 2 else "neutral")
                })
            
            if feedback.emotional_state:
                emotional_states_count[feedback.emotional_state] = emotional_states_count.get(feedback.emotional_state, 0) + 1
        
        # Determine overall sentiment
        if sentiment_trend:
            recent_sentiments = [item["sentiment"] for item in sentiment_trend[-5:]]  # Last 5 feedbacks
            pos_count = recent_sentiments.count("positive")
            neg_count = recent_sentiments.count("negative")
            
            if pos_count > neg_count:
                overall_sentiment = "positive"
            elif neg_count > pos_count:
                overall_sentiment = "negative"
            else:
                overall_sentiment = "neutral"
        else:
            overall_sentiment = "neutral"
        
        result = {
            "user_id": user_id,
            "sentiment_trend": sentiment_trend,
            "overall_sentiment": overall_sentiment,
            "emotional_states": emotional_states_count
        }
        
        # Cache the result
        self.sentiment_cache[user_id] = {
            "data": result,
            "cached_at": datetime.now()
        }
        
        return result
    
    def submit_feedback_batch(self, feedback_list: List[FeedbackSubmission]) -> List[FeedbackResponse]:
        """
        Submit multiple feedback entries in a batch for better performance.
        
        Args:
            feedback_list: List of feedback submissions.
            
        Returns:
            List of feedback responses.
        """
        responses = []
        
        for feedback in feedback_list:
            # Set timestamp if not provided
            if not feedback.timestamp:
                feedback.timestamp = datetime.now()
            
            feedback_id = str(uuid.uuid4())
            self.feedback_submissions[feedback_id] = feedback
            
            # Process feedback for curriculum adjustment if needed
            self._process_feedback_for_curriculum_adjustment(feedback)
            
            response = FeedbackResponse(
                feedback_id=feedback_id,
                message="Feedback submitted successfully",
                user_id=feedback.user_id,
                timestamp=feedback.timestamp
            )
            responses.append(response)
        
        # Update analytics for the subject once after all feedback is submitted
        if feedback_list:
            subject = feedback_list[0].subject
            self._update_analytics_cache_invalidate(subject)
        
        logger.info(f"Batch submitted {len(feedback_list)} feedback entries")
        return responses
    
    def _update_analytics_cache_invalidate(self, subject: str):
        """
        Invalidate analytics cache for a subject when new feedback is added.
        
        Args:
            subject: The subject to invalidate cache for.
        """
        if subject in self.last_analytics_update:
            del self.last_analytics_update[subject]
    
    def get_user_feedback_history(self, user_id: str) -> List[FeedbackSubmission]:
        """
        Get feedback history for a specific user.
        
        Args:
            user_id: The ID of the user.
            
        Returns:
            List of feedback submissions by the user.
        """
        return [
            feedback for feedback in self.feedback_submissions.values()
            if feedback.user_id == user_id
        ]
    
    def get_tutor_feedback(self, tutor_id: str) -> List[FeedbackSubmission]:
        """
        Get feedback specifically for a tutor.
        
        Args:
            tutor_id: The ID of the tutor.
            
        Returns:
            List of feedback submissions for the tutor.
        """
        return [
            feedback for feedback in self.feedback_submissions.values()
            if feedback.tutor_id == tutor_id
        ]
    
    def get_curriculum_feedback(self, curriculum_id: str) -> List[CurriculumFeedback]:
        """
        Get feedback for a specific curriculum.
        
        Args:
            curriculum_id: The ID of the curriculum.
            
        Returns:
            List of feedback submissions for the curriculum.
        """
        return [
            feedback for feedback in self.curriculum_feedback.values()
            if feedback.curriculum_id == curriculum_id
        ]


# Global instance of the feedback service
feedback_service = FeedbackService()