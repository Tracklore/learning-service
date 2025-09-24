"""
Unit tests for teaching LLM functions.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.llm.teaching_llm import TeachingLLM, teaching_llm
from app.services.evaluation_service import evaluation_service


def test_teaching_llm_initialization():
    """Test the initialization of the TeachingLLM class."""
    llm = TeachingLLM()
    # The model might be None if GEMINI_API_KEY is not set, which is acceptable for testing
    assert hasattr(llm, 'model')


def test_deliver_lesson_step_with_mocked_llm():
    """Test delivering a lesson step with mocked LLM."""
    with patch.object(teaching_llm, 'model', None):
        result = teaching_llm.deliver_lesson_step(
            subject="Math",
            topic="Algebra",
            step_number=1,
            total_steps=5,
            user_level="newbie",
            tutor_persona={
                "character_style": "friendly",
                "humor_level": "medium",
                "tone": "encouraging",
                "complexity": "simple"
            }
        )
        
        # Should return mock data when model is None
        assert "step_number" in result
        assert result["step_number"] == 1
        assert "total_steps" in result
        assert result["total_steps"] == 5
        assert "content" in result


def test_generate_interactive_question_with_mocked_llm():
    """Test generating an interactive question with mocked LLM."""
    with patch.object(teaching_llm, 'model', None):
        result = teaching_llm.generate_interactive_question(
            subject="Math",
            topic="Algebra",
            concept="Linear Equations",
            question_type="multiple_choice",
            tutor_persona={
                "character_style": "friendly",
                "humor_level": "medium",
                "tone": "encouraging",
                "complexity": "simple"
            }
        )
        
        # Should return mock data when model is None
        assert "question_type" in result
        assert result["question_type"] == "multiple_choice"
        assert "question" in result


@patch('google.generativeai.GenerativeModel')
def test_deliver_lesson_step_with_mocked_generation(mock_model_class):
    """Test delivering a lesson step with mocked content generation."""
    # Mock the model instance
    mock_model_instance = MagicMock()
    mock_model_class.return_value = mock_model_instance
    
    # Mock the generate_content method to return a specific response
    mock_response = MagicMock()
    mock_response.text = '''
    {
        "step_number": 1,
        "total_steps": 5,
        "title": "Introduction to Algebra",
        "content": "Algebra is a branch of mathematics...",
        "examples": ["x + 2 = 5"],
        "key_points": ["Variables represent unknowns"],
        "estimated_time_min": 5,
        "next_step_preview": "In the next step, we'll cover..."
    }
    '''
    mock_model_instance.generate_content.return_value = mock_response
    
    # Set the mocked model in the teaching_llm instance
    teaching_llm.model = mock_model_instance
    
    result = teaching_llm.deliver_lesson_step(
        subject="Math",
        topic="Algebra",
        step_number=1,
        total_steps=5,
        user_level="newbie",
        tutor_persona={
            "character_style": "friendly",
            "humor_level": "medium",
            "tone": "encouraging",
            "complexity": "simple"
        }
    )
    
    assert result["step_number"] == 1
    assert result["topic"] == "Algebra"  # This would be in content
    assert result["total_steps"] == 5


@patch('google.generativeai.GenerativeModel')
def test_generate_interactive_question_with_mocked_generation(mock_model_class):
    """Test generating an interactive question with mocked content generation."""
    # Mock the model instance
    mock_model_instance = MagicMock()
    mock_model_class.return_value = mock_model_instance
    
    # Mock the generate_content method to return a specific response
    mock_response = MagicMock()
    mock_response.text = '''
    {
        "question_type": "multiple_choice",
        "question": "What is x in the equation x + 2 = 5?",
        "options": ["1", "2", "3", "4"],
        "correct_answer": 2,
        "explanation": "Subtracting 2 from both sides gives x = 3",
        "difficulty": "easy"
    }
    '''
    mock_model_instance.generate_content.return_value = mock_response
    
    # Set the mocked model in the teaching_llm instance
    teaching_llm.model = mock_model_instance
    
    result = teaching_llm.generate_interactive_question(
        subject="Math",
        topic="Algebra",
        concept="Linear Equations",
        question_type="multiple_choice",
        tutor_persona={
            "character_style": "friendly",
            "humor_level": "medium",
            "tone": "encouraging",
            "complexity": "simple"
        }
    )
    
    assert result["question_type"] == "multiple_choice"
    assert "x + 2 = 5" in result["question"]
    assert result["correct_answer"] == 2


def test_update_lesson_complexity_with_mocked_llm():
    """Test updating lesson complexity with mocked LLM."""
    with patch.object(teaching_llm, 'model', None):
        result = teaching_llm.update_lesson_complexity(
            subject="Math",
            topic="Algebra",
            concept="Linear Equations",
            current_user_performance="good",
            tutor_persona={
                "character_style": "friendly",
                "humor_level": "medium",
                "tone": "encouraging",
                "complexity": "simple"
            }
        )
        
        # Should return mock data when model is None
        assert "subject" in result
        assert result["subject"] == "Math"
        assert "concept" in result
        assert result["concept"] == "Linear Equations"
        assert "content" in result