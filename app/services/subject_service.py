# app/services/subject_service.py
from typing import Dict
from app.utils.logger import get_logger

logger = get_logger(__name__)

def normalize_topic(topic: str) -> Dict[str, str]:
    """
    Accept a user-provided topic and return:
    - normalized subject
    - topic name
    - short description

    Replace this mock with your real LLM call later.
    """
    topic_lower = topic.lower()
    logger.info(f"Normalizing topic: {topic}")

    if "quantum" in topic_lower:
        return {
            "subject": "Physics",
            "topic": topic,
            "description": "Learn about quantum phenomena, including superposition and entanglement."
        }
    elif "python" in topic_lower:
        return {
            "subject": "Programming",
            "topic": topic,
            "description": "Learn Python programming fundamentals and advanced concepts."
        }
    else:
        return {
            "subject": "General",
            "topic": topic,
            "description": f"A general learning topic on {topic}."
        }
