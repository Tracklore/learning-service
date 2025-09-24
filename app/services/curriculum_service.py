# app/services/curriculum_service.py
from typing import List, Dict
from app.models.curriculum_model import Curriculum, Module
from app.llm.curriculum_llm import generate_curriculum_with_gemini
from app.analytics.bigquery_client import bigquery_client
from app.services.feedback_service import feedback_service
from app.services.progress_service import progress_service
from app.services.vector_db_service import vector_db_service
from app.llm.embeddings import embedding_service
from app.models.progress_model import UserProgress

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
                resources=["https://example.com/mechanics101"],
                description="Introduction to basic mechanics principles"
            ),
            Module(
                module_id="phys_newbie_2",
                title="Introduction to Waves",
                type="lesson",
                difficulty="easy",
                estimated_time_min=25,
                description="Understanding wave properties and behaviors"
            ),
            Module(
                module_id="phys_newbie_3",
                title="Simple Experiments",
                type="project",
                difficulty="medium",
                estimated_time_min=45,
                description="Perform simple physics experiments"
            )
        ],
        "amateur": [
            Module(
                module_id="phys_amateur_1",
                title="Classical Mechanics",
                type="lesson",
                difficulty="medium",
                estimated_time_min=40,
                description="Advanced classical mechanics concepts"
            ),
            Module(
                module_id="phys_amateur_2",
                title="Electrodynamics",
                type="lesson",
                difficulty="medium",
                estimated_time_min=35,
                description="Understanding electrodynamics principles"
            ),
            Module(
                module_id="phys_amateur_3",
                title="Modern Physics",
                type="lesson",
                difficulty="hard",
                estimated_time_min=50,
                description="Introduction to modern physics theories"
            )
        ],
        "pro": [
            Module(
                module_id="phys_pro_1",
                title="Quantum Mechanics",
                type="lesson",
                difficulty="hard",
                estimated_time_min=60,
                description="Advanced quantum mechanics principles"
            ),
            Module(
                module_id="phys_pro_2",
                title="Relativity",
                type="lesson",
                difficulty="hard",
                estimated_time_min=55,
                description="Understanding relativity concepts"
            ),
            Module(
                module_id="phys_pro_3",
                title="Advanced Experiments",
                type="project",
                difficulty="hard",
                estimated_time_min=90,
                description="Design and execute advanced experiments"
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
                estimated_time_min=20,
                description="Learn basic programming concepts"
            ),
            Module(
                module_id="prog_newbie_2",
                title="Functions",
                type="lesson",
                difficulty="easy",
                estimated_time_min=25,
                description="Understanding functions and their usage"
            ),
            Module(
                module_id="prog_newbie_3",
                title="Basic Projects",
                type="project",
                difficulty="medium",
                estimated_time_min=60,
                description="Apply learned concepts in basic projects"
            )
        ],
        "amateur": [
            Module(
                module_id="prog_amateur_1",
                title="Data Structures",
                type="lesson",
                difficulty="medium",
                estimated_time_min=40,
                description="Understanding data structures"
            ),
            Module(
                module_id="prog_amateur_2",
                title="OOP Concepts",
                type="lesson",
                difficulty="medium",
                estimated_time_min=35,
                description="Learn object-oriented programming concepts"
            ),
            Module(
                module_id="prog_amateur_3",
                title="Intermediate Projects",
                type="project",
                difficulty="medium",
                estimated_time_min=90,
                description="Apply intermediate programming concepts"
            )
        ],
        "pro": [
            Module(
                module_id="prog_pro_1",
                title="Algorithms & Optimization",
                type="lesson",
                difficulty="hard",
                estimated_time_min=60,
                description="Advanced algorithms and optimization techniques"
            ),
            Module(
                module_id="prog_pro_2",
                title="Design Patterns",
                type="lesson",
                difficulty="hard",
                estimated_time_min=50,
                description="Understanding common design patterns"
            ),
            Module(
                module_id="prog_pro_3",
                title="Advanced Projects",
                type="project",
                difficulty="hard",
                estimated_time_min=120,
                description="Apply advanced programming concepts in projects"
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
                estimated_time_min=15,
                description="Basic introduction to the subject"
            ),
            Module(
                module_id="gen_newbie_2",
                title="Basics",
                type="lesson",
                difficulty="easy",
                estimated_time_min=20,
                description="Fundamental concepts"
            ),
            Module(
                module_id="gen_newbie_3",
                title="Fundamentals",
                type="lesson",
                difficulty="easy",
                estimated_time_min=25,
                description="Core principles and concepts"
            )
        ],
        "amateur": [
            Module(
                module_id="gen_amateur_1",
                title="Intermediate Concepts",
                type="lesson",
                difficulty="medium",
                estimated_time_min=35,
                description="Intermediate level concepts"
            ),
            Module(
                module_id="gen_amateur_2",
                title="Practice",
                type="quiz",
                difficulty="medium",
                estimated_time_min=30,
                description="Practice and reinforce learning"
            )
        ],
        "pro": [
            Module(
                module_id="gen_pro_1",
                title="Advanced Topics",
                type="lesson",
                difficulty="hard",
                estimated_time_min=50,
                description="Advanced concepts and theories"
            ),
            Module(
                module_id="gen_pro_2",
                title="Projects",
                type="project",
                difficulty="hard",
                estimated_time_min=100,
                description="Apply advanced knowledge in projects"
            )
        ]
    }
}

