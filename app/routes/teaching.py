# app/routes/teaching.py
"""
Teaching routes for interactive tutoring sessions.
"""

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.services.teaching_service import teaching_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/teaching", tags=["Teaching"])

class StartSessionRequest(BaseModel):
    """Request model for starting a teaching session."""
    user_id: str
    subject: str
    topic: str
    user_level: str = "newbie"

class LessonStepRequest(BaseModel):
    """Request model for delivering a lesson step."""
    session_id: str
    step_number: Optional[int] = None

class QuestionRequest(BaseModel):
    """Request model for generating a question."""
    session_id: str
    concept: str
    question_type: str = "multiple_choice"

class AdvanceStepRequest(BaseModel):
    """Request model for advancing to the next step."""
    session_id: str

@router.post("/session/start", response_model=Dict[str, Any])
async def start_teaching_session(request: StartSessionRequest):
    """
    Start a new teaching session for a user.
    
    Args:
        request: The session start request containing user ID, subject, and topic.
        
    Returns:
        Dictionary containing session information and first lesson step.
    """
    try:
        logger.info(f"Starting teaching session for user {request.user_id}")
        
        session = teaching_service.start_teaching_session(
            user_id=request.user_id,
            subject=request.subject,
            topic=request.topic,
            user_level=request.user_level
        )
        
        logger.info(f"Successfully started teaching session {session['session_id']}")
        return session
        
    except Exception as e:
        logger.error(f"Error starting teaching session for user {request.user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start teaching session: {e}")

@router.post("/lesson/step", response_model=Dict[str, Any])
async def deliver_lesson_step(request: LessonStepRequest):
    """
    Deliver a specific lesson step to the user.
    
    Args:
        request: The lesson step request containing session ID and optional step number.
        
    Returns:
        Dictionary containing the lesson step content.
    """
    try:
        logger.info(f"Delivering lesson step for session {request.session_id}")
        
        lesson_step = teaching_service.deliver_lesson_step(
            session_id=request.session_id,
            step_number=request.step_number
        )
        
        logger.info(f"Successfully delivered lesson step for session {request.session_id}")
        return lesson_step
        
    except Exception as e:
        logger.error(f"Error delivering lesson step for session {request.session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to deliver lesson step: {e}")

@router.post("/question/generate", response_model=Dict[str, Any])
async def generate_question(request: QuestionRequest):
    """
    Generate an interactive question for the user.
    
    Args:
        request: The question request containing session ID and concept.
        
    Returns:
        Dictionary containing the question and possible answers.
    """
    try:
        logger.info(f"Generating question for session {request.session_id}")
        
        question = teaching_service.generate_question(
            session_id=request.session_id,
            concept=request.concept,
            question_type=request.question_type
        )
        
        logger.info(f"Successfully generated question for session {request.session_id}")
        return question
        
    except Exception as e:
        logger.error(f"Error generating question for session {request.session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate question: {e}")

@router.post("/session/advance", response_model=Dict[str, Any])
async def advance_to_next_step(request: AdvanceStepRequest):
    """
    Advance to the next lesson step in the session.
    
    Args:
        request: The advance step request containing session ID.
        
    Returns:
        Dictionary containing the next lesson step content or completion status.
    """
    try:
        logger.info(f"Advancing to next step for session {request.session_id}")
        
        result = teaching_service.advance_to_next_step(request.session_id)
        
        logger.info(f"Successfully advanced to next step for session {request.session_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error advancing to next step for session {request.session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to advance to next step: {e}")

@router.get("/session/{session_id}/progress", response_model=Dict[str, Any])
async def get_session_progress(session_id: str):
    """
    Get the progress of a teaching session.
    
    Args:
        session_id: The ID of the teaching session.
        
    Returns:
        Dictionary containing session progress information.
    """
    try:
        logger.info(f"Getting progress for session {session_id}")
        
        progress = teaching_service.get_session_progress(session_id)
        
        logger.info(f"Successfully retrieved progress for session {session_id}")
        return progress
        
    except Exception as e:
        logger.error(f"Error getting progress for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get session progress: {e}")

@router.post("/session/{session_id}/end", response_model=Dict[str, Any])
async def end_session(session_id: str):
    """
    End a teaching session and clean up resources.
    
    Args:
        session_id: The ID of the teaching session.
        
    Returns:
        Dictionary containing session summary.
    """
    try:
        logger.info(f"Ending session {session_id}")
        
        summary = teaching_service.end_session(session_id)
        
        logger.info(f"Successfully ended session {session_id}")
        return summary
        
    except Exception as e:
        logger.error(f"Error ending session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to end session: {e}")

@router.post("/session/{session_id}/pause", response_model=Dict[str, Any])
async def pause_session(session_id: str):
    """
    Pause a teaching session and save its state.
    
    Args:
        session_id: The ID of the teaching session.
        
    Returns:
        Dictionary containing pause confirmation.
    """
    try:
        logger.info(f"Pausing session {session_id}")
        
        teaching_service.pause_session(session_id)
        
        logger.info(f"Successfully paused session {session_id}")
        return {
            "session_id": session_id,
            "status": "paused",
            "message": f"Session {session_id} has been paused and saved"
        }
        
    except Exception as e:
        logger.error(f"Error pausing session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to pause session: {e}")

@router.post("/session/{session_id}/resume", response_model=Dict[str, Any])
async def resume_session(session_id: str):
    """
    Resume a teaching session from saved state.
    
    Args:
        session_id: The ID of the teaching session.
        
    Returns:
        Dictionary containing session progress.
    """
    try:
        logger.info(f"Resuming session {session_id}")
        
        progress = teaching_service.resume_session(session_id)
        
        logger.info(f"Successfully resumed session {session_id}")
        return progress
        
    except Exception as e:
        logger.error(f"Error resuming session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to resume session: {e}")