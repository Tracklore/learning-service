# tests/test_skill_level.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_skill_level_newbie_physics():
    response = client.post("/skill-level/", json={"topic": "Physics", "skill_level": "newbie"})
    assert response.status_code == 200
    data = response.json()
    assert data["path"] == "newbie"
    assert "Physics" in data["curriculum_id"]
    assert isinstance(data["modules"], list)
    assert len(data["modules"]) > 0

def test_skill_level_unknown_skill():
    response = client.post("/skill-level/", json={"topic": "Physics", "skill_level": "expert"})
    # fallback path should be "newbie"
    assert response.status_code == 200
    data = response.json()
    assert data["path"] == "newbie"
