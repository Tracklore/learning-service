from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class InteractionLog(BaseModel):
    user_id: str
    lesson_id: str
    feedback: Optional[str] = None
    rating: Optional[int] = None  # 1-5 scale
    timestamp: datetime
