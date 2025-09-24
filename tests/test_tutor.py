"""
Unit tests for tutor endpoints and service functionality.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.tutor_service import tutor_service
from app.models.tutor_model import TutorPersona

client = TestClient(app)

def test_list_tutors():
    """Test the list tutors endpoint."""
    response = client.get("/tutor/")
    assert response.status_code == 200
    
    tutors = response.json()
    assert isinstance(tutors, list)
    assert len(tutors) > 0  # Should have default tutors
    
    # Verify tutors have required fields
    for tutor in tutors:
        assert "tutor_id" in tutor
        assert "name" in tutor
        assert "character_style" in tutor
        assert "humor_level" in tutor
        assert "tone" in tutor
        assert "complexity" in tutor


def test_get_tutor_by_id():
    """Test getting a specific tutor by ID."""
    # Use the first available tutor ID
    all_tutors_response = client.get("/tutor/")
    tutors = all_tutors_response.json()
    tutor_id = tutors[0]["tutor_id"]
    
    response = client.get(f"/tutor/{tutor_id}")
    assert response.status_code == 200
    
    tutor = response.json()
    assert tutor["tutor_id"] == tutor_id


def test_get_nonexistent_tutor():
    """Test getting a tutor that doesn't exist."""
    response = client.get("/tutor/nonexistent_tutor")
    assert response.status_code == 404


def test_select_tutor():
    """Test selecting a tutor for a user."""
    # Prepare request data
    request_data = {
        "user_id": "test_user_123",
        "character_style": "friendly",
        "humor_level": "medium",
        "tone": "encouraging",
        "complexity": "simple"
    }
    
    response = client.post("/tutor/select", json=request_data)
    assert response.status_code == 200
    
    result = response.json()
    assert "tutor" in result
    assert "message" in result
    assert request_data["user_id"] in result["message"]


def test_select_tutor_without_preferences():
    """Test selecting a tutor without specific preferences."""
    request_data = {
        "user_id": "test_user_456"
        # No preferences specified
    }
    
    response = client.post("/tutor/select", json=request_data)
    assert response.status_code == 200
    
    result = response.json()
    assert "tutor" in result
    assert "message" in result


def test_get_user_tutor():
    """Test getting the tutor assigned to a user."""
    user_id = "test_user_789"
    
    # First, assign a tutor to the user
    request_data = {
        "user_id": user_id,
        "character_style": "professional"
    }
    select_response = client.post("/tutor/select", json=request_data)
    assert select_response.status_code == 200
    
    # Now get the assigned tutor
    response = client.get(f"/tutor/user/{user_id}")
    assert response.status_code == 200
    
    tutor = response.json()
    assert "tutor_id" in tutor
    assert tutor["character_style"] == "professional"


def test_get_user_tutor_no_assignment():
    """Test getting a tutor for a user that has none assigned."""
    response = client.get("/tutor/user/nonexistent_user")
    assert response.status_code == 404


def test_service_get_all_tutors():
    """Test the service method for getting all tutors."""
    tutors = tutor_service.get_all_tutors()
    assert isinstance(tutors, list)
    assert len(tutors) > 0
    
    for tutor in tutors:
        assert isinstance(tutor, TutorPersona)


def test_service_get_tutor_by_id():
    """Test the service method for getting a tutor by ID."""
    tutor_id = "friendly_alice"
    tutor = tutor_service.get_tutor_by_id(tutor_id)
    
    assert tutor is not None
    assert tutor.tutor_id == tutor_id
    assert tutor.name == "Friendly Alice"


def test_service_select_tutor_for_user():
    """Test the service method for selecting a tutor for a user."""
    from app.models.tutor_model import TutorSelectionRequest
    
    request = TutorSelectionRequest(
        user_id="test_user_service",
        character_style="friendly"
    )
    
    selected_tutor = tutor_service.select_tutor_for_user(request)
    
    assert selected_tutor is not None
    assert selected_tutor.character_style == "friendly"
    
    # Verify the preference was saved
    user_pref = tutor_service.get_user_tutor_preference("test_user_service")
    assert user_pref is not None
    assert user_pref.user_id == "test_user_service"
    assert user_pref.tutor_id == selected_tutor.tutor_id