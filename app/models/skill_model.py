# ---------- Request / Response Models ----------
class SkillLevelRequest(BaseModel):
    topic: str
    skill_level: str  # "newbie", "amateur", "novice", "pro"

class SkillLevelResponse(BaseModel):
    path: str
    curriculum_id: str
    modules: list[str]