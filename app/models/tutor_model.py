# app/models/tutor_model.py
"""
Tutor models for the learning service.
"""

from pydantic import BaseModel
from typing import List, Optional

class TutorPersona(BaseModel):
    """Model representing a tutor persona."""
    tutor_id: str
    name: str
    character_style: str  # e.g., "friendly", "professional", "funny"
    humor_level: str  # e.g., "low", "medium", "high"
    tone: str  # e.g., "encouraging", "direct", "casual"
    complexity: str  # e.g., "simple", "moderate", "complex"
    description: Optional[str] = None
    avatar_url: Optional[str] = None

class TutorSelectionRequest(BaseModel):
    """Model for tutor selection request."""
    user_id: str
    character_style: Optional[str] = None
    humor_level: Optional[str] = None
    tone: Optional[str] = None
    complexity: Optional[str] = None

class TutorResponse(BaseModel):
    """Model for tutor response."""
    tutor: TutorPersona
    message: str

class UserTutorPreference(BaseModel):
    """Model for storing user's tutor preferences."""
    user_id: str
    tutor_id: str
    selected_at: str  # ISO format timestamp