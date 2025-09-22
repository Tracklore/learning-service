# tests/test_curriculum.py
import pytest
from app.models.curriculum_model import Module, Curriculum, LearningPath

def test_module_creation():
    """Test that Module can be created with required fields"""
    module = Module(
        module_id="test_module_1",
        title="Test Module",
        type="lesson",
        difficulty="easy"
    )
    
    assert module.module_id == "test_module_1"
    assert module.title == "Test Module"
    assert module.type == "lesson"
    assert module.difficulty == "easy"
    
def test_module_optional_fields():
    """Test that Module can be created with optional fields"""
    module = Module(
        module_id="test_module_1",
        title="Test Module",
        type="lesson",
        difficulty="easy",
        estimated_time_min=30,
        resources=["https://example.com/resource1", "https://example.com/resource2"],
        embedding_vector=[0.1, 0.2, 0.3]
    )
    
    assert module.estimated_time_min == 30
    assert module.resources == ["https://example.com/resource1", "https://example.com/resource2"]
    assert module.embedding_vector == [0.1, 0.2, 0.3]
    
def test_module_default_values():
    """Test that Module has correct default values for optional fields"""
    module = Module(
        module_id="test_module_1",
        title="Test Module",
        type="lesson",
        difficulty="easy"
    )
    
    assert module.estimated_time_min is None
    assert module.resources is None
    assert module.embedding_vector is None

def test_module_type_validation():
    """Test that Module accepts valid types"""
    valid_types = ["lesson", "quiz", "project"]
    for valid_type in valid_types:
        module = Module(
            module_id="test_module_1",
            title="Test Module",
            type=valid_type,
            difficulty="easy"
        )
        assert module.type == valid_type

def test_module_difficulty_validation():
    """Test that Module accepts valid difficulty levels"""
    valid_difficulties = ["easy", "medium", "hard"]
    for valid_difficulty in valid_difficulties:
        module = Module(
            module_id="test_module_1",
            title="Test Module",
            type="lesson",
            difficulty=valid_difficulty
        )
        assert module.difficulty == valid_difficulty

def test_curriculum_creation():
    """Test that Curriculum can be created with required fields"""
    module = Module(
        module_id="test_module_1",
        title="Test Module",
        type="lesson",
        difficulty="easy"
    )
    
    curriculum = Curriculum(
        curriculum_id="test_curriculum_1",
        subject_id="Physics",
        path="newbie",
        modules=[module]
    )
    
    assert curriculum.curriculum_id == "test_curriculum_1"
    assert curriculum.subject_id == "Physics"
    assert curriculum.path == "newbie"
    assert len(curriculum.modules) == 1
    assert isinstance(curriculum.modules[0], Module)
    
def test_curriculum_optional_fields():
    """Test that Curriculum can be created with optional fields"""
    module = Module(
        module_id="test_module_1",
        title="Test Module",
        type="lesson",
        difficulty="easy"
    )
    
    curriculum = Curriculum(
        curriculum_id="test_curriculum_1",
        subject_id="Physics",
        path="newbie",
        modules=[module],
        recommended_tutor_style="friendly",
        learning_objectives=["Objective 1", "Objective 2"]
    )
    
    assert curriculum.recommended_tutor_style == "friendly"
    assert curriculum.learning_objectives == ["Objective 1", "Objective 2"]
    
def test_curriculum_default_values():
    """Test that Curriculum has correct default values for optional fields"""
    module = Module(
        module_id="test_module_1",
        title="Test Module",
        type="lesson",
        difficulty="easy"
    )
    
    curriculum = Curriculum(
        curriculum_id="test_curriculum_1",
        subject_id="Physics",
        path="newbie",
        modules=[module]
    )
    
    assert curriculum.recommended_tutor_style is None
    assert curriculum.learning_objectives is None

def test_curriculum_multiple_modules():
    """Test that Curriculum can handle multiple modules"""
    modules = [
        Module(
            module_id="test_module_1",
            title="Test Module 1",
            type="lesson",
            difficulty="easy"
        ),
        Module(
            module_id="test_module_2",
            title="Test Module 2",
            type="quiz",
            difficulty="medium"
        ),
        Module(
            module_id="test_module_3",
            title="Test Module 3",
            type="project",
            difficulty="hard"
        )
    ]
    
    curriculum = Curriculum(
        curriculum_id="test_curriculum_1",
        subject_id="Physics",
        path="newbie",
        modules=modules
    )
    
    assert len(curriculum.modules) == 3
    assert curriculum.modules[0].module_id == "test_module_1"
    assert curriculum.modules[1].module_id == "test_module_2"
    assert curriculum.modules[2].module_id == "test_module_3"

