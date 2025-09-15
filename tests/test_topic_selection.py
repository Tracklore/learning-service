# tests/test_topic_selection.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_topic_selection_quantum():
    response = client.post("/topic/", json={"topic": "Quantum Entanglement"})
    assert response.status_code == 200
    data = response.json()
    assert data["subject"] == "Physics"
    assert "quantum" in data["description"].lower()

def test_topic_selection_unknown():
    topic = "Astrobiology"
    response = client.post("/topic/", json={"topic": topic})
    assert response.status_code == 200
    data = response.json()
    assert data["subject"] == "General"
    assert topic in data["description"]
