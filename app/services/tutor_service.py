# app/services/tutor_service.py
"""
Tutor service for managing tutor personas and user preferences.
"""

from typing import List, Optional, Dict
from app.models.tutor_model import TutorPersona, TutorSelectionRequest, UserTutorPreference

class TutorService:
    """Service for managing tutor personas and user preferences."""
    
    def __init__(self):
        # In-memory storage for tutor personas (would be replaced with DB in production)
        self.tutors: Dict[str, TutorPersona] = {}
        # In-memory storage for user preferences (would be replaced with DB in production)
        self.user_preferences: Dict[str, UserTutorPreference] = {}
        
        # Initialize with some default tutors
        self._initialize_default_tutors()
    
    def _initialize_default_tutors(self):
        """Initialize the service with default tutor personas."""
        default_tutors = [
            TutorPersona(
                tutor_id="friendly_alice",
                name="Friendly Alice",
                character_style="friendly",
                humor_level="medium",
                tone="encouraging",
                complexity="simple",
                description="A warm and encouraging tutor who makes learning enjoyable.",
                avatar_url=None
            ),
            TutorPersona(
                tutor_id="professor_bob",
                name="Professor Bob",
                character_style="professional",
                humor_level="low",
                tone="direct",
                complexity="complex",
                description="A knowledgeable professor who delivers content in a structured manner.",
                avatar_url=None
            ),
            TutorPersona(
                tutor_id="funny_charlie",
                name="Funny Charlie",
                character_style="funny",
                humor_level="high",
                tone="casual",
                complexity="simple",
                description="A humorous tutor who uses jokes and analogies to make learning memorable.",
                avatar_url=None
            ),
            TutorPersona(
                tutor_id="coach_dana",
                name="Coach Dana",
                character_style="motivational",
                humor_level="medium",
                tone="encouraging",
                complexity="moderate",
                description="A motivational coach who helps you push through challenges.",
                avatar_url=None
            )
        ]
        
        for tutor in default_tutors:
            self.tutors[tutor.tutor_id] = tutor
    
    def get_all_tutors(self) -> List[TutorPersona]:
        """
        Get all available tutor personas.
        
        Returns:
            List of all tutor personas.
        """
        return list(self.tutors.values())
    
    def get_tutor_by_id(self, tutor_id: str) -> Optional[TutorPersona]:
        """
        Get a tutor persona by ID.
        
        Args:
            tutor_id: The ID of the tutor to retrieve.
            
        Returns:
            The tutor persona if found, None otherwise.
        """
        return self.tutors.get(tutor_id)
    
    def select_tutor_for_user(self, request: TutorSelectionRequest) -> Optional[TutorPersona]:
        """
        Select a tutor for a user based on their preferences.
        
        Args:
            request: The tutor selection request containing user preferences.
            
        Returns:
            The selected tutor persona, or None if no matching tutor is found.
        """
        # If user specified exact preferences, try to find a matching tutor
        if request.character_style or request.humor_level or request.tone or request.complexity:
            for tutor in self.tutors.values():
                if (not request.character_style or tutor.character_style == request.character_style) and \
                   (not request.humor_level or tutor.humor_level == request.humor_level) and \
                   (not request.tone or tutor.tone == request.tone) and \
                   (not request.complexity or tutor.complexity == request.complexity):
                    # Save user preference
                    import datetime
                    preference = UserTutorPreference(
                        user_id=request.user_id,
                        tutor_id=tutor.tutor_id,
                        selected_at=datetime.datetime.now().isoformat()
                    )
                    self.user_preferences[request.user_id] = preference
                    return tutor
        
        # If no specific preferences or no match found, return the first tutor
        if self.tutors:
            first_tutor = next(iter(self.tutors.values()))
            # Save user preference
            import datetime
            preference = UserTutorPreference(
                user_id=request.user_id,
                tutor_id=first_tutor.tutor_id,
                selected_at=datetime.datetime.now().isoformat()
            )
            self.user_preferences[request.user_id] = preference
            return first_tutor
        
        return None
    
    def get_user_tutor_preference(self, user_id: str) -> Optional[UserTutorPreference]:
        """
        Get a user's tutor preference.
        
        Args:
            user_id: The ID of the user.
            
        Returns:
            The user's tutor preference if found, None otherwise.
        """
        return self.user_preferences.get(user_id)

# Global instance of the tutor service
tutor_service = TutorService()