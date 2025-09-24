"""
Tests for mocking LLM calls to ensure consistent testing.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.services.progress_service import progress_service
from app.services.evaluation_service import evaluation_service
from app.services.adaptive_learning_service import adaptive_learning_service
from app.models.progress_model import ProgressUpdateRequest
from app.models.feedback_model import FeedbackSubmission
from datetime import datetime

def test_mock_teaching_llm_in_progress_tracking():
    """Test progress tracking with mocked teaching LLM."""
    with patch('app.services.teaching_service.teaching_llm') as mock_teaching_llm:
        # Configure the mock
        mock_teaching_llm.deliver_lesson_step.return_value = {
            "step_number": 1,
            "total_steps": 5,
            "title": "Mock Lesson Title",
            "content": "This is mocked lesson content",
            "examples": ["Example 1"],
            "key_points": ["Key point 1"],
            "estimated_time_min": 10,
            "next_step_preview": "Preview of next step"
        }
        
        # Test progress tracking still works when LLM is mocked
        user_id = "test_mock_user"
        subject = "MockSubject"
        
        progress_request = ProgressUpdateRequest(
            user_id=user_id,
            subject=subject,
            lesson_id="mock_lesson_1",
            completed=True,
            score=85.0,
            time_spent_seconds=1800
        )
        
        updated_progress = progress_service.update_progress(progress_request)
        
        assert updated_progress.user_id == user_id
        assert updated_progress.total_lessons_completed >= 0


def test_mock_progress_analytics_llm():
    """Test progress analytics with mocked LLM."""
    with patch('app.llm.progress_analytics_llm.progress_analytics_llm') as mock_analytics_llm:
        # Configure the mock
        mock_analytics_llm.analyze_learning_patterns.return_value = {
            "user_id": "test_user",
            "subject": "Math",
            "learning_patterns": {
                "pace": "moderate",
                "consistency": "high",
                "strengths": ["algebra", "geometry"],
                "improvement_areas": ["calculus"],
                "study_habits": ["night owl"]
            },
            "recommendations": ["Practice more problems"],
            "risk_factors": [],
            "motivational_insights": ["You're doing great!"]
        }
        
        # Add some progress data to trigger analytics
        user_id = "test_mock_analytics"
        subject = "Mathematics"
        
        progress_requests = [
            ProgressUpdateRequest(
                user_id=user_id,
                subject=subject,
                lesson_id="math_lesson_1",
                completed=True,
                score=80.0
            ),
            ProgressUpdateRequest(
                user_id=user_id,
                subject=subject,
                lesson_id="math_lesson_2",
                completed=True,
                score=90.0
            )
        ]
        
        for request in progress_requests:
            progress_service.update_progress(request)
        
        # Get advanced analytics (should use mocked LLM)
        advanced_analytics = progress_service.get_advanced_analytics(user_id, subject)
        
        assert advanced_analytics is not None
        assert advanced_analytics["user_id"] == "test_user"  # From mock
        assert advanced_analytics["subject"] == "Math"  # From mock


def test_mock_tutor_persona_in_evaluation():
    """Test evaluation service with mocked LLM."""
    with patch('app.services.evaluation_service.teaching_llm') as mock_teaching_llm:
        # Configure the mock
        mock_teaching_llm.update_lesson_complexity.return_value = {
            "subject": "Science",
            "topic": "Physics",
            "concept": "Motion",
            "complexity_adjustment": "Simplified for beginner",
            "content": "Simplified content for beginners",
            "recommendation": "Focus on basic concepts first"
        }
        
        # Test that evaluation service works with mocked LLM
        result = evaluation_service.adjust_complexity(
            user_id="test_user",
            subject="Science",
            topic="Physics"
        )
        
        assert "complexity_level" in result
        assert "message" in result


def test_mock_curriculum_generation_with_progress():
    """Test curriculum generation with mocked LLM but real progress data."""
    # Add real progress data
    user_id = "test_mock_curriculum"
    subject = "Programming"
    
    progress_requests = [
        ProgressUpdateRequest(
            user_id=user_id,
            subject=subject,
            lesson_id="prog_basics_1",
            completed=True,
            score=75.0
        ),
        ProgressUpdateRequest(
            user_id=user_id,
            subject=subject,
            lesson_id="prog_intermediate_1",
            completed=True,
            score=60.0  # Lower score indicating difficulty
        )
    ]
    
    for request in progress_requests:
        progress_service.update_progress(request)
    
    # Test that progress data exists and can be retrieved
    user_progress = progress_service.get_user_progress(user_id, subject)
    assert user_progress is not None
    assert user_progress.total_lessons_completed == 2
    assert user_progress.overall_score is not None


def test_mock_feedback_processing_with_llm():
    """Test feedback processing with mocked LLM components."""
    with patch('app.llm.progress_analytics_llm.progress_analytics_llm') as mock_analytics_llm:
        # Configure the mock
        mock_analytics_llm.analyze_learning_patterns.return_value = {
            "user_id": "test_user",
            "subject": "History",
            "learning_patterns": {
                "pace": "slow",
                "consistency": "medium",
                "strengths": [],
                "improvement_areas": ["dates", "chronology"],
                "study_habits": ["cramming before tests"]
            },
            "recommendations": ["Study in smaller chunks"],
            "risk_factors": ["Poor time management"],
            "motivational_insights": ["You can improve with better planning!"]
        }
        
        # Submit real feedback
        feedback = FeedbackSubmission(
            user_id="test_mock_feedback",
            subject="History",
            lesson_id="history_us_1",
            feedback_type="lesson",
            rating=3,  # Below average
            feedback_text="Found this lesson difficult to follow",
            timestamp=datetime.now()
        )
        response = feedback_service.submit_feedback(feedback)
        
        assert response.user_id == feedback.user_id