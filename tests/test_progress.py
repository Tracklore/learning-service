"""
Unit tests for progress tracking endpoints and service functionality.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.progress_service import progress_service
from app.models.progress_model import ProgressUpdateRequest

client = TestClient(app)

def test_update_user_progress():
    """Test updating user progress."""
    # Prepare request data
    request_data = {
        "user_id": "test_user_progress",
        "subject": "Mathematics",
        "lesson_id": "math_basic_algebra_1",
        "completed": True,
        "score": 85.0,
        "time_spent_seconds": 1800,
        "notes": "Completed basic algebra lesson"
    }
    
    response = client.post("/progress/", json=request_data)
    assert response.status_code == 200
    
    result = response.json()
    assert result["user_id"] == request_data["user_id"]
    assert result["subject"] == request_data["subject"]
    assert result["total_lessons_completed"] >= 0
    assert "message" in result


def test_get_user_progress():
    """Test getting a user's progress for a specific subject."""
    user_id = "test_user_get_progress"
    subject = "Science"
    
    # First, update progress to ensure data exists
    update_request = {
        "user_id": user_id,
        "subject": subject,
        "lesson_id": "science_basic_physics_1",
        "completed": True,
        "score": 90.0
    }
    client.post("/progress/", json=update_request)
    
    # Now get the progress
    response = client.get(f"/progress/{user_id}/{subject}")
    assert response.status_code == 200
    
    result = response.json()
    assert result["user_id"] == user_id
    assert result["subject"] == subject
    assert result["total_lessons_completed"] >= 0


def test_get_progress_analytics():
    """Test getting detailed analytics for a user's progress."""
    user_id = "test_user_analytics"
    subject = "History"
    
    # First, update progress to ensure data exists
    update_request = {
        "user_id": user_id,
        "subject": subject,
        "lesson_id": "history_world_war_1",
        "completed": True,
        "score": 75.0
    }
    client.post("/progress/", json=update_request)
    
    # Now get the analytics
    response = client.get(f"/progress/{user_id}/{subject}/analytics")
    assert response.status_code == 200
    
    result = response.json()
    assert result["user_id"] == user_id
    assert result["subject"] == subject
    assert "learning_velocity" in result
    assert "accuracy_trend" in result


def test_reset_user_progress():
    """Test resetting a user's progress for a specific subject."""
    user_id = "test_user_reset"
    subject = "Literature"
    
    # First, update progress to ensure data exists
    update_request = {
        "user_id": user_id,
        "subject": subject,
        "lesson_id": "literature_shakespeare_1",
        "completed": True,
        "score": 80.0
    }
    client.post("/progress/", json=update_request)
    
    # Verify progress exists
    get_response = client.get(f"/progress/{user_id}/{subject}")
    assert get_response.status_code == 200
    
    # Now reset the progress
    response = client.delete(f"/progress/{user_id}/{subject}")
    assert response.status_code == 200
    
    result = response.json()
    assert result["user_id"] == user_id
    assert result["subject"] == subject
    assert result["reset"] is True


def test_get_nonexistent_user_progress():
    """Test getting progress for a user that doesn't exist."""
    response = client.get("/progress/nonexistent_user/nonexistent_subject")
    assert response.status_code == 404


def test_service_update_progress():
    """Test the service method for updating progress directly."""
    request = ProgressUpdateRequest(
        user_id="test_service_user",
        subject="Geography",
        lesson_id="geography_continents_1",
        completed=True,
        score=95.0,
        time_spent_seconds=2700
    )
    
    updated_progress = progress_service.update_progress(request)
    
    assert updated_progress.user_id == request.user_id
    assert updated_progress.subject == request.subject
    assert updated_progress.total_lessons_completed >= 0


def test_service_get_user_progress():
    """Test the service method for getting user progress."""
    # First, add some progress data
    request = ProgressUpdateRequest(
        user_id="test_get_service_user",
        subject="Art",
        lesson_id="art_basic_color_1",
        completed=True,
        score=88.0
    )
    progress_service.update_progress(request)
    
    # Get the progress
    user_progress = progress_service.get_user_progress("test_get_service_user", "Art")
    
    assert user_progress is not None
    assert user_progress.user_id == "test_get_service_user"
    assert user_progress.subject == "Art"
    assert user_progress.total_lessons_completed >= 0