def test_learning_path_creation():
    """Test that LearningPath can be created with required fields"""
    learning_path = LearningPath(
        user_id="user_123",
        curriculum_id="curriculum_456"
    )
    
    assert learning_path.user_id == "user_123"
    assert learning_path.curriculum_id == "curriculum_456"
    assert learning_path.completed_modules == []
    assert learning_path.progress == 0.0
    assert learning_path.completion_status == "incomplete"
    
def test_learning_path_optional_fields():
    """Test that LearningPath can be created with optional fields"""
    learning_path = LearningPath(
        user_id="user_123",
        curriculum_id="curriculum_456",
        completed_modules=["module_1", "module_2"],
        progress=50.0,
        completion_status="in_progress"
    )
    
    assert learning_path.completed_modules == ["module_1", "module_2"]
    assert learning_path.progress == 50.0
    assert learning_path.completion_status == "in_progress"
    
def test_learning_path_progress_validation():
    """Test that LearningPath validates progress values"""
    # Test valid progress values
    valid_progress_values = [0.0, 25.5, 50.0, 75.2, 100.0]
    for progress in valid_progress_values:
        learning_path = LearningPath(
            user_id="user_123",
            curriculum_id="curriculum_456",
            progress=progress
        )
        assert learning_path.progress == progress
    
def test_learning_path_completion_status_validation():
    """Test that LearningPath accepts valid completion statuses"""
    valid_statuses = ["incomplete", "in_progress", "complete"]
    for status in valid_statuses:
        learning_path = LearningPath(
            user_id="user_123",
            curriculum_id="curriculum_456",
            completion_status=status
        )
        assert learning_path.completion_status == status
        
def test_learning_path_add_completed_module():
    """Test that LearningPath can track completed modules"""
    learning_path = LearningPath(
        user_id="user_123",
        curriculum_id="curriculum_456"
    )
    
    # Add modules to completed list
    learning_path.completed_modules.append("module_1")
    learning_path.completed_modules.append("module_2")
    
    assert len(learning_path.completed_modules) == 2
    assert "module_1" in learning_path.completed_modules
    assert "module_2" in learning_path.completed_modules

# Integration tests

def test_curriculum_with_learning_path():
    """Test integration between Curriculum and LearningPath"""
    # Create modules
    modules = [
        Module(
            module_id="physics_101",
            title="Introduction to Physics",
            type="lesson",
            difficulty="easy",
            estimated_time_min=30
        ),
        Module(
            module_id="physics_102",
            title="Classical Mechanics",
            type="lesson",
            difficulty="medium",
            estimated_time_min=45
        )
    ]
    
    # Create curriculum
    curriculum = Curriculum(
        curriculum_id="physics_newbie",
        subject_id="Physics",
        path="newbie",
        modules=modules,
        recommended_tutor_style="friendly",
        learning_objectives=["Understand basic physics principles"]
    )
    
    # Create learning path
    learning_path = LearningPath(
        user_id="student_001",
        curriculum_id=curriculum.curriculum_id
    )
    
    # Simulate completing a module
    learning_path.completed_modules.append(modules[0].module_id)
    learning_path.progress = 50.0
    learning_path.completion_status = "in_progress"
    
    # Verify integration
    assert learning_path.curriculum_id == curriculum.curriculum_id
    assert len(learning_path.completed_modules) == 1
    assert learning_path.completed_modules[0] == modules[0].module_id
    assert learning_path.progress == 50.0

def test_module_in_curriculum_and_learning_path():
    """Test that modules can be tracked from curriculum through learning path"""
    # Create a module
    module = Module(
        module_id="test_module_1",
        title="Test Module",
        type="lesson",
        difficulty="easy"
    )
    
    # Create curriculum with module
    curriculum = Curriculum(
        curriculum_id="test_curriculum",
        subject_id="General",
        path="newbie",
        modules=[module]
    )
    
    # Create learning path
    learning_path = LearningPath(
        user_id="student_001",
        curriculum_id=curriculum.curriculum_id
    )
    
    # Verify that the module from curriculum can be tracked in learning path
    assert curriculum.modules[0].module_id == module.module_id
    assert module.module_id not in learning_path.completed_modules
    
    # Add module to completed modules
    learning_path.completed_modules.append(module.module_id)
    assert module.module_id in learning_path.completed_modules