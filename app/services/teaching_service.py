# app/services/teaching_service.py
"""
Teaching service for managing interactive tutoring sessions.
"""

import json
import logging
import uuid
from typing import Dict, Any, Optional, List
from app.llm.teaching_llm import teaching_llm
from app.models.tutor_model import TutorPersona
from app.services.tutor_service import tutor_service
from app.services.progress_service import progress_service
from app.models.progress_model import ProgressUpdateRequest

# Configure logging
logger = logging.getLogger(__name__)
from app.services.evaluation_service import evaluation_service

# Configure logging
logger = logging.getLogger(__name__)

class TeachingSession:
    """Class representing a teaching session."""
    
    def __init__(self, session_id: str, user_id: str, subject: str, topic: str, 
                 user_level: str, tutor: Dict[str, Any]):
        self.session_id = session_id
        self.user_id = user_id
        self.subject = subject
        self.topic = topic
        self.user_level = user_level
        self.tutor = tutor
        self.started_at = self._get_current_timestamp()
        self.current_step = 1
        self.total_steps = 5  # Default number of steps
        self.completed_steps = []
        self.questions_answered = []
        self.session_state = "active"  # active, paused, completed, abandoned
        self.adaptation_history = []  # Track adaptations made during the session
        self.last_interaction_time = self.started_at  # Track last activity
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary format."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "subject": self.subject,
            "topic": self.topic,
            "user_level": self.user_level,
            "tutor": self.tutor,
            "started_at": self.started_at,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "completed_steps": self.completed_steps,
            "questions_answered": self.questions_answered,
            "session_state": self.session_state,
            "adaptation_history": self.adaptation_history,
            "last_interaction_time": self.last_interaction_time
        }
    
    def add_adaptation(self, adaptation: Dict[str, Any]):
        """Add an adaptation to the session's history."""
        self.adaptation_history.append({
            "timestamp": self._get_current_timestamp(),
            "adaptation": adaptation
        })
    
    def update_last_interaction(self):
        """Update the last interaction time."""
        self.last_interaction_time = self._get_current_timestamp()
    
    def mark_step_complete(self, step_number: int):
        """Mark a step as completed."""
        if step_number not in self.completed_steps:
            self.completed_steps.append(step_number)
            self.completed_steps.sort()  # Keep steps in order

import os
import json
import pickle
from datetime import datetime

