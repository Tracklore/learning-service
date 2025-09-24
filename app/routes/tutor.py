# app/routes/tutor.py
"""
Tutor routes for the learning service.
"""

from fastapi import APIRouter, HTTPException
from app.models.tutor_model import TutorPersona, TutorSelectionRequest, TutorResponse
from app.services.tutor_service import tutor_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/tutor", tags=["Tutor"])

@router.get("/", response_model=list[TutorPersona])
async def list_tutors():
    """
    List all available tutor personas.
    
    Returns:
        List of all available tutor personas.
    """
    try:
        tutors = tutor_service.get_all_tutors()
        logger.info("Retrieved list of tutors")
        return tutors
    except Exception as e:
        logger.error(f"Error retrieving tutors: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve tutors")

@router.get("/{tutor_id}", response_model=TutorPersona)
async def get_tutor(tutor_id: str):
    """
    Get a specific tutor persona by ID.
    
    Args:
        tutor_id: The ID of the tutor to retrieve.
        
    Returns:
        The requested tutor persona.
    """
    try:
        tutor = tutor_service.get_tutor_by_id(tutor_id)
        if not tutor:
            logger.warning(f"Tutor with ID {tutor_id} not found")
            raise HTTPException(status_code=404, detail="Tutor not found")
        
        logger.info(f"Retrieved tutor with ID: {tutor_id}")
        return tutor
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving tutor {tutor_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve tutor")

@router.post("/select", response_model=TutorResponse)
async def select_tutor(request: TutorSelectionRequest):
    """
    Select a tutor for a user based on their preferences.
    
    Args:
        request: The tutor selection request containing user preferences.
        
    Returns:
        The selected tutor persona and confirmation message.
    """
    try:
        tutor = tutor_service.select_tutor_for_user(request)
        if not tutor:
            logger.warning("No tutor available for selection")
            raise HTTPException(status_code=404, detail="No tutor available")
        
        message = f"Tutor '{tutor.name}' has been selected for user '{request.user_id}'"
        logger.info(message)
        
        return TutorResponse(tutor=tutor, message=message)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error selecting tutor for user {request.user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to select tutor")

@router.get("/user/{user_id}", response_model=TutorPersona)
async def get_user_tutor(user_id: str):
    """
    Get the tutor currently assigned to a user.
    
    Args:
        user_id: The ID of the user.
        
    Returns:
        The tutor persona currently assigned to the user.
    """
    try:
        preference = tutor_service.get_user_tutor_preference(user_id)
        if not preference:
            logger.warning(f"No tutor preference found for user {user_id}")
            raise HTTPException(status_code=404, detail="No tutor assigned to user")
        
        tutor = tutor_service.get_tutor_by_id(preference.tutor_id)
        if not tutor:
            logger.error(f"Tutor {preference.tutor_id} not found for user {user_id}")
            raise HTTPException(status_code=500, detail="Assigned tutor not found")
        
        logger.info(f"Retrieved tutor for user {user_id}")
        return tutor
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user {user_id} tutor: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user tutor")