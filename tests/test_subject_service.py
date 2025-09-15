# tests/test_subject_service.py
import pytest
from app.services.subject_service import normalize_topic

def test_normalize_topic_known():
    result = normalize_topic("Quantum Entanglement")
    assert result["subject"] == "Physics"
    assert "quantum" in result["description"].lower()

def test_normalize_topic_python():
    result = normalize_topic("Python Basics")
    assert result["subject"] == "Programming"
    assert "python" in result["description"].lower()

def test_normalize_topic_unknown():
    topic = "Astrobiology"
    result = normalize_topic(topic)
    assert result["subject"] == "General"
    assert topic in result["description"]
