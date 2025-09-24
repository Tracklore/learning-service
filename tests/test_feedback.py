"""
Unit tests for feedback collection and processing functionality.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.feedback_service import feedback_service
from app.models.feedback_model import FeedbackSubmission
from datetime import datetime

client = TestClient(app)

def test_submit_feedback():
    """Test submitting feedback."""
    request_data = {
        "user_id": "test_user_feedback",
        "subject": "Mathematics",
        "lesson_id": "math_basic_algebra_1",
        "feedback_type": "lesson",
        "rating": 4,
        "content_rating": 5,
        "feedback_text": "This lesson was very helpful!",
        "suggestions": ["Add more practice problems"],
        "would_recommend": True,
        "timestamp": datetime.now().isoformat()
    }
    
    response = client.post("/feedback/submit", json=request_data)
    assert response.status_code == 200
    
    result = response.json()
    assert "feedback_id" in result
    assert result["user_id"] == request_data["user_id"]
    assert "Feedback submitted successfully" in result["message"]


def test_submit_curriculum_feedback():
    """Test submitting curriculum feedback."""
    request_data = {
        "user_id": "test_user_curriculum",
        "curriculum_id": "math_algebra_curriculum",
        "learning_path": "newbie",
        "overall_satisfaction": 4,
        "pacing_feedback": 4,
        "content_relevance": 5,
        "effectiveness": 4,
        "feedback_text": "Good curriculum, could use more real-world examples",
        "suggested_improvements": ["Add real-world examples"],
        "completed_modules": 5,
        "total_modules": 10,
        "timestamp": datetime.now().isoformat()
    }
    
    response = client.post("/feedback/curriculum", json=request_data)
    assert response.status_code == 200
    
    result = response.json()
    assert "feedback_id" in result
    assert result["user_id"] == request_data["user_id"]
    assert "Curriculum feedback submitted successfully" in result["message"]


def test_get_feedback_analytics():
    """Test getting feedback analytics for a subject."""
    # First submit some feedback to create analytics data
    feedback_request = {
        "user_id": "test_analytics_user",
        "subject": "Physics",
        "lesson_id": "physics_basic_1",
        "feedback_type": "lesson",
        "rating": 4,
        "timestamp": datetime.now().isoformat()
    }
    client.post("/feedback/submit", json=feedback_request)
    
    # Get analytics
    response = client.get("/feedback/Physics/analytics")
    assert response.status_code == 200
    
    result = response.json()
    assert result["subject"] == "Physics"
    assert "average_rating" in result
    assert "total_feedback" in result
    assert "rating_distribution" in result


def test_get_user_feedback_history():
    """Test getting a user's feedback history."""
    user_id = "test_history_user"
    
    # Submit multiple feedback entries
    feedback_requests = [
        {
            "user_id": user_id,
            "subject": "Biology",
            "lesson_id": "bio_cell_1",
            "feedback_type": "lesson",
            "rating": 5,
            "timestamp": datetime.now().isoformat()
        },
        {
            "user_id": user_id,
            "subject": "Biology",
            "lesson_id": "bio_genetics_1",
            "feedback_type": "lesson",
            "rating": 3,
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    for request in feedback_requests:
        client.post("/feedback/submit", json=request)
    
    # Get user feedback history
    response = client.get(f"/feedback/user/{user_id}")
    assert response.status_code == 200
    
    result = response.json()
    assert isinstance(result, list)
    assert len(result) >= 2  # At least the 2 entries we added


def test_get_nonexistent_feedback_analytics():
    """Test getting feedback analytics for a subject with no feedback."""
    response = client.get("/feedback/NonexistentSubject/analytics")
    assert response.status_code == 404


def test_service_submit_feedback():
    """Test the service method for submitting feedback directly."""
    feedback = FeedbackSubmission(
        user_id="test_service_feedback",
        subject="Chemistry",
        lesson_id="chem_basic_1",
        feedback_type="lesson",
        rating=4,
        feedback_text="Good content",
        timestamp=datetime.now()
    )
    
    response = feedback_service.submit_feedback(feedback)
    
    assert response.feedback_id
    assert response.user_id == feedback.user_id
    assert "Feedback submitted successfully" in response.message


def test_service_get_user_feedback_history():
    """Test the service method for getting user feedback history."""
    user_id = "test_service_history"
    
    # Submit feedback
    feedback1 = FeedbackSubmission(
        user_id=user_id,
        subject="Astronomy",
        lesson_id="astro_basic_1",
        feedback_type="lesson",
        rating=5,
        timestamp=datetime.now()
    )
    
    feedback2 = FeedbackSubmission(
        user_id=user_id,
        subject="Astronomy",
        lesson_id="astro_stars_1",
        feedback_type="lesson",
        rating=4,
        timestamp=datetime.now()
    )
    
    feedback_service.submit_feedback(feedback1)
    feedback_service.submit_feedback(feedback2)
    
    # Get history
    history = feedback_service.get_user_feedback_history(user_id)
    
    assert isinstance(history, list)
    assert len(history) >= 2
    assert all(fb.user_id == user_id for fb in history)