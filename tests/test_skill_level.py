# tests/test_skill_level.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.curriculum_model import Module

client = TestClient(app)

def test_skill_level_newbie_physics():
    response = client.post("/skill-level/", json={"topic": "Physics", "skill_level": "newbie"})
    assert response.status_code == 200
    data = response.json()
    assert data["path"] == "newbie"
    assert "Physics" in data["curriculum_id"]
    assert isinstance(data["modules"], list)
    assert len(data["modules"]) > 0
    # Check that modules are Module objects
    assert isinstance(data["modules"][0], dict)
    assert "module_id" in data["modules"][0]
    assert "title" in data["modules"][0]
    # Check for new fields in response
    assert "recommended_tutor_style" in data
    assert "learning_objectives" in data

def test_skill_level_unknown_skill():
    response = client.post("/skill-level/", json={"topic": "Physics", "skill_level": "expert"})
    # fallback path should be "newbie"
    assert response.status_code == 200
    data = response.json()
    assert data["path"] == "newbie"
    
def test_skill_level_module_details():
    """Test that skill level response includes detailed module information"""
    response = client.post("/skill-level/", json={"topic": "Physics", "skill_level": "newbie"})
    assert response.status_code == 200
    data = response.json()
    
    # Check that modules have required fields
    for module in data["modules"]:
        assert "module_id" in module
        assert "title" in module
        assert "type" in module
        assert "difficulty" in module
        assert module["type"] in ["lesson", "quiz", "project"]
        assert module["difficulty"] in ["easy", "medium", "hard"]
        
def test_skill_level_tutor_style():
    """Test that skill level response includes recommended tutor style"""
    response = client.post("/skill-level/", json={"topic": "Physics", "skill_level": "newbie"})
    assert response.status_code == 200
    data = response.json()
    
    # Check that response includes tutor style
    assert "recommended_tutor_style" in data
    assert data["recommended_tutor_style"] is not None
    
def test_skill_level_learning_objectives():
    """Test that skill level response includes learning objectives"""
    response = client.post("/skill-level/", json={"topic": "Physics", "skill_level": "newbie"})
    assert response.status_code == 200
    data = response.json()
    
    # Check that response includes learning objectives
    assert "learning_objectives" in data
    assert isinstance(data["learning_objectives"], list)
