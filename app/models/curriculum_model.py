from pydantic import BaseModel
from typing import List

class Curriculum(BaseModel):
    curriculum_id: str
    subject_id: str
    path: str  # e.g., "newbie", "pro"
    modules: List[str]  # List of lesson/module IDs

class LearningPath(BaseModel):
    user_id: str
    curriculum_id: str
    progress: float = 0.0  # 0-100%
    completion_status: str = "incomplete"

