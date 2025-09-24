"""
Unit tests for answer evaluation and hint systems.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.services.evaluation_service import evaluation_service


def test_evaluate_answer_basic():
    """Test basic answer evaluation functionality."""
    result = evaluation_service.evaluate_answer(
        user_answer="Paris",
        correct_answer="Paris",
        question_context={
            "subject": "Geography",
            "topic": "Capitals",
            "concept": "European Capitals",
            "question": "What is the capital of France?"
        },
        user_id="test_user_123"
    )
    
    assert "is_correct" in result
    assert result["is_correct"] == True
    assert "score" in result
    assert result["score"] == 100  # Exact match


def test_evaluate_answer_incorrect():
    """Test answer evaluation for incorrect answers."""
    result = evaluation_service.evaluate_answer(
        user_answer="London",
        correct_answer="Paris",
        question_context={
            "subject": "Geography",
            "topic": "Capitals",
            "concept": "European Capitals",
            "question": "What is the capital of France?"
        },
        user_id="test_user_123"
    )
    
    assert "is_correct" in result
    assert result["is_correct"] == False
    assert "score" in result
    assert result["score"] < 90  # Below threshold for correctness


def test_evaluate_answer_with_mocked_llm():
    """Test answer evaluation with mocked LLM for detailed feedback."""
    with patch('app.services.evaluation_service.teaching_llm.model', None):
        result = evaluation_service.evaluate_answer(
            user_answer="Paris",
            correct_answer="Paris",
            question_context={
                "subject": "Geography",
                "topic": "Capitals",
                "concept": "European Capitals",
                "question": "What is the capital of France?"
            },
            user_id="test_user_123"
        )
        
        assert "is_correct" in result
        assert "score" in result
        assert "feedback" in result
        assert "explanation" in result


def test_get_user_performance_summary():
    """Test getting user performance summary."""
    # First, record some performance data
    evaluation_service._record_performance(
        user_id="test_user_perf",
        question_context={
            "subject": "Math",
            "topic": "Algebra",
            "concept": "Linear Equations"
        },
        is_correct=True,
        score=95
    )
    
    evaluation_service._record_performance(
        user_id="test_user_perf",
        question_context={
            "subject": "Math",
            "topic": "Algebra",
            "concept": "Quadratic Equations"
        },
        is_correct=False,
        score=45
    )
    
    summary = evaluation_service.get_user_performance_summary("test_user_perf")
    
    assert summary["user_id"] == "test_user_perf"
    assert summary["total_questions"] == 2
    assert summary["correct_answers"] == 1
    assert summary["accuracy_percentage"] == 50.0
    assert "subject_performance" in summary
    assert "Math" in summary["subject_performance"]


def test_generate_hint_with_mocked_llm():
    """Test generating hints with mocked LLM."""
    with patch('app.services.evaluation_service.teaching_llm.model', None):
        result = evaluation_service.generate_hint(
            question_context={
                "subject": "Math",
                "topic": "Algebra",
                "concept": "Linear Equations",
                "question": "Solve for x: 2x + 3 = 7"
            },
            hint_level="starter"
        )
        
        assert "hint_level" in result
        assert result["hint_level"] == "starter"
        assert "hint" in result
        assert "relevance" in result


def test_get_progressive_hint():
    """Test getting progressive hints."""
    question_context = {
        "subject": "Math",
        "topic": "Algebra",
        "concept": "Linear Equations",
        "question": "Solve for x: 2x + 3 = 7"
    }
    
    # Get the first hint (should be starter level)
    hint1 = evaluation_service.get_progressive_hint(
        user_id="test_user_hints",
        question_context=question_context
    )
    
    assert hint1["hint_level"] == "starter"
    
    # Get the second hint (should be intermediate level)
    hint2 = evaluation_service.get_progressive_hint(
        user_id="test_user_hints",
        question_context=question_context
    )
    
    assert hint2["hint_level"] == "intermediate"


def test_adjust_complexity():
    """Test adjusting complexity based on user performance."""
    # First, record some performance data for the user
    evaluation_service._record_performance(
        user_id="test_user_complexity",
        question_context={
            "subject": "Math",
            "topic": "Algebra",
            "concept": "Linear Equations"
        },
        is_correct=True,
        score=95
    )
    
    result = evaluation_service.adjust_complexity(
        user_id="test_user_complexity",
        subject="Math",
        topic="Algebra"
    )
    
    assert "complexity_level" in result
    assert "message" in result
    assert "recommended_actions" in result
    assert "current_accuracy" in result