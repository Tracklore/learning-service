"""
Integration tests for feedback to curriculum adjustment pipeline.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from datetime import datetime

client = TestClient(app)

def test_feedback_triggers_curriculum_adjustment():
    """Test that submitting feedback triggers curriculum adjustment."""
    user_id = "feedback_adjustment_user"
    subject = "Mathematics"
    
    # 1. Submit feedback indicating difficulty
    feedback_request = {
        "user_id": user_id,
        "subject": subject,
        "lesson_id": "math_difficult_lesson",
        "feedback_type": "difficulty",
        "rating": 2,  # Low rating
        "difficulty_rating": 2,  # Found too difficult
        "feedback_text": "This lesson was too hard for my level",
        "suggestions": ["Provide more examples", "Slow down explanations"],
        "timestamp": datetime.now().isoformat()
    }
    
    feedback_response = client.post("/feedback/submit", json=feedback_request)
    assert feedback_response.status_code == 200
    
    feedback_id = feedback_response.json()["feedback_id"]
    assert feedback_id
    
    # 2. Process the feedback for adjustment
    adjustment_response = client.post(f"/feedback/process-adjustment/{user_id}/{subject}")
    assert adjustment_response.status_code == 200
    
    adjustment_result = adjustment_response.json()
    assert adjustment_result["user_id"] == user_id
    assert adjustment_result["subject"] == subject
    assert "success" in adjustment_result


def test_curriculum_feedback_integration():
    """Test curriculum-specific feedback submission and processing."""
    user_id = "curriculum_feedback_user"
    curriculum_id = "math_algebra_track"
    
    # 1. Submit curriculum feedback
    curriculum_feedback_request = {
        "user_id": user_id,
        "curriculum_id": curriculum_id,
        "learning_path": "newbie",
        "overall_satisfaction": 3,  # Average
        "pacing_feedback": 2,  # Too fast
        "content_relevance": 4,  # Good
        "effectiveness": 3,  # Okay
        "feedback_text": "The pacing is too quick for beginners",
        "suggested_improvements": ["Slow down the pacing", "Add more practice modules"],
        "completed_modules": 3,
        "total_modules": 10,
        "timestamp": datetime.now().isoformat()
    }
    
    response = client.post("/feedback/curriculum", json=curriculum_feedback_request)
    assert response.status_code == 200
    
    result = response.json()
    assert "feedback_id" in result
    assert result["user_id"] == user_id


def test_feedback_analytics_and_recommendations():
    """Test that feedback analytics influence recommendations."""
    user_id = "analytics_test_user"
    subject = "Science"
    
    # Submit multiple feedback entries with different ratings
    feedback_entries = [
        {
            "user_id": user_id,
            "subject": subject,
            "lesson_id": f"science_lesson_{i}",
            "feedback_type": "lesson",
            "rating": 2 if i < 3 else 4,  # First 3 are low, next 2 are high
            "feedback_text": f"Feedback for lesson {i}",
            "timestamp": datetime.now().isoformat()
        }
        for i in range(5)
    ]
    
    for feedback in feedback_entries:
        response = client.post("/feedback/submit", json=feedback)
        assert response.status_code == 200
    
    # Get feedback analytics
    analytics_response = client.get(f"/feedback/{subject}/analytics")
    assert analytics_response.status_code == 200
    
    analytics_data = analytics_response.json()
    assert analytics_data["subject"] == subject
    assert "average_rating" in analytics_data
    assert "total_feedback" in analytics_data
    assert "rating_distribution" in analytics_data
    
    # Process adjustment based on collected feedback
    adjustment_response = client.post(f"/feedback/process-adjustment/{user_id}/{subject}")
    assert adjustment_response.status_code == 200


def test_negative_feedback_triggers_intervention():
    """Test that consistently negative feedback triggers interventions."""
    user_id = "intervention_test_user"
    subject = "Programming"
    
    # Submit several negative feedback entries
    for i in range(4):  # More than threshold to trigger intervention
        feedback_request = {
            "user_id": user_id,
            "subject": subject,
            "lesson_id": f"prog_lesson_{i}",
            "feedback_type": "lesson",
            "rating": 1,  # Very low rating
            "content_rating": 2,
            "difficulty_rating": 1,  # Too difficult
            "feedback_text": f"I'm struggling with lesson {i}",
            "suggestions": ["Need more basic content"],
            "timestamp": datetime.now().isoformat()
        }
        
        response = client.post("/feedback/submit", json=feedback_request)
        assert response.status_code == 200
    
    # Check that analytics reflect the negative feedback
    analytics_response = client.get(f"/feedback/{subject}/analytics")
    assert analytics_response.status_code == 200
    
    analytics_data = analytics_response.json()
    assert analytics_data["average_rating"] < 2.5  # Should be low due to negative feedback
    
    # Process adjustment
    adjustment_response = client.post(f"/feedback/process-adjustment/{user_id}/{subject}")
    assert adjustment_response.status_code == 200
    
    adjustment_data = adjustment_response.json()
    assert adjustment_data["success"] is True


def test_positive_feedback_acceleration():
    """Test that consistently positive feedback may trigger acceleration."""
    user_id = "acceleration_test_user"
    subject = "History"
    
    # Submit several positive feedback entries
    for i in range(5):
        feedback_request = {
            "user_id": user_id,
            "subject": subject,
            "lesson_id": f"history_lesson_{i}",
            "feedback_type": "lesson",
            "rating": 5,  # High rating
            "content_rating": 5,
            "difficulty_rating": 4,  # Appropriate difficulty
            "feedback_text": f"Lesson {i} was excellent",
            "would_recommend": True,
            "timestamp": datetime.now().isoformat()
        }
        
        response = client.post("/feedback/submit", json=feedback_request)
        assert response.status_code == 200
    
    # Check analytics
    analytics_response = client.get(f"/feedback/{subject}/analytics")
    assert analytics_response.status_code == 200
    
    analytics_data = analytics_response.json()
    assert analytics_data["average_rating"] > 4.0  # Should be high due to positive feedback
    
    # Process adjustment
    adjustment_response = client.post(f"/feedback/process-adjustment/{user_id}/{subject}")
    assert adjustment_response.status_code == 200


def test_user_feedback_history_integration():
    """Test that feedback history is properly maintained and accessible."""
    user_id = "history_integration_user"
    
    # Submit various types of feedback
    feedback_types = ["lesson", "tutor", "content", "difficulty"]
    
    for i, fb_type in enumerate(feedback_types):
        feedback_request = {
            "user_id": user_id,
            "subject": "SampleSubject",
            "lesson_id": f"lesson_{i}",
            "feedback_type": fb_type,
            "rating": 4 if i % 2 == 0 else 3,  # Alternating ratings
            "feedback_text": f"Feedback for {fb_type}",
            "timestamp": datetime.now().isoformat()
        }
        
        response = client.post("/feedback/submit", json=feedback_request)
        assert response.status_code == 200
    
    # Get user feedback history
    history_response = client.get(f"/feedback/user/{user_id}")
    assert history_response.status_code == 200
    
    history_data = history_response.json()
    assert isinstance(history_data, list)
    assert len(history_data) >= len(feedback_types)
    
    # Verify each feedback type is represented
    feedback_types_received = [fb["feedback_type"] for fb in history_data]
    for fb_type in feedback_types:
        assert fb_type in feedback_types_received