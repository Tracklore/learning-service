from pydantic import BaseModel
from typing import Optional

class TopicRequest(BaseModel):
    topic: str
    language: Optional[str] = "en"

class TopicResponse(BaseModel):
    subject: str          # Normalized subject (Physics, Math, CS, etc.)
    topic: str            # User-provided topic
    description: str      # Short description for UI