def generate_curriculum(subject: str, path: str, user_id: str = None) -> Curriculum:
    """
    Generate a curriculum for a given subject and skill level.
    Tries to use LLM-based generation first, falls back to mock data if LLM fails.
    
    Args:
        subject: The subject for the curriculum
        path: The skill level path (newbie, amateur, pro)
        user_id: Optional user ID to personalize the curriculum based on user progress
    """
    try:
        # Get user progress if user_id is provided
        user_progress = None
        if user_id:
            user_progress = progress_service.get_user_progress(user_id, subject)
        
        # Try to generate curriculum using LLM
        curriculum_data = generate_curriculum_with_gemini(subject, path, path)
        
        # Convert modules to Module objects
        modules = [Module(**module_data) for module_data in curriculum_data.get("modules", [])]
        
        # Adapt curriculum based on user progress if available
        if user_progress:
            modules = _adapt_modules_based_on_progress(modules, user_progress)
        
        curriculum = Curriculum(
            curriculum_id=curriculum_data.get("curriculum_id", f"{subject}_{path}"),
            subject_id=subject,
            path=path,
            modules=modules,
            recommended_tutor_style=curriculum_data.get("recommended_tutor_style", "friendly"),
            learning_objectives=curriculum_data.get("learning_objectives", [])
        )
        return curriculum
    except Exception as e:
        # Fallback to mock data if LLM generation fails
        print(f"LLM generation failed, using mock data: {e}")
        
        # Create mock curriculum data for logging
        mock_curriculum_data = {
            "curriculum_id": f"{subject}_{path}",
            "subject_id": subject,
            "path": path,
            "modules": [],
            "recommended_tutor_style": "friendly",
            "learning_objectives": []
        }
        
        # Log the fallback to BigQuery
        bigquery_client.log_curriculum_generation(mock_curriculum_data, success=True, fallback_used=True)
        
        modules = MODULE_DB.get(subject, MODULE_DB["General"]).get(path, MODULE_DB["General"]["newbie"])
        
        # Get user progress if user_id is provided
        if user_id:
            user_progress = progress_service.get_user_progress(user_id, subject)
            if user_progress:
                modules = _adapt_modules_based_on_progress(modules, user_progress)
        
        # Determine recommended tutor style based on path
        tutor_style_map = {
            "newbie": "friendly",
            "amateur": "balanced",
            "pro": "technical"
        }
        
        # Enhance modules based on feedback if available
        modules = _enhance_modules_with_feedback(subject, path, modules)
        
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

def _adapt_modules_based_on_progress(modules: List[Module], user_progress: UserProgress) -> List[Module]:
    """
    Adapt curriculum modules based on user's progress.
    
    Args:
        modules: List of modules to adapt
        user_progress: User's progress information
        
    Returns:
        Adapted list of modules
    """
    # If user has weaknesses in certain areas, add more practice modules for those areas
    adapted_modules = []
    
    for module in modules:
        # Check if the module topic is in the user's weaknesses
        is_weakness = any(weakness.lower() in module.title.lower() for weakness in user_progress.weaknesses)
        
        # Check if the module topic is in the user's strengths
        is_strength = any(strength.lower() in module.title.lower() for strength in user_progress.strengths)
        
        if is_weakness:
            # For weaknesses, add additional practice modules
            adapted_modules.append(module)
            # Add a practice module after the lesson
            practice_module = Module(
                module_id=f"{module.module_id}_practice",
                title=f"Practice: {module.title}",
                type="quiz",
                difficulty=module.difficulty,
                estimated_time_min=15,
                resources=module.resources
            )
            adapted_modules.append(practice_module)
        elif is_strength:
            # For strengths, possibly accelerate by adding more advanced content
            adapted_modules.append(module)
            # Add an advanced module after the lesson if the user is doing well
            if user_progress.overall_score and user_progress.overall_score > 85:
                advanced_module = Module(
                    module_id=f"{module.module_id}_advanced",
                    title=f"Advanced: {module.title}",
                    type="lesson",
                    difficulty="hard",
                    estimated_time_min=module.estimated_time_min,
                    resources=module.resources
                )
                adapted_modules.append(advanced_module)
        else:
            # For other topics, keep the module as is
            adapted_modules.append(module)
    
    return adapted_modules

