# scripts/demo_curriculum.py
"""
Demo script to show how to use the curriculum generation feature with the Gemini API.
"""

import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / "app"))

from app.services.curriculum_service import generate_curriculum
from app.models.curriculum_model import CurriculumRequest

def demo_curriculum_generation():
    """Demo function to generate a curriculum using the Gemini API."""
    print("Curriculum Generation Demo")
    print("=" * 30)
    
    # Example: Generate a curriculum for Python programming at the newbie level
    subject = "Python Programming"
    path = "newbie"
    
    print(f"Generating curriculum for '{subject}' at '{path}' level...")
    
    try:
        # Generate the curriculum
        curriculum = generate_curriculum(subject, path)
        
        # Display the results
        print(f"\nCurriculum ID: {curriculum.curriculum_id}")
        print(f"Subject: {curriculum.subject_id}")
        print(f"Path: {curriculum.path}")
        print(f"Recommended Tutor Style: {curriculum.recommended_tutor_style}")
        print(f"Learning Objectives: {curriculum.learning_objectives}")
        print("\nModules:")
        for i, module in enumerate(curriculum.modules, 1):
            print(f"  {i}. {module.title} ({module.type}) - {module.difficulty}")
            print(f"     Estimated Time: {module.estimated_time_min} minutes")
            if module.description:
                print(f"     Description: {module.description}")
            if module.resources:
                print(f"     Resources: {', '.join(module.resources)}")
            print()
            
    except Exception as e:
        print(f"Error generating curriculum: {e}")

if __name__ == "__main__":
    demo_curriculum_generation()
