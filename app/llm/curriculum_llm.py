# app/llm/curriculum_llm.py
import json
from typing import Dict, Any
from app.config import settings
from app.utils.logger import get_logger
from app.analytics.bigquery_client import bigquery_client

# Attempt to import Google Generative AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    genai = None
    GEMINI_AVAILABLE = False

logger = get_logger(__name__)

# Configure the Gemini API if available
if GEMINI_AVAILABLE and settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

def generate_curriculum_with_gemini(subject: str, path: str, skill_level: str) -> Dict[str, Any]:
    """
    Generate a curriculum using the Gemini API based on subject, path, and skill level.
    
    Args:
        subject (str): The subject to generate curriculum for
        path (str): The learning path (newbie, amateur, pro)
        skill_level (str): The user's skill level
    
    Returns:
        Dict[str, Any]: The generated curriculum as a dictionary
    """
    if not GEMINI_AVAILABLE:
        logger.warning("Google Generative AI not available. Returning mock curriculum.")
        # Return a mock curriculum
        return {
            "subject": subject,
            "path": path,
            "modules": [
                {
                    "module_id": "mock_module_1",
                    "title": f"Introduction to {subject}",
                    "type": "lesson",
                    "difficulty": "easy",
                    "estimated_time_min": 30,
                    "resources": [],
                    "description": f"Basic concepts in {subject}"
                }
            ],
            "recommended_tutor_style": "friendly",
            "learning_objectives": [f"Learn basic {subject} concepts"]
        }
    
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in environment variables")
    
    # Try different models if the primary one fails
    # Start with the configured model, then try flash models which have better quotas
    models_to_try = [
        settings.GEMINI_MODEL_NAME, 
        "gemini-1.5-flash", 
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro",
        "gemini-1.5-pro-latest"
    ]
    
    # Prepare the prompt with JSON structure
    prompt = f"""
    Generate a detailed curriculum for {subject} at the {path} level for someone with {skill_level} skills.
    
    Please provide the response in the following JSON format:
    {{
        "subject": "{subject}",
        "path": "{path}",
        "modules": [
            {{
                "module_id": "unique_identifier",
                "title": "Module title",
                "type": "lesson|quiz|project",
                "difficulty": "easy|medium|hard",
                "estimated_time_min": 30,
                "resources": ["https://example.com/resource1", "https://example.com/resource2"],
                "description": "Brief description of what this module covers"
            }}
        ],
        "recommended_tutor_style": "friendly|balanced|technical",
        "learning_objectives": [
            "Objective 1",
            "Objective 2"
        ]
    }}
    
    Requirements:
    1. Provide exactly 3-5 modules
    2. Include a mix of lesson, quiz, and project types
    3. Set difficulty appropriately for the {path} level
    4. Estimated time should be realistic (15-120 minutes)
    5. Include 2-3 learning objectives
    6. Recommended tutor style should match the path level (newbie=friednly, amateur=balanced, pro=technical)
    7. Ensure all fields are populated with relevant content
    8. Return ONLY valid JSON, no additional text or markdown
    """
    
    # Try each model until one works
    for model_name in models_to_try:
        try:
            logger.info(f"Trying to generate curriculum with model: {model_name}")
            
            # Log API usage attempt
            bigquery_client.log_api_usage(model_name, success=False, error_message="Starting request")
            
            # Create the model
            model = genai.GenerativeModel(model_name)
            
            # Generate the curriculum
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=4000,
                    response_mime_type="application/json"
                )
            )
            
            # Parse the JSON response
            curriculum_data = json.loads(response.text)
            
            # Add curriculum_id based on subject and path
            curriculum_data["curriculum_id"] = f"{subject.lower()}_{path}"
            
            logger.info(f"Successfully generated curriculum for {subject} at {path} level using model {model_name}")
            
            # Log successful API usage and curriculum generation
            bigquery_client.log_api_usage(model_name, success=True)
            bigquery_client.log_curriculum_generation(curriculum_data, success=True, fallback_used=False)
            
            return curriculum_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response from Gemini API with model {model_name}: {e}")
            bigquery_client.log_api_usage(model_name, success=False, error_message=str(e))
            continue
        except Exception as e:
            logger.error(f"Error generating curriculum with Gemini API using model {model_name}: {e}")
            # Log the API usage error
            quota_exceeded = "quota" in str(e).lower() or "429" in str(e)
            bigquery_client.log_api_usage(model_name, success=False, error_message=str(e), quota_exceeded=quota_exceeded)
            
            # If it's a quota error, try the next model
            if quota_exceeded:
                continue
            # For other errors, re-raise
            raise Exception(f"Failed to generate curriculum: {e}")
    
    # If all models fail, raise an exception
    raise Exception("Failed to generate curriculum with all available models. Check your API key and quota limits.")