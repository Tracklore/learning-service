"""
Feedback routes for the learning service.
"""

from fastapi import APIRouter, HTTPException
from app.models.feedback_model import (
    FeedbackSubmission,
    FeedbackResponse,
    FeedbackAnalytics,
    CurriculumFeedback
)
from app.services.feedback_service import feedback_service
from app.utils.logger import get_logger
from datetime import datetime

logger = get_logger(__name__)

router = APIRouter(prefix="/feedback", tags=["Feedback"])

@router.post("/submit", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackSubmission):
    """
    Submit feedback about lessons, tutors, or the learning experience.
    
    Args:
        request: Feedback submission containing user feedback details.
        
    Returns:
        FeedbackResponse confirming submission.
    """
    try:
        # Set timestamp if not provided
        if not hasattr(request, 'timestamp') or not request.timestamp:
            request.timestamp = datetime.now()
        
        response = feedback_service.submit_feedback(request)
        
        logger.info(f"Feedback submitted for user {request.user_id}, type: {request.feedback_type}")
        return response
        
    except Exception as e:
        logger.error(f"Error submitting feedback for user {request.user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {e}")

@router.post("/curriculum", response_model=FeedbackResponse)
async def submit_curriculum_feedback(request: CurriculumFeedback):
    """
    Submit feedback about a curriculum.
    
    Args:
        request: Curriculum feedback submission.
        
    Returns:
        FeedbackResponse confirming submission.
    """
    try:
        response = feedback_service.submit_curriculum_feedback(request)
        
        logger.info(f"Curriculum feedback submitted for user {request.user_id}, curriculum {request.curriculum_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error submitting curriculum feedback for user {request.user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit curriculum feedback: {e}")

@router.get("/{subject}/analytics", response_model=FeedbackAnalytics)
async def get_feedback_analytics(subject: str):
    """
    Get aggregated feedback analytics for a subject.
    
    Args:
        subject: The subject to retrieve analytics for.
        
    Returns:
        FeedbackAnalytics with aggregated feedback data.
    """
    try:
        analytics = feedback_service.get_feedback_analytics(subject)
        
        if not analytics:
            logger.warning(f"No feedback analytics found for subject: {subject}")
            raise HTTPException(status_code=404, detail="Feedback analytics not found")
        
        logger.info(f"Retrieved feedback analytics for subject: {subject}")
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving analytics for subject {subject}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve analytics: {e}")

@router.get("/user/{user_id}", response_model=list)
async def get_user_feedback_history(user_id: str):
    """
    Get feedback history for a specific user.
    
    Args:
        user_id: The ID of the user.
        
    Returns:
        List of feedback submissions by the user.
    """
    try:
        feedback_history = feedback_service.get_user_feedback_history(user_id)
        
        logger.info(f"Retrieved feedback history for user {user_id} ({len(feedback_history)} items)")
        return feedback_history
        
    except Exception as e:
        logger.error(f"Error retrieving feedback history for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve feedback history: {e}")

@router.post("/process-adjustment/{user_id}/{subject}", response_model=dict)
async def process_feedback_adjustment(user_id: str, subject: str):
    """
    Process feedback for a user and subject to trigger immediate curriculum adjustments.
    
    Args:
        user_id: The ID of the user.
        subject: The subject to adjust curriculum for.
        
    Returns:
        Dictionary confirming adjustment processing.
    """
    try:
        success = feedback_service.adjust_curriculum_based_on_feedback(user_id, subject)
        
        if success:
            message = f"Curriculum adjustment processed successfully for user {user_id} in subject {subject}"
            logger.info(message)
            return {
                "user_id": user_id,
                "subject": subject,
                "success": True,
                "message": message
            }
        else:
            message = f"Failed to process curriculum adjustment for user {user_id} in subject {subject}"
            logger.warning(message)
            return {
                "user_id": user_id,
                "subject": subject,
                "success": False,
                "message": message
            }
        
    except Exception as e:
        logger.error(f"Error processing curriculum adjustment for user {user_id} in subject {subject}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process adjustment: {e}")