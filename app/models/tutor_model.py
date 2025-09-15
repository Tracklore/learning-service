from pydantic import BaseModel, Field

class TutorProfile(BaseModel):
    tutor_id: str
    character: str  # e.g., "friendly", "serious"
    humour_level: int = Field(ge=0, le=10)
    language_complexity: str  # e.g., "simple", "technical"

