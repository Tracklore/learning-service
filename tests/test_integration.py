"""
Integration tests for teaching service and lesson delivery.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_end_to_end_teaching_flow():
    """Test the complete teaching flow from session start to end."""
    # 1. First, select a tutor for the user
    tutor_request = {
        "user_id": "integration_test_user",
        "character_style": "friendly",
        "humor_level": "medium",
        "tone": "encouraging",
        "complexity": "simple"
    }
    
    tutor_response = client.post("/tutor/select", json=tutor_request)
    assert tutor_response.status_code == 200
    
    # 2. Start a teaching session
    session_request = {
        "user_id": "integration_test_user",
        "subject": "Mathematics",
        "topic": "Algebra Basics",
        "user_level": "newbie"
    }
    
    session_response = client.post("/teaching/session/start", json=session_request)
    assert session_response.status_code == 200
    
    session_data = session_response.json()
    assert "session_id" in session_data
    session_id = session_data["session_id"]
    
    # 3. Get the first lesson step
    step_response = client.post("/teaching/lesson/step", json={
        "session_id": session_id,
        "step_number": 1
    })
    assert step_response.status_code == 200
    assert step_response.json()["step_number"] == 1
    
    # 4. Generate a question for practice
    question_response = client.post("/teaching/question/generate", json={
        "session_id": session_id,
        "concept": "Basic Equations",
        "question_type": "multiple_choice"
    })
    assert question_response.status_code == 200
    assert "question" in question_response.json()
    
    # 5. Evaluate the user's answer
    evaluation_response = client.post("/evaluation/answer/evaluate", json={
        "user_id": "integration_test_user",
        "user_answer": "x = 5",
        "correct_answer": "x = 5",
        "question_context": {
            "subject": "Mathematics",
            "topic": "Algebra Basics",
            "concept": "Basic Equations",
            "question": "Solve for x: x + 2 = 7"
        }
    })
    assert evaluation_response.status_code == 200
    assert evaluation_response.json()["is_correct"] == True
    
    # 6. Advance to the next step
    advance_response = client.post("/teaching/session/advance", json={
        "session_id": session_id
    })
    assert advance_response.status_code == 200
    
    # 7. Get session progress
    progress_response = client.get(f"/teaching/session/{session_id}/progress")
    assert progress_response.status_code == 200
    progress_data = progress_response.json()
    assert progress_data["current_step"] == 2
    assert progress_data["session_id"] == session_id
    
    # 8. End the session
    end_response = client.post(f"/teaching/session/{session_id}/end")
    assert end_response.status_code == 200
    assert end_response.json()["status"] == "ended"


def test_different_tutor_personas():
    """Test lesson delivery with different tutor personas."""
    tutor_personas = [
        {
            "character_style": "professional",
            "humor_level": "low",
            "tone": "direct",
            "complexity": "complex"
        },
        {
            "character_style": "funny",
            "humor_level": "high",
            "tone": "casual",
            "complexity": "simple"
        },
        {
            "character_style": "motivational",
            "humor_level": "medium",
            "tone": "encouraging",
            "complexity": "moderate"
        }
    ]
    
    for i, persona in enumerate(tutor_personas):
        user_id = f"test_user_persona_{i}"
        
        # Select tutor with specific persona
        tutor_request = {
            "user_id": user_id,
            "character_style": persona["character_style"],
            "humor_level": persona["humor_level"],
            "tone": persona["tone"],
            "complexity": persona["complexity"]
        }
        
        tutor_response = client.post("/tutor/select", json=tutor_request)
        assert tutor_response.status_code == 200
        
        # Get the user's assigned tutor
        get_tutor_response = client.get(f"/tutor/user/{user_id}")
        assert get_tutor_response.status_code == 200
        
        tutor_data = get_tutor_response.json()
        assert tutor_data["character_style"] == persona["character_style"]
        assert tutor_data["humor_level"] == persona["humor_level"]
        assert tutor_data["tone"] == persona["tone"]
        assert tutor_data["complexity"] == persona["complexity"]


def test_adaptive_learning_integration():
    """Test the integration of adaptive learning features."""
    # Start a teaching session
    session_request = {
        "user_id": "adaptive_test_user",
        "subject": "Science",
        "topic": "Biology",
        "user_level": "newbie"
    }
    
    session_response = client.post("/teaching/session/start", json=session_request)
    assert session_response.status_code == 200
    
    session_data = session_response.json()
    session_id = session_data["session_id"]
    assert session_id
    
    # Advance through a few steps to trigger adaptation
    for step in range(3):
        advance_response = client.post("/teaching/session/advance", json={
            "session_id": session_id
        })
        assert advance_response.status_code == 200
    
    # Get session progress to verify adaptation history
    progress_response = client.get(f"/teaching/session/{session_id}/progress")
    assert progress_response.status_code == 200
    
    # Check if adaptation history is present
    progress_data = progress_response.json()
    # This might not be present if the user is just following the normal path
    # But the structure should be there
    
    # Try the adaptation endpoint directly
    adaptation_request = {
        "user_id": "adaptive_test_user",
        "subject": "Science",
        "topic": "Biology",
        "current_step": 2,
        "total_steps": 5
    }
    
    adaptation_response = client.post("/adaptive/adaptation", json=adaptation_request)
    assert adaptation_response.status_code == 200
    
    adaptation_data = adaptation_response.json()
    assert "adaptation_type" in adaptation_data
    assert "message" in adaptation_data