class TeachingService:
    """Service for managing interactive tutoring sessions."""
    
    def __init__(self):
        """Initialize the Teaching Service."""
        self.sessions = {}  # In-memory storage for teaching sessions
        self.session_storage_path = "./session_storage"  # Directory for session persistence
        self._ensure_storage_directory()
    
    def _ensure_storage_directory(self):
        """Ensure the session storage directory exists."""
        if not os.path.exists(self.session_storage_path):
            os.makedirs(self.session_storage_path)
    
    def _get_session_file_path(self, session_id: str) -> str:
        """Get the file path for a specific session."""
        return os.path.join(self.session_storage_path, f"{session_id}.json")
    
    def save_session_to_storage(self, session_id: str):
        """Save a session to persistent storage."""
        session = self.sessions.get(session_id)
        if not session:
            logger.warning(f"Cannot save session {session_id} - session not found")
            return
        
        try:
            # Convert session to dictionary for storage
            session_data = session.to_dict()
            
            # Write session data to file
            file_path = self._get_session_file_path(session_id)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved session {session_id} to persistent storage")
        except Exception as e:
            logger.error(f"Error saving session {session_id} to storage: {e}")
    
    def load_session_from_storage(self, session_id: str) -> Optional[TeachingSession]:
        """Load a session from persistent storage."""
        try:
            file_path = self._get_session_file_path(session_id)
            if not os.path.exists(file_path):
                logger.warning(f"Session file {file_path} does not exist")
                return None
            
            # Read session data from file
            with open(file_path, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # Create a new TeachingSession object from the loaded data
            session = TeachingSession(
                session_id=session_data["session_id"],
                user_id=session_data["user_id"],
                subject=session_data["subject"],
                topic=session_data["topic"],
                user_level=session_data["user_level"],
                tutor=session_data["tutor"]
            )
            session.started_at = session_data["started_at"]
            session.current_step = session_data["current_step"]
            session.total_steps = session_data["total_steps"]
            session.completed_steps = session_data["completed_steps"]
            session.questions_answered = session_data["questions_answered"]
            session.session_state = session_data["session_state"]
            
            # Add the loaded session to active sessions
            self.sessions[session_id] = session
            
            logger.info(f"Loaded session {session_id} from persistent storage")
            return session
        except Exception as e:
            logger.error(f"Error loading session {session_id} from storage: {e}")
            return None
    
    def delete_session_from_storage(self, session_id: str):
        """Delete a session from persistent storage."""
        try:
            file_path = self._get_session_file_path(session_id)
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted session {session_id} from persistent storage")
        except Exception as e:
            logger.error(f"Error deleting session {session_id} from storage: {e}")
    
    def pause_session(self, session_id: str):
        """Pause a teaching session and save it to storage."""
        session = self.sessions.get(session_id)
        if not session:
            raise Exception(f"Session {session_id} not found")
        
        # Update session state
        session.session_state = "paused"
        
        # Save to persistent storage
        self.save_session_to_storage(session_id)
        
        logger.info(f"Paused session {session_id} and saved to storage")
    
    def resume_session(self, session_id: str) -> Dict[str, Any]:
        """Resume a teaching session from storage."""
        # First, check if session is already in memory
        session = self.sessions.get(session_id)
        if session and session.session_state == "active":
            logger.info(f"Session {session_id} is already active in memory")
            return self.get_session_progress(session_id)
        
        # If not in memory, try to load from storage
        if not session:
            session = self.load_session_from_storage(session_id)
        
        if not session:
            raise Exception(f"Session {session_id} not found in memory or storage")
        
        # Update session state
        session.session_state = "active"
        
        logger.info(f"Resumed session {session_id}")
        return self.get_session_progress(session_id)
    
    def start_teaching_session(self, user_id: str, subject: str, topic: str, 
                              user_level: str = "newbie") -> Dict[str, Any]:
        """
        Start a new teaching session for a user.
        
        Args:
            user_id: The ID of the user
            subject: The subject to teach
            topic: The specific topic within the subject
            user_level: User's skill level (newbie, amateur, pro)
            
        Returns:
            Dictionary containing session information and first lesson step.
        """
        try:
            # Get user's tutor preference
            tutor_pref = tutor_service.get_user_tutor_preference(user_id)
            if not tutor_pref:
                # If no tutor preference, assign a default tutor
                tutor_pref = {"tutor_id": "friendly_alice"}
            
            # Get tutor persona
            tutor = tutor_service.get_tutor_by_id(tutor_pref["tutor_id"])
            if not tutor:
                tutor = tutor_service.get_tutor_by_id("friendly_alice")
            
            # Create session with UUID for better session management
            session_id = str(uuid.uuid4())
            session = TeachingSession(
                session_id=session_id,
                user_id=user_id,
                subject=subject,
                topic=topic,
                user_level=user_level,
                tutor=tutor.dict() if tutor else {}
            )
            
            # Store session
            self.sessions[session_id] = session
            
            # Save session to persistent storage
            self.save_session_to_storage(session_id)
            
            # Deliver the first lesson step
            first_step = self.deliver_lesson_step(session_id)
            
            logger.info(f"Started teaching session {session_id} for user {user_id}")
            
            result = {
                "session_id": session_id,
                "subject": subject,
                "topic": topic,
                "user_level": user_level,
                "tutor": tutor.dict() if tutor else {},
                "current_step": 1,
                "total_steps": session.total_steps,
                "lesson_step": first_step
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error starting teaching session for user {user_id}: {e}")
            raise Exception(f"Failed to start teaching session: {e}")
    
    def deliver_lesson_step(self, session_id: str, step_number: Optional[int] = None) -> Dict[str, Any]:
        """
        Deliver a specific lesson step to the user.
        
        Args:
            session_id: The ID of the teaching session
            step_number: Specific step number to deliver (optional)
            
        Returns:
            Dictionary containing the lesson step content.
        """
        try:
            # Get session data
            session = self.sessions.get(session_id)
            if not session:
                raise Exception(f"Session {session_id} not found")
            
            # Determine which step to deliver
            if step_number is None:
                step_number = session.current_step
            
            # Validate step number
            if step_number < 1 or step_number > session.total_steps:
                raise Exception(f"Invalid step number: {step_number}. Must be between 1 and {session.total_steps}")
            
            # Get tutor persona
            tutor_persona = session.tutor
            
            # Use teaching LLM to generate lesson content
            lesson_step = teaching_llm.deliver_lesson_step(
                subject=session.subject,
                topic=session.topic,
                step_number=step_number,
                total_steps=session.total_steps,
                user_level=session.user_level,
                tutor_persona=tutor_persona
            )
            
            # Update session progress
            session.current_step = step_number
            
            logger.info(f"Delivered lesson step {step_number} for session {session_id}")
            
            return lesson_step
            
        except Exception as e:
            logger.error(f"Error delivering lesson step for session {session_id}: {e}")
            # Return mock data as fallback
            return self._mock_lesson_step(session_id, step_number)
    
    def generate_question(self, session_id: str, concept: str, 
                         question_type: str = "multiple_choice") -> Dict[str, Any]:
        """
        Generate an interactive question for the user.
        
        Args:
            session_id: The ID of the teaching session
            concept: The specific concept to test
            question_type: Type of question to generate
            
        Returns:
            Dictionary containing the question and possible answers.
        """
        try:
            # Get session data
            session = self.sessions.get(session_id)
            if not session:
                raise Exception(f"Session {session_id} not found")
            
            # Get tutor persona
            tutor_persona = session.tutor
            
            # Use teaching LLM to generate question
            question = teaching_llm.generate_interactive_question(
                subject=session.subject,
                topic=session.topic,
                concept=concept,
                question_type=question_type,
                tutor_persona=tutor_persona
            )
            
            logger.info(f"Generated {question_type} question for session {session_id}")
            
            return question
            
        except Exception as e:
            logger.error(f"Error generating question for session {session_id}: {e}")
            # Return mock data as fallback
            return self._mock_question(session_id, concept, question_type)
    
    def advance_to_next_step(self, session_id: str) -> Dict[str, Any]:
        """
        Advance to the next lesson step in the session.
        
        Args:
            session_id: The ID of the teaching session
            
        Returns:
            Dictionary containing the next lesson step content.
        """
        try:
            # Get session data
            session = self.sessions.get(session_id)
            if not session:
                raise Exception(f"Session {session_id} not found")
            
            # Check if we're at the end of the lesson
            if session.current_step >= session.total_steps:
                # Mark the final step as completed
                if session.current_step not in session.completed_steps:
                    session.mark_step_complete(session.current_step)
                
                # Mark session as completed
                session.session_state = "completed"
                
                return {
                    "status": "completed",
                    "message": "You have completed this lesson!",
                    "current_step": session.current_step,
                    "total_steps": session.total_steps
                }
            
            # Before advancing, check if adaptation is needed based on performance
            from app.services.adaptive_learning_service import adaptive_learning_service
            adaptation = adaptive_learning_service.adapt_lesson_path(
                user_id=session.user_id,
                subject=session.subject,
                topic=session.topic,
                current_step=session.current_step,
                total_steps=session.total_steps
            )
            
            # Add adaptation to session history
            session.add_adaptation(adaptation)
            
            # If adaptation suggests remedial content, handle it
            if adaptation["adaptation_type"] == "remedial" and not adaptation["continue_path"]:
                # User needs remedial content, don't advance normally
                return {
                    "status": "remedial",
                    "message": adaptation["message"],
                    "recommended_action": adaptation["recommended_action"],
                    "remedial_content": adaptation["remedial_content"],
                    "recommendations": adaptation["recommendations"],
                    "current_step": session.current_step,
                    "total_steps": session.total_steps
                }
            
            # If adaptation suggests acceleration, skip steps
            if adaptation["adaptation_type"] == "acceleration" and adaptation["continue_path"]:
                next_step = adaptation["next_step"]
            else:
                # Normal progression
                next_step = session.current_step + 1
            
            # Mark current step as completed
            session.mark_step_complete(session.current_step)
            
            # Update session with next step
            session.current_step = next_step
            
            # Update last interaction time
            session.update_last_interaction()
            
            # Save session to persistent storage
            self.save_session_to_storage(session_id)
            
            # Log progress to the progress service
            try:
                progress_request = ProgressUpdateRequest(
                    user_id=session.user_id,
                    lesson_id=f"{session.topic}_step_{session.current_step - 1}",
                    subject=session.subject,
                    completed=True,
                    time_spent_seconds=300,  # Assuming 5 minutes per step
                    notes=f"Completed step {session.current_step - 1} of {session.topic}"
                )
                progress_service.update_progress(progress_request)
            except Exception as e:
                logger.error(f"Error logging progress for user {session.user_id}: {e}")
            
            # If we've reached the end after adaptation
            if session.current_step > session.total_steps:
                # Mark session as completed
                session.session_state = "completed"
                
                return {
                    "status": "completed",
                    "message": "You have completed this lesson!",
                    "current_step": session.current_step - 1,  # Report the last step
                    "total_steps": session.total_steps
                }
            
            # Deliver the next lesson step
            lesson_step = self.deliver_lesson_step(session_id, next_step)
            
            return {
                "status": "continuing",
                "current_step": next_step,
                "total_steps": session.total_steps,
                "lesson_step": lesson_step
            }
            
        except Exception as e:
            logger.error(f"Error advancing to next step for session {session_id}: {e}")
            raise Exception(f"Failed to advance to next step: {e}")
    
    def get_session_progress(self, session_id: str) -> Dict[str, Any]:
        """
        Get the progress of a teaching session.
        
        Args:
            session_id: The ID of the teaching session
            
        Returns:
            Dictionary containing session progress information.
        """
        try:
            # Get session data
            session = self.sessions.get(session_id)
            if not session:
                raise Exception(f"Session {session_id} not found")
            
            completed_count = len(session.completed_steps)
            total_steps = session.total_steps
            progress_percentage = (completed_count / total_steps) * 100 if total_steps > 0 else 0
            
            return {
                "session_id": session_id,
                "subject": session.subject,
                "topic": session.topic,
                "current_step": session.current_step,
                "total_steps": total_steps,
                "completed_steps": session.completed_steps,
                "questions_answered": session.questions_answered,
                "progress_percentage": round(progress_percentage, 2),
                "session_state": session.session_state,
                "started_at": session.started_at
            }
            
        except Exception as e:
            logger.error(f"Error getting progress for session {session_id}: {e}")
            raise Exception(f"Failed to get session progress: {e}")
    
    def end_session(self, session_id: str) -> Dict[str, Any]:
        """
        End a teaching session and clean up resources.
        
        Args:
            session_id: The ID of the teaching session
            
        Returns:
            Dictionary containing session summary.
        """
        try:
            # Get session data
            session = self.sessions.get(session_id)
            if not session:
                raise Exception(f"Session {session_id} not found")
            
            # Update session state to ended
            session.session_state = "ended"
            
            # Get final progress before deleting from memory
            progress = self.get_session_progress(session_id)
            
            # Clean up session data
            if session_id in self.sessions:
                del self.sessions[session_id]
            
            # Also remove from persistent storage
            self.delete_session_from_storage(session_id)
            
            logger.info(f"Ended teaching session {session_id}")
            
            return {
                "session_id": session_id,
                "status": "ended",
                "subject": session.subject,
                "topic": session.topic,
                "progress_summary": progress,
                "ended_at": self._get_current_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Error ending session {session_id}: {e}")
            raise Exception(f"Failed to end session: {e}")
    
    def _mock_lesson_step(self, session_id: str, step_number: int) -> Dict[str, Any]:
        """Generate mock lesson step data."""
        session = self.sessions.get(session_id)
        if not session:
            subject = "Unknown Subject"
            topic = "Unknown Topic"
            total_steps = 5
        else:
            subject = session.subject
            topic = session.topic
            total_steps = session.total_steps
        
        return {
            "step_number": step_number,
            "total_steps": total_steps,
            "title": f"Introduction to {topic} - Step {step_number}",
            "content": f"This is a mock lesson step {step_number} of {total_steps} for {subject}: {topic}. In a real implementation, this would contain actual educational content generated by an AI tutor.",
            "examples": [
                f"Example related to {topic}",
                f"Another example for {subject}"
            ],
            "key_points": [
                f"Key concept {step_number} in {topic}",
                f"Important point about {subject}"
            ],
            "estimated_time_min": 5,
            "next_step_preview": f"In the next step, we'll explore more concepts in {topic}."
        }
    
    def _mock_question(self, session_id: str, concept: str, question_type: str) -> Dict[str, Any]:
        """Generate mock question data."""
        session = self.sessions.get(session_id)
        if not session:
            subject = "Unknown Subject"
            topic = "Unknown Topic"
        else:
            subject = session.subject
            topic = session.topic
        
        return {
            "question_type": question_type,
            "question": f"What is the most important aspect of {concept} in {subject}?",
            "options": [
                f"A fundamental principle of {concept}",
                f"A common misconception about {topic}",
                f"An advanced application of {concept}",
                f"None of the above"
            ],
            "correct_answer": 0,
            "explanation": f"This is a mock question about {concept} in {subject}. In a real implementation, this would be a carefully crafted question generated by an AI tutor.",
            "difficulty": "medium"
        }
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()

# Global instance
teaching_service = TeachingService()