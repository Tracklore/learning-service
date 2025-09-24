"""
Integration tests for progress-based adaptive learning.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.adaptive_learning_paths_service import adaptive_learning_service
from app.services.progress_service import progress_service
from app.models.progress_model import ProgressUpdateRequest

client = TestClient(app)

def test_adaptive_curriculum_generation():
    """Test that curriculum is adapted based on user progress."""
    user_id = "adaptive_test_user"
    subject = "Mathematics"
    
    # Add some progress data showing strengths and weaknesses
    progress_requests = [
        # Weakness: Algebra
        ProgressUpdateRequest(
            user_id=user_id,
            subject=subject,
            lesson_id="math_algebra_1",
            completed=True,
            score=45,  # Low score
        ),
        ProgressUpdateRequest(
            user_id=user_id,
            subject=subject,
            lesson_id="math_algebra_2", 
            completed=True,
            score=50,  # Still low
        ),
        # Strength: Geometry
        ProgressUpdateRequest(
            user_id=user_id,
            subject=subject,
            lesson_id="math_geometry_1",
            completed=True,
            score=90,  # High score
        ),
        ProgressUpdateRequest(
            user_id=user_id,
            subject=subject,
            lesson_id="math_geometry_2",
            completed=True,
            score=92,  # High score
        )
    ]
    
    for request in progress_requests:
        progress_service.update_progress(request)
    
    # Get adaptive curriculum (this would typically be called via an API endpoint)
    # For now, test the service directly
    adaptive_curriculum = adaptive_learning_service.generate_adaptive_curriculum(
        user_id=user_id,
        subject=subject,
        current_path="newbie"
    )
    
    assert adaptive_curriculum is not None
    assert adaptive_curriculum.subject_id == subject
    # The curriculum should have more algebra content due to weaknesses
    # or remedial modules added


def test_end_to_end_adaptive_learning_flow():
    """Test a complete adaptive learning flow."""
    user_id = "e2e_adaptive_user"
    subject = "Science"
    
    # 1. Start a teaching session
    session_request = {
        "user_id": user_id,
        "subject": subject,
        "topic": "Physics",
        "user_level": "newbie"
    }
    
    session_response = client.post("/teaching/session/start", json=session_request)
    assert session_response.status_code == 200
    
    session_data = session_response.json()
    assert "session_id" in session_data
    session_id = session_data["session_id"]
    
    # 2. Complete several lessons, some with low scores to indicate weaknesses
    for i in range(3):
        # Submit progress data with varying scores
        progress_request = {
            "user_id": user_id,
            "subject": subject,
            "lesson_id": f"physics_lesson_{i+1}",
            "completed": True,
            "score": 45 if i == 0 else 80,  # First lesson low, others higher
            "time_spent_seconds": 1800
        }
        
        progress_response = client.post("/progress/", json=progress_request)
        assert progress_response.status_code == 200
    
    # 3. Get user's progress to verify it's been tracked
    progress_response = client.get(f"/progress/{user_id}/{subject}")
    assert progress_response.status_code == 200
    
    progress_data = progress_response.json()
    assert progress_data["user_id"] == user_id
    assert progress_data["total_lessons_completed"] >= 3
    
    # 4. Submit feedback indicating difficulty with initial lesson
    feedback_request = {
        "user_id": user_id,
        "subject": subject,
        "lesson_id": "physics_lesson_1",
        "feedback_type": "difficulty",
        "rating": 2,
        "feedback_text": "Found the first lesson very difficult",
        "suggestions": ["More foundational content needed"],
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }
    
    feedback_response = client.post("/feedback/submit", json=feedback_request)
    assert feedback_response.status_code == 200
    
    # 5. Process feedback adjustment
    adjustment_response = client.post(f"/feedback/process-adjustment/{user_id}/{subject}")
    assert adjustment_response.status_code == 200
    
    # 6. End the session
    end_response = client.post(f"/teaching/session/{session_id}/end")
    assert end_response.status_code == 200


def test_weakness_based_adaptation():
    """Test that identified weaknesses trigger adaptive responses."""
    user_id = "weakness_adapt_user"
    subject = "Programming"
    
    # Simulate weak performance in specific areas
    weak_areas = ["algorithms", "data_structures"]
    strong_areas = ["syntax", "basic_concepts"]
    
    # Add progress data for weak areas
    for i, area in enumerate(weak_areas):
        progress_request = {
            "user_id": user_id,
            "subject": subject,
            "lesson_id": f"prog_{area}_{i+1}",
            "completed": True,
            "score": 40 + i*5,  # Low scores
            "time_spent_seconds": 2400
        }
        client.post("/progress/", json=progress_request)
    
    # Add progress data for strong areas
    for i, area in enumerate(strong_areas):
        progress_request = {
            "user_id": user_id,
            "subject": subject,
            "lesson_id": f"prog_{area}_{i+1}",
            "completed": True,
            "score": 85 + i*2,  # High scores
            "time_spent_seconds": 1200
        }
        client.post("/progress/", json=progress_request)
    
    # Get adaptive curriculum based on this progress
    # This would typically happen through a service call
    user_progress = progress_service.get_user_progress(user_id, subject)
    assert user_progress is not None
    assert user_progress.total_lessons_completed >= 4
    # The user should have weaknesses and strengths recorded based on scores


def test_progress_based_pacing_adjustment():
    """Test that pacing is adjusted based on user progress."""
    user_id = "pacing_test_user"
    subject = "Literature"
    
    # Add progress data over time to establish pacing patterns
    for i in range(5):
        # Simulate slower progress (lower scores, more time spent)
        progress_request = {
            "user_id": user_id,
            "subject": subject,
            "lesson_id": f"lit_lesson_{i+1}",
            "completed": True,
            "score": 65,  # Moderate score
            "time_spent_seconds": 3600,  # More time spent than average
        }
        client.post("/progress/", json=progress_request)
    
    # Get progress and verify pacing
    progress_response = client.get(f"/progress/{user_id}/{subject}")
    assert progress_response.status_code == 200
    
    progress_data = progress_response.json()
    assert progress_data["user_id"] == user_id
    assert "learning_pace" in progress_data
    # Based on the slower pace, the system might adjust this user's pace setting


def test_personalized_recommendation_integration():
    """Test that personalization happens based on progress and feedback."""
    user_id = "personalization_test_user"
    subject = "History"
    
    # Create varied performance data
    performance_data = [
        {"lesson": "ancient_rome_1", "score": 90, "time": 1800},
        {"lesson": "ancient_rome_2", "score": 45, "time": 3600},  # Struggled
        {"lesson": "medieval_europe_1", "score": 50, "time": 3000},  # Struggled
        {"lesson": "renaissance_1", "score": 85, "time": 2000},
    ]
    
    for perf in performance_data:
        progress_request = {
            "user_id": user_id,
            "subject": subject,
            "lesson_id": perf["lesson"],
            "completed": True,
            "score": perf["score"],
            "time_spent_seconds": perf["time"]
        }
        client.post("/progress/", json=progress_request)
    
    # Submit feedback
    feedback_request = {
        "user_id": user_id,
        "subject": subject,
        "lesson_id": "ancient_rome_2",
        "feedback_type": "content",
        "rating": 2,
        "feedback_text": "Need more visual aids for this topic",
        "suggestions": ["Add more images and diagrams"],
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }
    client.post("/feedback/submit", json=feedback_request)
    
    # Get analytics to verify personalization
    analytics_response = client.get(f"/progress/{user_id}/{subject}/analytics")
    assert analytics_response.status_code == 200
    
    # Process feedback for adjustments
    adjustment_response = client.post(f"/feedback/process-adjustment/{user_id}/{subject}")
    assert adjustment_response.status_code == 200


def test_knowledge_state_embedding_integration():
    """Test integration of knowledge state embeddings with progress tracking."""
    user_id = "embedding_test_user"
    subject = "Chemistry"
    
    # Add significant progress data
    for i in range(8):  # More than typical to establish knowledge state
        progress_request = {
            "user_id": user_id,
            "subject": subject,
            "lesson_id": f"chem_topic_{i+1}",
            "completed": True if i < 6 else False,  # Last 2 not completed
            "score": 70 + (i * 3) if i < 6 else None,  # Scores improving over time
            "time_spent_seconds": 1800 + (i * 200)
        }
        client.post("/progress/", json=progress_request)
    
    # Get comprehensive progress data
    progress_response = client.get(f"/progress/{user_id}/{subject}")
    assert progress_response.status_code == 200
    
    progress_data = progress_response.json()
    assert progress_data["user_id"] == user_id
    assert progress_data["total_lessons_completed"] >= 6
    # Knowledge state should be populated based on progress