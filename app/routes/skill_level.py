# app/routes/skill_level.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.curriculum_service import recommend_curriculum_path, generate_curriculum
from app.utils.logger import get_logger
from app.models.skill_model import SkillLevelRequest, SkillLevelResponse

logger = get_logger(__name__)
router = APIRouter(prefix="/skill-level", tags=["Skill Level"])


# ---------- POST Route ----------
@router.post("/", response_model=SkillLevelResponse)
async def set_skill_level(request: SkillLevelRequest):
    """
    Accepts user topic and skill level, returns the recommended curriculum path and modules.
    """
    try:
        logger.info(f"Received skill-level request for topic: {request.topic}, skill_level: {request.skill_level}")

        # Map user skill to curriculum path
        path = recommend_curriculum_path(request.skill_level)

        # Generate curriculum based on topic and path
        curriculum = generate_curriculum(subject=request.topic, path=path)

        response = SkillLevelResponse(
            path=curriculum.path,
            curriculum_id=curriculum.curriculum_id,
            modules=curriculum.modules,
            recommended_tutor_style=curriculum.recommended_tutor_style,
            learning_objectives=curriculum.learning_objectives
        )

        return response

    except Exception as e:
        logger.error(f"Error generating curriculum: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate curriculum")
