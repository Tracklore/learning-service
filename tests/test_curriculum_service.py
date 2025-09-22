# tests/test_curriculum_service.py
import pytest
from app.services.curriculum_service import recommend_curriculum_path, generate_curriculum
from app.models.curriculum_model import Module

def test_recommend_curriculum_path_known():
    assert recommend_curriculum_path("newbie") == "newbie"
    assert recommend_curriculum_path("Pro") == "pro"

def test_recommend_curriculum_path_unknown():
    assert recommend_curriculum_path("expert") == "newbie"  # fallback

def test_generate_curriculum_known_subject():
    curriculum = generate_curriculum("Physics", "newbie")
    assert curriculum.subject_id == "Physics"
    assert curriculum.path == "newbie"
    assert isinstance(curriculum.modules, list)
    assert len(curriculum.modules) > 0
    # Check that modules are Module objects
    assert isinstance(curriculum.modules[0], Module)
    # Check that additional fields exist
    assert hasattr(curriculum, 'recommended_tutor_style')
    assert hasattr(curriculum, 'learning_objectives')

def test_generate_curriculum_unknown_subject():
    curriculum = generate_curriculum("Astrobiology", "novice")
    assert curriculum.subject_id == "Astrobiology"
    assert curriculum.path == "novice"
    assert len(curriculum.modules) > 0
    # Check that modules are Module objects
    assert isinstance(curriculum.modules[0], Module)
    
def test_generate_curriculum_module_details():
    """Test that generated curriculum modules have detailed information"""
    curriculum = generate_curriculum("Physics", "newbie")
    
    # Check that modules have required fields
    for module in curriculum.modules:
        assert isinstance(module, Module)
        assert module.module_id is not None
        assert module.title is not None
        assert module.type in ["lesson", "quiz", "project"]
        assert module.difficulty in ["easy", "medium", "hard"]
        
def test_generate_curriculum_tutor_style():
    """Test that curriculum has recommended tutor style based on path"""
    curriculum_newbie = generate_curriculum("Physics", "newbie")
    curriculum_pro = generate_curriculum("Physics", "pro")
    
    assert curriculum_newbie.recommended_tutor_style == "friendly"
    assert curriculum_pro.recommended_tutor_style == "technical"
    
def test_generate_curriculum_learning_objectives():
    """Test that curriculum has learning objectives for known subjects"""
    curriculum = generate_curriculum("Physics", "newbie")
    
    # Physics newbie should have learning objectives
    assert isinstance(curriculum.learning_objectives, list)
    assert len(curriculum.learning_objectives) > 0
    
def test_generate_curriculum_module_metadata():
    """Test that curriculum modules have metadata fields"""
    curriculum = generate_curriculum("Physics", "newbie")
    module = curriculum.modules[0]
    
    # Check that module has metadata fields (even if None)
    assert hasattr(module, 'estimated_time_min')
    assert hasattr(module, 'resources')
    assert hasattr(module, 'embedding_vector')
