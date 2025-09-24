# app/llm/teaching_llm.py
"""
Teaching LLM module for interactive tutoring.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from app.config import settings

# Attempt to import Google Generative AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    genai = None
    GEMINI_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)

class TeachingLLM:
    """Teaching LLM class for interactive tutoring sessions."""
    
    def __init__(self):
        """Initialize the Teaching LLM."""
        # Configure the Gemini API if available and API key is set
        if GEMINI_AVAILABLE and settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL_NAME)
        else:
            self.model = None
            logger.warning("GEMINI_API_KEY not set or Google Generative AI not available. Teaching LLM will operate in mock mode.")
    
    def deliver_lesson_step(self, subject: str, topic: str, step_number: int, 
                          total_steps: int, user_level: str, tutor_persona: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deliver a lesson step to the user.
        
        Args:
            subject: The subject being taught
            topic: The specific topic within the subject
            step_number: Current step number in the lesson
            total_steps: Total number of steps in the lesson
            user_level: User's skill level (newbie, amateur, pro)
            tutor_persona: Tutor's personality attributes
            
        Returns:
            Dictionary containing the lesson step content and metadata.
        """
        try:
            if not self.model:
                return self._mock_lesson_step(subject, topic, step_number, total_steps, user_level, tutor_persona)
            
            # Create the prompt for lesson delivery
            prompt = self._create_lesson_prompt(subject, topic, step_number, total_steps, user_level, tutor_persona)
            
            # Generate the lesson content
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=2000,
                    response_mime_type="application/json"
                )
            )
            
            # Parse the JSON response
            lesson_data = json.loads(response.text)
            return lesson_data
            
        except Exception as e:
            logger.error(f"Error generating lesson step: {e}")
            # Fallback to mock data
            return self._mock_lesson_step(subject, topic, step_number, total_steps, user_level, tutor_persona)
    
    def generate_interactive_question(self, subject: str, topic: str, concept: str, 
                                    question_type: str, tutor_persona: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate an interactive question for the user.
        
        Args:
            subject: The subject being taught
            topic: The specific topic within the subject
            concept: The specific concept to test
            question_type: Type of question (multiple_choice, short_answer, etc.)
            tutor_persona: Tutor's personality attributes
            
        Returns:
            Dictionary containing the question and possible answers.
        """
        try:
            if not self.model:
                return self._mock_question(subject, topic, concept, question_type, tutor_persona)
            
            # Create the prompt for question generation
            prompt = self._create_personalized_question_prompt(subject, topic, concept, question_type, tutor_persona)
            
            # Generate the question
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1000,
                    response_mime_type="application/json"
                )
            )
            
            # Parse the JSON response
            question_data = json.loads(response.text)
            return question_data
            
        except Exception as e:
            logger.error(f"Error generating question: {e}")
            # Fallback to mock data
            return self._mock_question(subject, topic, concept, question_type, tutor_persona)
    
    def _create_lesson_prompt(self, subject: str, topic: str, step_number: int, 
                             total_steps: int, user_level: str, tutor_persona: Dict[str, Any]) -> str:
        """Create a prompt for lesson delivery."""
        # Get persona attributes with defaults
        character_style = tutor_persona.get('character_style', 'friendly')
        humor_level = tutor_persona.get('humor_level', 'medium')
        tone = tutor_persona.get('tone', 'encouraging')
        complexity = tutor_persona.get('complexity', 'simple')
        
        # Map humor level to specific instructions
        humor_instructions = {
            'low': 'Avoid jokes or humorous content',
            'medium': 'Include occasional light humor when appropriate',
            'high': 'Make the lesson engaging with jokes, puns, or humorous examples'
        }
        
        # Map character style to specific instructions
        style_instructions = {
            'friendly': 'Be warm and approachable in your explanations',
            'professional': 'Use formal language and maintain a professional tone',
            'funny': 'Keep the content light-hearted and humorous throughout',
            'motivational': 'Include encouraging messages and motivational elements'
        }
        
        # Map tone to specific instructions
        tone_instructions = {
            'encouraging': 'Provide positive reinforcement and encouragement',
            'direct': 'Be straightforward and to the point',
            'casual': 'Use informal language and a relaxed approach'
        }
        
        # Map complexity to specific instructions
        complexity_instructions = {
            'simple': 'Use basic language, simple examples, and step-by-step explanations',
            'moderate': 'Include some technical terms but with clear explanations',
            'complex': 'Use advanced terminology and in-depth analysis suitable for experts'
        }
        
        return f"""
        You are an AI tutor with the following persona:
        - Character Style: {character_style} - {style_instructions.get(character_style, 'Be warm and approachable in your explanations')}
        - Humor Level: {humor_level} - {humor_instructions.get(humor_level, 'Include occasional light humor when appropriate')}
        - Tone: {tone} - {tone_instructions.get(tone, 'Provide positive reinforcement and encouragement')}
        - Complexity: {complexity} - {complexity_instructions.get(complexity, 'Use basic language, simple examples, and step-by-step explanations')}
        
        Please provide a lesson step for the following:
        - Subject: {subject}
        - Topic: {topic}
        - Step: {step_number} of {total_steps}
        - User Level: {user_level}
        
        Respond in the following JSON format:
        {{
            "step_number": {step_number},
            "total_steps": {total_steps},
            "title": "Step title",
            "content": "Detailed explanation of the concept",
            "examples": ["Example 1", "Example 2"],
            "key_points": ["Point 1", "Point 2"],
            "estimated_time_min": 5,
            "next_step_preview": "Brief preview of what comes next"
        }}
        
        Requirements:
        1. Adapt the complexity and tone to match the tutor persona and user level
        2. Keep the explanation clear and engaging
        3. Include practical examples relevant to the topic
        4. Highlight key points that the user should remember
        5. Keep the estimated time realistic (2-10 minutes)
        6. Provide a smooth transition to the next step
        7. Return ONLY valid JSON, no additional text
        8. Make the explanation appropriate for the current step in the sequence
        9. Apply the personality traits as specified in the persona description
        """
    
    def _create_personalized_question_prompt(self, subject: str, topic: str, concept: str, 
                               question_type: str, tutor_persona: Dict[str, Any]) -> str:
        """Create a personalized prompt for question generation based on tutor persona."""
        # Get persona attributes with defaults
        character_style = tutor_persona.get('character_style', 'friendly')
        humor_level = tutor_persona.get('humor_level', 'medium')
        tone = tutor_persona.get('tone', 'encouraging')
        complexity = tutor_persona.get('complexity', 'simple')
        
        # Map humor level to specific instructions
        humor_instructions = {
            'low': 'Avoid jokes or humorous content',
            'medium': 'Include occasional light humor when appropriate',
            'high': 'Make the question engaging with jokes, puns, or humorous elements'
        }
        
        # Map character style to specific instructions
        style_instructions = {
            'friendly': 'Be warm and approachable in the question phrasing',
            'professional': 'Use formal language and maintain a professional tone',
            'funny': 'Keep the question light-hearted and humorous',
            'motivational': 'Include encouraging language in the question'
        }
        
        # Map tone to specific instructions
        tone_instructions = {
            'encouraging': 'Provide positive framing for the question',
            'direct': 'Be straightforward and to the point',
            'casual': 'Use informal language and a relaxed approach'
        }
        
        # Map complexity to specific instructions
        complexity_instructions = {
            'simple': 'Frame the question at a basic level with clear, simple language',
            'moderate': 'Include some technical terms but with clear context',
            'complex': 'Use advanced terminology and complex scenarios suitable for experts'
        }
        
        return f"""
        You are an AI tutor with the following persona:
        - Character Style: {character_style} - {style_instructions.get(character_style, 'Be warm and approachable in the question phrasing')}
        - Humor Level: {humor_level} - {humor_instructions.get(humor_level, 'Include occasional light humor when appropriate')}
        - Tone: {tone} - {tone_instructions.get(tone, 'Provide positive framing for the question')}
        - Complexity: {complexity} - {complexity_instructions.get(complexity, 'Frame the question at a basic level with clear, simple language')}
        
        Please generate a {question_type} question for the following:
        - Subject: {subject}
        - Topic: {topic}
        - Concept: {concept}
        
        Respond in the following JSON format:
        {{
            "question_type": "{question_type}",
            "question": "The question text",
            "options": ["Option A", "Option B", "Option C", "Option D"],  // For multiple choice
            "correct_answer": "Correct answer or index",
            "explanation": "Explanation of why the answer is correct",
            "difficulty": "easy|medium|hard"
        }}
        
        Requirements:
        1. Adapt the question difficulty to match the tutor persona and assumed user level
        2. Make the question clear and unambiguous
        3. For multiple choice, provide plausible distractors
        4. Include a helpful explanation
        5. Match the tutor's character style, tone, and complexity preferences
        6. Return ONLY valid JSON, no additional text
        """
    
    def update_lesson_complexity(self, subject: str, topic: str, concept: str, 
                                current_user_performance: str, tutor_persona: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adjust lesson complexity based on user's performance.
        
        Args:
            subject: The subject being taught
            topic: The specific topic within the subject
            concept: The specific concept being taught
            current_user_performance: User's current performance level (poor, average, good)
            tutor_persona: Tutor's personality attributes
            
        Returns:
            Dictionary containing adjusted lesson content.
        """
        try:
            if not self.model:
                # Return mock data when model is not available
                return {
                    "subject": subject,
                    "topic": topic,
                    "concept": concept,
                    "complexity_adjustment": f"Adjusted for {current_user_performance} performance",
                    "content": f"Mock content adjusted for {current_user_performance} performance in {subject}: {topic}",
                    "recommendation": f"Tutor suggests focusing on {concept} with more practice for {current_user_performance} performance"
                }
            
            # Create the prompt for complexity adjustment
            prompt = f"""
            You are an AI tutor with the following persona:
            - Character Style: {tutor_persona.get('character_style', 'friendly')}
            - Humor Level: {tutor_persona.get('humor_level', 'medium')}
            - Tone: {tutor_persona.get('tone', 'encouraging')}
            - Complexity: {tutor_persona.get('complexity', 'simple')}
            
            Please adjust the teaching approach for a user with '{current_user_performance}' performance in:
            - Subject: {subject}
            - Topic: {topic}
            - Concept: {concept}
            
            Respond in the following JSON format:
            {{
                "subject": "{subject}",
                "topic": "{topic}",
                "concept": "{concept}",
                "complexity_adjustment": "How complexity should be adjusted based on performance",
                "content": "Adjusted lesson content based on performance",
                "recommendation": "Specific recommendations for the user"
            }}
            
            Requirements:
            1. Adjust the content complexity based on the user's performance level
            2. Provide specific recommendations for improvement if performance is poor
            3. Suggest acceleration or additional challenges if performance is good
            4. Keep the explanation aligned with the tutor's persona
            5. Return ONLY valid JSON, no additional text
            """
            
            # Generate the adjusted lesson content
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1000,
                    response_mime_type="application/json"
                )
            )
            
            # Parse the JSON response
            adjustment_data = json.loads(response.text)
            return adjustment_data
            
        except Exception as e:
            logger.error(f"Error adjusting lesson complexity: {e}")
            # Return mock data as fallback
            return {
                "subject": subject,
                "topic": topic,
                "concept": concept,
                "complexity_adjustment": f"Adjusted for {current_user_performance} performance",
                "content": f"Mock content adjusted for {current_user_performance} performance in {subject}: {topic}",
                "recommendation": f"Tutor suggests focusing on {concept} with more practice for {current_user_performance} performance"
            }
    
    def _create_question_prompt(self, subject: str, topic: str, concept: str, 
                               question_type: str, tutor_persona: Dict[str, Any]) -> str:
        """Create a prompt for question generation."""
        return f"""
        You are an AI tutor with the following persona:
        - Character Style: {tutor_persona.get('character_style', 'friendly')}
        - Humor Level: {tutor_persona.get('humor_level', 'medium')}
        - Tone: {tutor_persona.get('tone', 'encouraging')}
        - Complexity: {tutor_persona.get('complexity', 'simple')}
        
        Please generate a {question_type} question for the following:
        - Subject: {subject}
        - Topic: {topic}
        - Concept: {concept}
        
        Respond in the following JSON format:
        {{
            "question_type": "{question_type}",
            "question": "The question text",
            "options": ["Option A", "Option B", "Option C", "Option D"],  // For multiple choice
            "correct_answer": "Correct answer or index",
            "explanation": "Explanation of why the answer is correct",
            "difficulty": "easy|medium|hard"
        }}
        
        Requirements:
        1. Adapt the question difficulty to the tutor persona and assumed user level
        2. Make the question clear and unambiguous
        3. For multiple choice, provide plausible distractors
        4. Include a helpful explanation
        5. Match the tutor's character style and tone
        6. Return ONLY valid JSON, no additional text
        """
    
    def _mock_lesson_step(self, subject: str, topic: str, step_number: int, 
                          total_steps: int, user_level: str, tutor_persona: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock lesson step data when LLM is not available."""
        tutor_name = tutor_persona.get('name', 'Friendly Tutor')
        character_style = tutor_persona.get('character_style', 'friendly')
        
        mock_content = f"Welcome to step {step_number} of {total_steps} in {subject}: {topic}!\n\n"
        mock_content += f"I'm {tutor_name}, your {character_style} guide through this learning journey. "
        mock_content += "Today we'll explore key concepts in a fun and engaging way!"
        
        return {
            "step_number": step_number,
            "total_steps": total_steps,
            "title": f"Introduction to {topic}",
            "content": mock_content,
            "examples": [
                f"Example related to {topic}",
                f"Another example for {subject}"
            ],
            "key_points": [
                f"Key concept 1 in {topic}",
                f"Important point about {subject}"
            ],
            "estimated_time_min": 5,
            "next_step_preview": f"In the next step, we'll dive deeper into {topic} concepts."
        }
    
    def _mock_question(self, subject: str, topic: str, concept: str, 
                      question_type: str, tutor_persona: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock question data when LLM is not available."""
        tutor_name = tutor_persona.get('name', 'Quiz Master')
        
        return {
            "question_type": question_type,
            "question": f"What is the most important aspect of {concept} in {subject}?",
            "options": [
                f"A fundamental principle of {concept}",
                f"A common misconception about {topic}",
                f"An advanced application of {concept}",
                f"None of the above"
            ],
            "correct_answer": 0,
            "explanation": f"Great question! As {tutor_name} always says, understanding the fundamentals is key.",
            "difficulty": "medium"
        }

# Global instance
teaching_llm = TeachingLLM()