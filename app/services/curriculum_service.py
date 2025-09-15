# app/services/curriculum_service.py
from typing import List, Dict
from app.models.curriculum_model import Curriculum

# Mock database of modules for MVP
MODULE_DB = {
    "Physics": {
        "newbie": ["Mechanics Basics", "Introduction to Waves", "Simple Experiments"],
        "amateur": ["Classical Mechanics", "Electrodynamics", "Modern Physics"],
        "pro": ["Quantum Mechanics", "Relativity", "Advanced Experiments"]
    },
    "Programming": {
        "newbie": ["Variables & Loops", "Functions", "Basic Projects"],
        "amateur": ["Data Structures", "OOP Concepts", "Intermediate Projects"],
        "pro": ["Algorithms & Optimization", "Design Patterns", "Advanced Projects"]
    },
    "General": {
        "newbie": ["Introduction", "Basics", "Fundamentals"],
        "amateur": ["Intermediate Concepts", "Practice"],
        "pro": ["Advanced Topics", "Projects"]
    }
}

def generate_curriculum(subject: str, path: str) -> Curriculum:
    """
    Generate a curriculum for a given subject and skill level.
    """
    modules = MODULE_DB.get(subject, MODULE_DB["General"]).get(path, MODULE_DB["General"]["newbie"])
    
    curriculum = Curriculum(
        curriculum_id=f"{subject}_{path}",
        subject_id=subject,
        path=path,
        modules=modules
    )
    return curriculum

def recommend_curriculum_path(skill_level: str) -> str:
    """
    Placeholder function to map user skill level to a curriculum path.
    """
    allowed_paths = ["newbie", "amateur", "pro"]
    if skill_level.lower() in allowed_paths:
        return skill_level.lower()
    return "newbie"
