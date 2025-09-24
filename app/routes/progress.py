"""
Progress tracking routes for the learning service.
"""

from fastapi import APIRouter, HTTPException
from app.models.progress_model import (
    ProgressUpdateRequest,
    ProgressResponse,
    UserProgress,
    ProgressAnalytics
)
from app.services.progress_service import progress_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/progress", tags=["Progress"])

@router.post("/", response_model=ProgressResponse)
async def update_user_progress(request: ProgressUpdateRequest):
    """
    Update user's progress for a lesson or module.
    
    Args:
        request: Progress update request containing user ID, lesson/module ID, and progress details.
        
    Returns:
        ProgressResponse with updated progress information.
    """
    try:
        logger.info(f"Updating progress for user {request.user_id}")
        
        # Update progress in the service
        updated_progress = progress_service.update_progress(request)
        
        logger.info(f"Successfully updated progress for user {request.user_id}")
        
        return ProgressResponse(
            user_id=updated_progress.user_id,
            subject=updated_progress.subject,
            current_lesson_id=updated_progress.current_lesson_id,
            current_module_id=updated_progress.current_module_id,
            total_lessons_completed=updated_progress.total_lessons_completed,
            total_modules_completed=updated_progress.total_modules_completed,
            overall_score=updated_progress.overall_score,
            completion_percentage=updated_progress.completion_percentage,
            message="Progress updated successfully",
            last_updated=updated_progress.last_accessed or request.__dict__.get('last_updated', __import__('datetime').datetime.now())
        )
        
    except Exception as e:
        logger.error(f"Error updating progress for user {request.user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update progress: {e}")

@router.get("/{user_id}/{subject}", response_model=UserProgress)
async def get_user_progress(user_id: str, subject: str):
    """
    Get a user's progress for a specific subject.
    
    Args:
        user_id: The ID of the user.
        subject: The subject to retrieve progress for.
        
    Returns:
        UserProgress with detailed progress information.
    """
    try:
        logger.info(f"Retrieving progress for user {user_id}, subject: {subject}")
        
        progress = progress_service.get_user_progress(user_id, subject)
        
        if not progress:
            logger.warning(f"No progress found for user {user_id}, subject: {subject}")
            raise HTTPException(status_code=404, detail="User progress not found")
        
        logger.info(f"Successfully retrieved progress for user {user_id}, subject: {subject}")
        return progress
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving progress for user {user_id}, subject: {subject}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve progress: {e}")

@router.get("/{user_id}/{subject}/analytics", response_model=ProgressAnalytics)
async def get_progress_analytics(user_id: str, subject: str):
    """
    Get detailed analytics for a user's progress in a specific subject.
    
    Args:
        user_id: The ID of the user.
        subject: The subject to retrieve analytics for.
        
    Returns:
        ProgressAnalytics with detailed progress analytics.
    """
    try:
        logger.info(f"Retrieving analytics for user {user_id}, subject: {subject}")
        
        analytics = progress_service.get_progress_analytics(user_id, subject)
        
        if not analytics:
            logger.warning(f"No analytics found for user {user_id}, subject: {subject}")
            raise HTTPException(status_code=404, detail="User analytics not found")
        
        logger.info(f"Successfully retrieved analytics for user {user_id}, subject: {subject}")
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving analytics for user {user_id}, subject: {subject}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve analytics: {e}")

@router.delete("/{user_id}/{subject}", response_model=dict)
async def reset_user_progress(user_id: str, subject: str):
    """
    Reset a user's progress for a specific subject.
    
    Args:
        user_id: The ID of the user.
        subject: The subject to reset progress for.
        
    Returns:
        Dictionary with reset confirmation.
    """
    try:
        logger.info(f"Resetting progress for user {user_id}, subject: {subject}")
        
        success = progress_service.reset_user_progress(user_id, subject)
        
        if not success:
            logger.warning(f"Failed to reset progress for user {user_id}, subject: {subject}")
            raise HTTPException(status_code=404, detail="User progress not found")
        
        message = f"Progress for user {user_id} in subject {subject} has been reset"
        logger.info(message)
        
        return {
            "user_id": user_id,
            "subject": subject,
            "message": message,
            "reset": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting progress for user {user_id}, subject: {subject}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reset progress: {e}")