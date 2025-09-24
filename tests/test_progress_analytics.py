"""
Unit tests for progress analytics functions.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.services.progress_service import progress_service
from app.models.progress_model import ProgressUpdateRequest
from app.llm.progress_analytics_llm import progress_analytics_llm

def test_basic_progress_analytics():
    """Test basic progress analytics functionality."""
    user_id = "test_analytics_user"
    subject = "Mathematics"
    
    # Add some progress data
    progress_requests = [
        ProgressUpdateRequest(
            user_id=user_id,
            subject=subject,
            lesson_id="math_lesson_1",
            completed=True,
            score=85.0,
            time_spent_seconds=1800
        ),
        ProgressUpdateRequest(
            user_id=user_id,
            subject=subject,
            lesson_id="math_lesson_2",
            completed=True,
            score=92.0,
            time_spent_seconds=2400
        ),
        ProgressUpdateRequest(
            user_id=user_id,
            subject=subject,
            lesson_id="math_lesson_3",
            completed=False,  # Not completed
            score=None,
            time_spent_seconds=1200
        )
    ]
    
    for request in progress_requests:
        progress_service.update_progress(request)
    
    # Get analytics
    analytics = progress_service.get_progress_analytics(user_id, subject)
    
    assert analytics is not None
    assert analytics.user_id == user_id
    assert analytics.subject == subject
    assert analytics.learning_velocity > 0
    assert isinstance(analytics.accuracy_trend, list)
    assert isinstance(analytics.weak_areas, list)
    assert isinstance(analytics.strong_areas, list)


def test_advanced_analytics():
    """Test advanced analytics using LLM."""
    user_id = "test_advanced_analytics_user"
    subject = "Physics"
    
    # Add some progress data
    progress_requests = [
        ProgressUpdateRequest(
            user_id=user_id,
            subject=subject,
            lesson_id="physics_kinematics_1",
            completed=True,
            score=78.0
        ),
        ProgressUpdateRequest(
            user_id=user_id,
            subject=subject,
            lesson_id="physics_dynamics_1",
            completed=True,
            score=89.0
        )
    ]
    
    for request in progress_requests:
        progress_service.update_progress(request)
    
    # Get advanced analytics (this uses the LLM)
    advanced_analytics = progress_service.get_advanced_analytics(user_id, subject)
    
    assert advanced_analytics is not None
    assert advanced_analytics["user_id"] == user_id
    assert advanced_analytics["subject"] == subject
    assert "learning_patterns" in advanced_analytics
    assert "recommendations" in advanced_analytics


def test_personalized_insights():
    """Test personalized insights using LLM."""
    user_id = "test_insights_user"
    subject = "Chemistry"
    
    # Add some progress data
    progress_request = ProgressUpdateRequest(
        user_id=user_id,
        subject=subject,
        lesson_id="chem_basics_1",
        completed=True,
        score=82.0
    )
    progress_service.update_progress(progress_request)
    
    # Get personalized insights (this uses the LLM)
    insights = progress_service.get_personalized_insights(user_id, subject)
    
    assert insights is not None
    assert insights["user_id"] == user_id
    assert insights["subject"] == subject
    assert "insights" in insights
    assert "study_tips" in insights
    assert "motivational_message" in insights


def test_progress_analytics_with_mocked_llm():
    """Test progress analytics with mocked LLM."""
    with patch.object(progress_analytics_llm, 'model', None):
        user_id = "test_mocked_analytics_user"
        subject = "Biology"
        
        # Add some progress data
        progress_request = ProgressUpdateRequest(
            user_id=user_id,
            subject=subject,
            lesson_id="bio_cells_1",
            completed=True,
            score=90.0
        )
        progress_service.update_progress(progress_request)
        
        # Get advanced analytics (should use mock data)
        advanced_analytics = progress_service.get_advanced_analytics(user_id, subject)
        
        assert advanced_analytics is not None
        assert advanced_analytics["user_id"] == user_id
        # Mock data should have default values
        assert advanced_analytics["learning_patterns"]["pace"] == "moderate"


def test_empty_progress_analytics():
    """Test analytics for user with no progress data."""
    user_id = "test_empty_analytics_user"
    subject = "NonExistentSubject"
    
    # Try to get analytics for non-existent data
    analytics = progress_service.get_progress_analytics(user_id, subject)
    
    # Should return None or handle gracefully
    # This behavior depends on the implementation
    # In our case, it should return None since there's no data
    assert analytics is None