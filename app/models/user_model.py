  
from pydantic import BaseModel, Field
from typing import Optional, Dict

class User(BaseModel):
    user_id: str
    name: str
    email: str
    language: str = "en"
    skill_level: str = Field(..., regex="^(newbie|amateur|novice|pro)$")
    preferences: Optional[Dict] = None
