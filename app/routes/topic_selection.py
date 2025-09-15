# app/routes/topic_selection.py
from fastapi import APIRouter, HTTPException
from app.models.topic_model import TopicRequest, TopicResponse
from app.services.subject_service import normalize_topic
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/topic", tags=["Topic Selection"])

@router.post("/", response_model=TopicResponse)
async def select_topic(request: TopicRequest):
    try:
        logger.info(f"Received topic selection request: {request.topic}")
        result = normalize_topic(request.topic)
        return TopicResponse(**result)
    except Exception as e:
        logger.error(f"Error normalizing topic: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process topic selection")
  
