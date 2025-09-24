# tests/test_curriculum.py
import pytest
from app.services.curriculum_service import generate_curriculum
from app.models.curriculum_model import Curriculum

def test_generate_curriculum():
    """Test that curriculum generation works with mock data."""
    # Test with a known subject and path
    curriculum = generate_curriculum("Programming", "newbie")
    
    # Verify the returned object is a Curriculum
    assert isinstance(curriculum, Curriculum)
    
    # Verify basic properties
    assert curriculum.subject_id == "Programming"
    assert curriculum.path == "newbie"
    assert len(curriculum.modules) > 0
    
    # Verify modules have required fields
    for module in curriculum.modules:
        assert module.module_id is not None
        assert module.title is not None
        assert module.type is not None
        assert module.difficulty is not None

def test_generate_curriculum_with_unknown_subject():
    """Test that curriculum generation works with unknown subjects (fallback to General)."""
    curriculum = generate_curriculum("UnknownSubject", "newbie")
    
    # Verify the returned object is a Curriculum
    assert isinstance(curriculum, Curriculum)
    
    # Verify basic properties
    assert curriculum.subject_id == "UnknownSubject"
    assert curriculum.path == "newbie"
    assert len(curriculum.modules) > 0

if __name__ == "__main__":
    pytest.main([__file__])