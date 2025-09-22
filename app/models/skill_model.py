from pydantic import BaseModel
from typing import List, Optional
from app.models.curriculum_model import Module

# ---------- Request / Response Models ----------
class SkillLevelRequest(BaseModel):
    topic: str
    skill_level: str  # "newbie", "amateur", "novice", "pro"

class SkillLevelResponse(BaseModel):
    path: str
    curriculum_id: str
    modules: List[Module]
    recommended_tutor_style: Optional[str] = None
    learning_objectives: Optional[List[str]] = None