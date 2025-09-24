#!/usr/bin/env python3
"""
Test script for the learning service with development environment.
"""

import os
import sys
from pathlib import Path

# Add the project directory to the Python path
sys.path.append(str(Path(__file__).parent))

def test_with_development_env():
    """Test the curriculum generation with the development environment."""
    print("Testing curriculum generation with development environment...")
    
    # Set the environment to use the development file
    os.environ["ENV_FILE"] = ".env.development"
    
    # Import after setting the environment
    from app.services.curriculum_service import generate_curriculum
    
    # Generate a curriculum (will use mock data since API key is placeholder)
    print("\nGenerating curriculum for 'Python Programming' at 'newbie' level...")
    curriculum = generate_curriculum("Python Programming", "newbie")
    
    # Display results
    print(f"Curriculum ID: {curriculum.curriculum_id}")
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
        print()

if __name__ == "__main__":
    test_with_development_env()