"""
Progress analytics module for advanced LLM-based analysis of user progress.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from app.config import settings
from app.models.progress_model import ProgressAnalytics
from app.utils.logger import get_logger

# Attempt to import Google Generative AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    genai = None
    GEMINI_AVAILABLE = False

logger = get_logger(__name__)

class ProgressAnalyticsLLM:
    """Class for performing advanced progress analytics using LLM."""
    
    def __init__(self):
        """Initialize the Progress Analytics LLM."""
        # Configure the Gemini API if available and API key is set
        if GEMINI_AVAILABLE and settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL_NAME)
        else:
            self.model = None
            logger.warning("GEMINI_API_KEY not set or Google Generative AI not available. Progress analytics will operate in mock mode.")
    
    def analyze_learning_patterns(self, user_id: str, subject: str, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze user's learning patterns to identify trends and recommendations.
        
        Args:
            user_id: The ID of the user
            subject: The subject being analyzed
            progress_data: Current progress data for the user
            
        Returns:
            Dictionary containing analysis and recommendations.
        """
        try:
            if not self.model:
                return self._mock_learning_pattern_analysis(user_id, subject, progress_data)
            
            # Create the prompt for pattern analysis
            prompt = self._create_pattern_analysis_prompt(user_id, subject, progress_data)
            
            # Generate the analysis
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1000,
                    response_mime_type="application/json"
                )
            )
            
            # Parse the JSON response
            analysis_data = json.loads(response.text)
            return analysis_data
            
        except Exception as e:
            logger.error(f"Error analyzing learning patterns for user {user_id}: {e}")
            # Return mock data as fallback
            return self._mock_learning_pattern_analysis(user_id, subject, progress_data)
    
    def _create_pattern_analysis_prompt(self, user_id: str, subject: str, progress_data: Dict[str, Any]) -> str:
        """Create a prompt for learning pattern analysis."""
        return f"""
        You are an AI learning analyst. Analyze the following progress data for user {user_id} in subject {subject}:
        
        Progress Data:
        {json.dumps(progress_data, indent=2)}
        
        Respond in the following JSON format:
        {{
            "user_id": "{user_id}",
            "subject": "{subject}",
            "learning_patterns": {{
                "pace": "slow|moderate|fast",
                "consistency": "high|medium|low",
                "strengths": ["topic1", "topic2"],
                "improvement_areas": ["topic1", "topic2"],
                "study_habits": ["habit1", "habit2"]
            }},
            "recommendations": [
                "Recommendation 1",
                "Recommendation 2"
            ],
            "risk_factors": [
                "Factor 1",
                "Factor 2"
            ],
            "motivational_insights": [
                "Insight 1",
                "Insight 2"
            ]
        }}
        
        Requirements:
        1. Identify the user's learning pace based on completion rates
        2. Assess consistency by looking at activity patterns
        3. Identify strengths based on high-performing areas
        4. Identify areas that need improvement based on low scores
        5. Provide actionable recommendations
        6. Identify any risk factors for learning success
        7. Include motivational insights to encourage the learner
        8. Return ONLY valid JSON, no additional text
        """
    
    def get_personalized_insights(self, user_id: str, subject: str, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate personalized insights based on user's progress.
        
        Args:
            user_id: The ID of the user
            subject: The subject being analyzed
            progress_data: Current progress data for the user
            
        Returns:
            Dictionary containing personalized insights.
        """
        try:
            if not self.model:
                return self._mock_personalized_insights(user_id, subject, progress_data)
            
            # Create the prompt for personalized insights
            prompt = self._create_insights_prompt(user_id, subject, progress_data)
            
            # Generate the insights
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=800,
                    response_mime_type="application/json"
                )
            )
            
            # Parse the JSON response
            insights_data = json.loads(response.text)
            return insights_data
            
        except Exception as e:
            logger.error(f"Error generating personalized insights for user {user_id}: {e}")
            # Return mock data as fallback
            return self._mock_personalized_insights(user_id, subject, progress_data)
    
    def _create_insights_prompt(self, user_id: str, subject: str, progress_data: Dict[str, Any]) -> str:
        """Create a prompt for personalized insights generation."""
        return f"""
        You are an AI learning coach. Generate personalized insights for user {user_id} in subject {subject} based on this progress data:
        
        Progress Data:
        {json.dumps(progress_data, indent=2)}
        
        Respond in the following JSON format:
        {{
            "user_id": "{user_id}",
            "subject": "{subject}",
            "insights": [
                "Insight 1",
                "Insight 2"
            ],
            "study_tips": [
                "Tip 1",
                "Tip 2"
            ],
            "confidence_level": "low|medium|high",
            "motivational_message": "Encouraging message for the user"
        }}
        
        Requirements:
        1. Provide specific insights based on the user's performance
        2. Suggest study tips tailored to their learning style and challenges
        3. Assess their confidence level based on performance and consistency
        4. Include a motivational message to encourage continued learning
        5. Return ONLY valid JSON, no additional text
        """
    
    def _mock_learning_pattern_analysis(self, user_id: str, subject: str, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock learning pattern analysis when LLM is not available."""
        return {
            "user_id": user_id,
            "subject": subject,
            "learning_patterns": {
                "pace": "moderate",
                "consistency": "medium",
                "strengths": ["basic concepts", "visual learning"],
                "improvement_areas": ["advanced problems", "time management"],
                "study_habits": ["evening sessions", "short bursts"]
            },
            "recommendations": [
                "Try studying in the morning for better focus",
                "Spend more time on advanced problems"
            ],
            "risk_factors": [
                "Inconsistent study schedule",
                "Over focus on easier topics"
            ],
            "motivational_insights": [
                "You're making steady progress!",
                "Your visual learning approach is effective"
            ]
        }
    
    def _mock_personalized_insights(self, user_id: str, subject: str, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock personalized insights when LLM is not available."""
        return {
            "user_id": user_id,
            "subject": subject,
            "insights": [
                "You perform better on practice problems than theory",
                "Your scores improve with repeated attempts"
            ],
            "study_tips": [
                "Review mistakes carefully before moving on",
                "Try explaining concepts to reinforce learning"
            ],
            "confidence_level": "medium",
            "motivational_message": "You're making great progress! Keep up the consistent effort."
        }


# Global instance
progress_analytics_llm = ProgressAnalyticsLLM()