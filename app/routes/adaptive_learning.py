"""
Adaptive learning routes for lesson path adaptation and content delivery.
"""

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.services.adaptive_learning_service import adaptive_learning_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/adaptive", tags=["Adaptive Learning"])

class AdaptationRequest(BaseModel):
    """Request model for lesson path adaptation."""
    user_id: str
    subject: str
    topic: str
    current_step: int
    total_steps: int

class ConceptPracticeRequest(BaseModel):
    """Request model for concept practice suggestions."""
    user_id: str
    subject: str
    topic: str
    concept: str

@router.post("/adaptation", response_model=Dict[str, Any])
async def adapt_lesson_path(request: AdaptationRequest):
    """
    Adapt the lesson path based on user's performance.
    
    Args:
        request: The adaptation request containing user ID, subject, topic, and step information.
        
    Returns:
        Dictionary containing adaptation recommendations.
    """
    try:
        logger.info(f"Adapting lesson path for user {request.user_id}, subject: {request.subject}, topic: {request.topic}")
        
        adaptation = adaptive_learning_service.adapt_lesson_path(
            user_id=request.user_id,
            subject=request.subject,
            topic=request.topic,
            current_step=request.current_step,
            total_steps=request.total_steps
        )
        
        logger.info(f"Successfully adapted lesson path for user {request.user_id}")
        return adaptation
        
    except Exception as e:
        logger.error(f"Error adapting lesson path for user {request.user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to adapt lesson path: {e}")

@router.get("/adaptation/history/{user_id}", response_model=Dict[str, Any])
async def get_user_adaptation_history(user_id: str):
    """
    Get the adaptation history for a user.
    
    Args:
        user_id: The ID of the user.
        
    Returns:
        Dictionary containing the user's adaptation history.
    """
    try:
        logger.info(f"Getting adaptation history for user {user_id}")
        
        history = adaptive_learning_service.get_user_adaptation_history(user_id)
        
        logger.info(f"Successfully retrieved adaptation history for user {user_id}")
        return {
            "user_id": user_id,
            "adaptation_history": history
        }
        
    except Exception as e:
        logger.error(f"Error getting adaptation history for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get adaptation history: {e}")

@router.post("/practice/suggest", response_model=Dict[str, Any])
async def suggest_concept_practice(request: ConceptPracticeRequest):
    """
    Suggest additional practice for a specific concept based on user performance.
    
    Args:
        request: The concept practice request containing user ID, subject, topic, and concept.
        
    Returns:
        Dictionary containing practice recommendations.
    """
    try:
        logger.info(f"Suggesting practice for user {request.user_id}, concept: {request.concept}")
        
        suggestion = adaptive_learning_service.suggest_concept_practice(
            user_id=request.user_id,
            subject=request.subject,
            topic=request.topic,
            concept=request.concept
        )
        
        logger.info(f"Successfully generated practice suggestion for user {request.user_id}")
        return suggestion
        
    except Exception as e:
        logger.error(f"Error suggesting practice for user {request.user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to suggest practice: {e}")