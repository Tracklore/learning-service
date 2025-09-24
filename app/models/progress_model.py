from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class LessonProgress(BaseModel):
    """Model for tracking progress on a specific lesson."""
    lesson_id: str
    user_id: str
    completed: bool = False
    score: Optional[float] = None
    time_spent_seconds: Optional[int] = None
    attempts: int = 0
    last_interaction: Optional[datetime] = None
    repeated_mistakes: List[str] = []
    notes: Optional[str] = None


class ModuleProgress(BaseModel):
    """Model for tracking progress on a module."""
    module_id: str
    user_id: str
    completed: bool = False
    lessons_completed: List[str] = []
    lessons_total: int = 0
    score_average: Optional[float] = None
    time_spent_seconds: Optional[int] = None
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None


class KnowledgeEmbedding(BaseModel):
    """Model for knowledge state embeddings."""
    embedding_vector: List[float]  # Vector representation of knowledge
    embedding_version: str = "1.0"
    generated_at: datetime
    topics_covered: List[str]
    topics_mastery: Dict[str, float]  # Topic to mastery level (0-1)


class UserProgress(BaseModel):
    """Model aggregating user's overall progress."""
    user_id: str
    subject: str
    total_lessons_completed: int = 0
    total_modules_completed: int = 0
    overall_score: Optional[float] = None
    time_spent_total_seconds: int = 0
    current_module_id: Optional[str] = None
    current_lesson_id: Optional[str] = None
    last_accessed: Optional[datetime] = None
    completion_percentage: float = 0.0
    knowledge_state: Optional[KnowledgeEmbedding] = None  # For embedding user's knowledge state
    strengths: List[str] = []  # Topics the user excels in
    weaknesses: List[str] = []  # Topics the user struggles with
    learning_pace: str = "normal"  # "slow", "normal", "fast"


class ProgressUpdateRequest(BaseModel):
    """Request model for updating user progress."""
    user_id: str
    lesson_id: Optional[str] = None
    module_id: Optional[str] = None
    subject: str
    completed: Optional[bool] = None
    score: Optional[float] = None
    time_spent_seconds: Optional[int] = None
    repeated_mistakes: Optional[List[str]] = None
    notes: Optional[str] = None


class ProgressResponse(BaseModel):
    """Response model for progress data."""
    user_id: str
    subject: str
    current_lesson_id: Optional[str] = None
    current_module_id: Optional[str] = None
    total_lessons_completed: int
    total_modules_completed: int
    overall_score: Optional[float]
    completion_percentage: float
    message: str
    last_updated: datetime


class ProgressAnalytics(BaseModel):
    """Model for progress analytics."""
    user_id: str
    subject: str
    learning_velocity: float  # Lessons per day
    accuracy_trend: List[Dict[str, Any]]  # Accuracy over time
    time_spent_trend: List[Dict[str, Any]]  # Time spent over time
    weak_areas: List[str]  # Topics with lower performance
    strong_areas: List[str]  # Topics with higher performance
    estimated_completion_days: Optional[int]