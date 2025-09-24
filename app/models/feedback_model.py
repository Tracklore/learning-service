from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class InteractionLog(BaseModel):
    """Basic interaction log for tracking user interactions."""
    user_id: str
    lesson_id: str
    feedback: Optional[str] = None
    rating: Optional[int] = None  # 1-5 scale
    timestamp: datetime


class FeedbackSubmission(BaseModel):
    """Model for submitting feedback about lessons, tutors, or the learning experience."""
    user_id: str
    subject: str
    lesson_id: Optional[str] = None
    module_id: Optional[str] = None
    tutor_id: Optional[str] = None
    feedback_type: str  # "lesson", "tutor", "content", "difficulty", "overall"
    rating: Optional[int] = None  # 1-5 scale
    content_rating: Optional[int] = None  # 1-5 scale for content quality
    difficulty_rating: Optional[int] = None  # 1-5 scale for difficulty level
    tutor_rating: Optional[int] = None  # 1-5 scale for tutor effectiveness
    feedback_text: Optional[str] = None
    suggestions: Optional[List[str]] = None
    would_recommend: Optional[bool] = None
    emotional_state: Optional[str] = None  # "frustrated", "confused", "engaged", "bored", etc.
    context_tags: Optional[List[str]] = None  # Tags for context: "first_lesson", "review_session", etc.
    timestamp: datetime


class FeedbackResponse(BaseModel):
    """Model for feedback submission response."""
    feedback_id: str
    message: str
    user_id: str
    timestamp: datetime


class FeedbackAnalytics(BaseModel):
    """Model for aggregated feedback analytics."""
    subject: str
    average_rating: float
    total_feedback: int
    positive_feedback: int
    negative_feedback: int
    common_suggestions: List[str]
    rating_distribution: dict  # e.g., {1: 5, 2: 3, 3: 8, 4: 12, 5: 22}
    top_feedback_topics: List[str]
    timestamp: datetime


class CurriculumFeedback(BaseModel):
    """Model for feedback specific to curriculum."""
    user_id: str
    curriculum_id: str
    learning_path: str  # "fast-track", "deep-dive", etc.
    overall_satisfaction: Optional[int]  # 1-5 scale
    pacing_feedback: Optional[int]  # 1-5 scale
    content_relevance: Optional[int]  # 1-5 scale
    effectiveness: Optional[int]  # 1-5 scale
    feedback_text: Optional[str] = None
    suggested_improvements: Optional[List[str]] = None
    completed_modules: int
    total_modules: int
    timestamp: datetime
