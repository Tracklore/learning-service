# app/models/curriculum_model.py
from pydantic import BaseModel
from typing import List, Optional

class Module(BaseModel):
    module_id: str
    title: str
    type: str  # e.g., "lesson", "quiz", "project"
    difficulty: str  # "easy", "medium", "hard"
    estimated_time_min: Optional[int] = None
    resources: Optional[List[str]] = None
    description: Optional[str] = None
    embedding_vector: Optional[List[float]] = None  # For semantic search

class Curriculum(BaseModel):
    curriculum_id: str
    subject_id: str
    path: str  # e.g., "newbie", "pro"
    modules: List[Module]  # Fully detailed modules
    recommended_tutor_style: Optional[str] = None  # e.g., "friendly"
    learning_objectives: Optional[List[str]] = None

class LearningPath(BaseModel):
    user_id: str
    curriculum_id: str
    completed_modules: List[str] = []
    progress: float = 0.0  # 0-100%
    completion_status: str = "incomplete"

class CurriculumRequest(BaseModel):
    subject: str
    skill_level: str  # e.g., "beginner", "intermediate", "advanced"
    path: str  # e.g., "newbie", "amateur", "pro"