def _enhance_modules_with_feedback(subject: str, path: str, modules: List[Module]) -> List[Module]:
    """
    Enhance modules based on feedback analytics for the subject.
    
    Args:
        subject: The subject of the curriculum
        path: The skill level path
        modules: The list of modules to enhance
        
    Returns:
        Enhanced list of modules
    """
    # Get feedback analytics for the subject
    analytics = feedback_service.get_feedback_analytics(subject)
    
    if not analytics:
        return modules
    
    # If feedback indicates difficulty with certain topics, add more resources or examples
    # This is a simplified implementation - in a real system, this would be more sophisticated
    enhanced_modules = []
    
    for module in modules:
        # Create a copy to modify
        enhanced_module = module.copy()
        
        # If there are common suggestions related to this module's topic, enhance it
        for suggestion in analytics.common_suggestions:
            if suggestion.lower() in module.title.lower():
                # Add more resources or adjust difficulty based on feedback
                if module.resources is None:
                    enhanced_module.resources = []
                enhanced_module.resources.append(f"Additional resource for: {suggestion}")
        
        enhanced_modules.append(enhanced_module)
    
    return enhanced_modules

def find_relevant_content_via_semantic_search(query: str, subject: str, top_k: int = 5) -> List[Module]:
    """
    Find relevant content using semantic search based on a query.
    
    Args:
        query: The search query
        subject: The subject area to search in
        top_k: Number of relevant content items to return
        
    Returns:
        List of relevant modules
    """
    try:
        # Generate embedding for the query
        query_embedding = embedding_service.generate_embedding(query)
        
        # Find relevant content using the vector database
        relevant_content = vector_db_service.find_relevant_content(
            query_embedding=query_embedding,
            subject=subject,
            top_k=top_k
        )
        
        # Convert the search results to modules (in a real implementation, 
        # we would look up the actual module details)
        modules = []
        for content in relevant_content:
            metadata = content["metadata"]
            module = Module(
                module_id=metadata.get("content_id", "unknown"),
                title=metadata.get("title", "Unknown Title"),
                type=metadata.get("type", "lesson"),
                difficulty=metadata.get("difficulty", "medium"),
                estimated_time_min=metadata.get("estimated_time_min", 30),
                resources=metadata.get("resources", [])
            )
            modules.append(module)
        
        return modules
    except Exception as e:
        logger.error(f"Error in semantic search for query '{query}': {e}")
        return []


def recommend_content_for_user_weaknesses(user_id: str, subject: str, top_k: int = 3) -> List[Module]:
    """
    Recommend content to address a user's weaknesses using semantic search.
    
    Args:
        user_id: The ID of the user
        subject: The subject area
        top_k: Number of recommendations to return
        
    Returns:
        List of recommended modules
    """
    try:
        # Get the user's knowledge embedding from the vector database
        user_knowledge_embedding = None
        search_results = vector_db_service.search(
            query_embedding=embedding_service.generate_embedding(f"user {user_id} knowledge state"),
            top_k=1,
            namespace="users",
            filters={"user_id": user_id, "subject": subject}
        )
        
        if search_results:
            user_knowledge_embedding = search_results[0]["embedding"]
        else:
            # If we can't find the user's embedding, use their progress to generate a query
            user_progress = progress_service.get_user_progress(user_id, subject)
            if user_progress and user_progress.weaknesses:
                query = f"content to improve understanding of {', '.join(user_progress.weaknesses)} for {subject}"
                return find_relevant_content_via_semantic_search(query, subject, top_k)
        
        if user_knowledge_embedding is not None:
            # Find content that might help address weaknesses
            # This would typically be content that covers the user's weak areas
            relevant_content = vector_db_service.find_relevant_content(
                query_embedding=user_knowledge_embedding,
                subject=subject,
                top_k=top_k
            )
            
            # Convert the search results to modules
            modules = []
            for content in relevant_content:
                metadata = content["metadata"]
                module = Module(
                    module_id=metadata.get("content_id", "unknown"),
                    title=metadata.get("title", "Unknown Title"),
                    type=metadata.get("type", "lesson"),
                    difficulty=metadata.get("difficulty", "medium"),
                    estimated_time_min=metadata.get("estimated_time_min", 30),
                    resources=metadata.get("resources", [])
                )
                modules.append(module)
            
            return modules
        else:
            return []
    except Exception as e:
        logger.error(f"Error recommending content for user {user_id}: {e}")
        return []

def recommend_curriculum_path(skill_level: str) -> str:
    """
    Placeholder function to map user skill level to a curriculum path.
    """
    allowed_paths = ["newbie", "amateur", "pro"]
    if skill_level.lower() in allowed_paths:
        return skill_level.lower()
    return "newbie"