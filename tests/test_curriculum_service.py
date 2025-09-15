# tests/test_curriculum_service.py
import pytest
from app.services.curriculum_service import recommend_curriculum_path, generate_curriculum

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

def test_generate_curriculum_unknown_subject():
    curriculum = generate_curriculum("Astrobiology", "novice")
    assert curriculum.subject_id == "Astrobiology"
    assert curriculum.path == "novice"
    assert len(curriculum.modules) > 0
