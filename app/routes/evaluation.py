"""
Evaluation routes for answer evaluation, hint generation, and complexity adjustment.
"""

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.services.evaluation_service import evaluation_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])

class AnswerEvaluationRequest(BaseModel):
    """Request model for answer evaluation."""
    user_id: str
    user_answer: str
    correct_answer: str
    question_context: Dict[str, Any]

class HintRequest(BaseModel):
    """Request model for hint generation."""
    user_id: str
    question_context: Dict[str, Any]
    hint_level: Optional[str] = "starter"  # starter, intermediate, advanced

class ComplexityAdjustmentRequest(BaseModel):
    """Request model for complexity adjustment."""
    user_id: str
    subject: str
    topic: str

class ProgressiveHintRequest(BaseModel):
    """Request model for progressive hint generation."""
    user_id: str
    question_context: Dict[str, Any]

@router.post("/answer/evaluate", response_model=Dict[str, Any])
async def evaluate_answer(request: AnswerEvaluationRequest):
    """
    Evaluate a user's answer to a question and provide feedback.
    
    Args:
        request: The answer evaluation request containing user answer and question context.
        
    Returns:
        Dictionary containing evaluation results and feedback.
    """
    try:
        logger.info(f"Evaluating answer for user {request.user_id}")
        
        result = evaluation_service.evaluate_answer(
            user_answer=request.user_answer,
            correct_answer=request.correct_answer,
            question_context=request.question_context,
            user_id=request.user_id
        )
        
        logger.info(f"Successfully evaluated answer for user {request.user_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error evaluating answer for user {request.user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to evaluate answer: {e}")

@router.post("/hint/generate", response_model=Dict[str, Any])
async def generate_hint(request: HintRequest):
    """
    Generate a hint for a question.
    
    Args:
        request: The hint request containing question context and hint level.
        
    Returns:
        Dictionary containing the generated hint.
    """
    try:
        logger.info(f"Generating hint for user {request.user_id}")
        
        result = evaluation_service.generate_hint(
            question_context=request.question_context,
            hint_level=request.hint_level
        )
        
        logger.info(f"Successfully generated hint for user {request.user_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error generating hint for user {request.user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate hint: {e}")

@router.post("/hint/progressive", response_model=Dict[str, Any])
async def get_progressive_hint(request: ProgressiveHintRequest):
    """
    Get the next progressive hint based on user's current position in the hint sequence.
    
    Args:
        request: The progressive hint request containing question context.
        
    Returns:
        Dictionary containing the next progressive hint.
    """
    try:
        logger.info(f"Getting progressive hint for user {request.user_id}")
        
        result = evaluation_service.get_progressive_hint(
            user_id=request.user_id,
            question_context=request.question_context
        )
        
        logger.info(f"Successfully retrieved progressive hint for user {request.user_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error getting progressive hint for user {request.user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get progressive hint: {e}")

@router.post("/complexity/adjust", response_model=Dict[str, Any])
async def adjust_complexity(request: ComplexityAdjustmentRequest):
    """
    Adjust the complexity of lessons based on user's performance.
    
    Args:
        request: The complexity adjustment request containing user ID, subject, and topic.
        
    Returns:
        Dictionary containing complexity adjustment recommendations.
    """
    try:
        logger.info(f"Adjusting complexity for user {request.user_id}, subject: {request.subject}, topic: {request.topic}")
        
        result = evaluation_service.adjust_complexity(
            user_id=request.user_id,
            subject=request.subject,
            topic=request.topic
        )
        
        logger.info(f"Successfully adjusted complexity for user {request.user_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error adjusting complexity for user {request.user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to adjust complexity: {e}")

@router.get("/performance/{user_id}", response_model=Dict[str, Any])
async def get_user_performance(user_id: str):
    """
    Get a summary of user's performance for adaptive learning.
    
    Args:
        user_id: The ID of the user.
        
    Returns:
        Dictionary containing performance statistics.
    """
    try:
        logger.info(f"Getting performance for user {user_id}")
        
        performance = evaluation_service.get_user_performance_summary(user_id)
        
        logger.info(f"Successfully retrieved performance for user {user_id}")
        return performance
        
    except Exception as e:
        logger.error(f"Error getting performance for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user performance: {e}")