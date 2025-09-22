# app/services/curriculum_service.py
from typing import List, Dict
from app.models.curriculum_model import Curriculum, Module

# Mock database of modules for MVP with enhanced details
MODULE_DB = {
    "Physics": {
        "newbie": [
            Module(
                module_id="phys_newbie_1",
                title="Mechanics Basics",
                type="lesson",
                difficulty="easy",
                estimated_time_min=30,
                resources=["https://example.com/mechanics101"]
            ),
            Module(
                module_id="phys_newbie_2",
                title="Introduction to Waves",
                type="lesson",
                difficulty="easy",
                estimated_time_min=25
            ),
            Module(
                module_id="phys_newbie_3",
                title="Simple Experiments",
                type="project",
                difficulty="medium",
                estimated_time_min=45
            )
        ],
        "amateur": [
            Module(
                module_id="phys_amateur_1",
                title="Classical Mechanics",
                type="lesson",
                difficulty="medium",
                estimated_time_min=40
            ),
            Module(
                module_id="phys_amateur_2",
                title="Electrodynamics",
                type="lesson",
                difficulty="medium",
                estimated_time_min=35
            ),
            Module(
                module_id="phys_amateur_3",
                title="Modern Physics",
                type="lesson",
                difficulty="hard",
                estimated_time_min=50
            )
        ],
        "pro": [
            Module(
                module_id="phys_pro_1",
                title="Quantum Mechanics",
                type="lesson",
                difficulty="hard",
                estimated_time_min=60
            ),
            Module(
                module_id="phys_pro_2",
                title="Relativity",
                type="lesson",
                difficulty="hard",
                estimated_time_min=55
            ),
            Module(
                module_id="phys_pro_3",
                title="Advanced Experiments",
                type="project",
                difficulty="hard",
                estimated_time_min=90
            )
        ]
    },
    "Programming": {
        "newbie": [
            Module(
                module_id="prog_newbie_1",
                title="Variables & Loops",
                type="lesson",
                difficulty="easy",
                estimated_time_min=20
            ),
            Module(
                module_id="prog_newbie_2",
                title="Functions",
                type="lesson",
                difficulty="easy",
                estimated_time_min=25
            ),
            Module(
                module_id="prog_newbie_3",
                title="Basic Projects",
                type="project",
                difficulty="medium",
                estimated_time_min=60
            )
        ],
        "amateur": [
            Module(
                module_id="prog_amateur_1",
                title="Data Structures",
                type="lesson",
                difficulty="medium",
                estimated_time_min=40
            ),
            Module(
                module_id="prog_amateur_2",
                title="OOP Concepts",
                type="lesson",
                difficulty="medium",
                estimated_time_min=35
            ),
            Module(
                module_id="prog_amateur_3",
                title="Intermediate Projects",
                type="project",
                difficulty="medium",
                estimated_time_min=90
            )
        ],
        "pro": [
            Module(
                module_id="prog_pro_1",
                title="Algorithms & Optimization",
                type="lesson",
                difficulty="hard",
                estimated_time_min=60
            ),
            Module(
                module_id="prog_pro_2",
                title="Design Patterns",
                type="lesson",
                difficulty="hard",
                estimated_time_min=50
            ),
            Module(
                module_id="prog_pro_3",
                title="Advanced Projects",
                type="project",
                difficulty="hard",
                estimated_time_min=120
            )
        ]
    },
    "General": {
        "newbie": [
            Module(
                module_id="gen_newbie_1",
                title="Introduction",
                type="lesson",
                difficulty="easy",
                estimated_time_min=15
            ),
            Module(
                module_id="gen_newbie_2",
                title="Basics",
                type="lesson",
                difficulty="easy",
                estimated_time_min=20
            ),
            Module(
                module_id="gen_newbie_3",
                title="Fundamentals",
                type="lesson",
                difficulty="easy",
                estimated_time_min=25
            )
        ],
        "amateur": [
            Module(
                module_id="gen_amateur_1",
                title="Intermediate Concepts",
                type="lesson",
                difficulty="medium",
                estimated_time_min=35
            ),
            Module(
                module_id="gen_amateur_2",
                title="Practice",
                type="quiz",
                difficulty="medium",
                estimated_time_min=30
            )
        ],
        "pro": [
            Module(
                module_id="gen_pro_1",
                title="Advanced Topics",
                type="lesson",
                difficulty="hard",
                estimated_time_min=50
            ),
            Module(
                module_id="gen_pro_2",
                title="Projects",
                type="project",
                difficulty="hard",
                estimated_time_min=100
            )
        ]
    }
}

def generate_curriculum(subject: str, path: str) -> Curriculum:
    """
    Generate a curriculum for a given subject and skill level.
    """
    modules = MODULE_DB.get(subject, MODULE_DB["General"]).get(path, MODULE_DB["General"]["newbie"])
    
    # Determine recommended tutor style based on path
    tutor_style_map = {
        "newbie": "friendly",
        "amateur": "balanced",
        "pro": "technical"
    }
    
    # Set learning objectives based on subject and path
    learning_objectives = []
    if subject == "Physics":
        if path == "newbie":
            learning_objectives = [
                "Understand basic mechanics principles",
                "Learn wave properties and behaviors",
                "Perform simple physics experiments"
            ]
        elif path == "amateur":
            learning_objectives = [
                "Master classical mechanics",
                "Understand electrodynamics concepts",
                "Explore modern physics theories"
            ]
        elif path == "pro":
            learning_objectives = [
                "Apply quantum mechanics principles",
                "Understand relativity concepts",
                "Design and execute advanced experiments"
            ]
    
    curriculum = Curriculum(
        curriculum_id=f"{subject}_{path}",
        subject_id=subject,
        path=path,
        modules=modules,
        recommended_tutor_style=tutor_style_map.get(path, "friendly"),
        learning_objectives=learning_objectives
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
