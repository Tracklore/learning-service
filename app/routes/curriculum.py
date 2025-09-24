# app/routes/curriculum.py
from fastapi import APIRouter, HTTPException
from app.models.curriculum_model import CurriculumRequest, Curriculum
from app.services.curriculum_service import generate_curriculum
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/curriculum", tags=["Curriculum"])

@router.post("/", response_model=Curriculum)
async def create_curriculum(request: CurriculumRequest):
    """
    Generate a personalized curriculum based on subject and skill level.
    """
    try:
        logger.info(f"Generating curriculum for subject: {request.subject}, path: {request.path}")
        
        # Generate the curriculum
        curriculum = generate_curriculum(request.subject, request.path)
        
        logger.info(f"Successfully generated curriculum: {curriculum.curriculum_id}")
        return curriculum
    except Exception as e:
        logger.error(f"Error generating curriculum: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate curriculum: {str(e)}")