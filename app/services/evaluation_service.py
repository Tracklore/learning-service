import json
import logging
from typing import Dict, Any, List, Optional
from app.llm.teaching_llm import teaching_llm
from app.models.tutor_model import TutorPersona
from app.services.progress_service import progress_service
from app.models.progress_model import ProgressUpdateRequest

# Configure logging
logger = logging.getLogger(__name__)

class EvaluationService:
    """Service for evaluating answers, generating hints, and adjusting complexity."""
    
    def __init__(self):
        """Initialize the Evaluation Service."""
        self.user_performance = {}  # Track user performance over time
        self.hint_history = {}  # Track hints shown to each user
    
    def evaluate_answer(
        self, 
        user_answer: str, 
        correct_answer: str, 
        question_context: Dict[str, Any], 
        user_id: str,
        tutor_persona: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate user's answer to a question and provide scoring and feedback.
        
        Args:
            user_answer: The answer provided by the user
            correct_answer: The correct answer to the question
            question_context: Context about the question (subject, topic, concept, etc.)
            user_id: The ID of the user answering
            tutor_persona: The tutor's persona for feedback style
            
        Returns:
            Dictionary containing evaluation results and feedback.
        """
        try:
            # Calculate initial score based on string similarity
            from difflib import SequenceMatcher
            score = round(SequenceMatcher(None, user_answer.lower(), correct_answer.lower()).ratio() * 100, 2)
            
            # Determine if answer is correct based on threshold
            is_correct = score >= 90  # 90% similarity threshold
            
            # Get enhanced evaluation from LLM
            evaluation = self._get_llm_evaluation(
                user_answer, 
                correct_answer, 
                question_context, 
                tutor_persona
            )
            
            # Save performance data for adaptive learning
            self._record_performance(user_id, question_context, is_correct, score)
            
            # Log progress to the progress service
            try:
                progress_request = ProgressUpdateRequest(
                    user_id=user_id,
                    lesson_id=question_context.get('lesson_id', f"lesson_{question_context.get('topic', 'unknown')}"),
                    subject=question_context.get('subject', 'unknown'),
                    completed=True,
                    score=score,
                    time_spent_seconds=None,  # Not specified
                    repeated_mistakes=[] if is_correct else [question_context.get('concept', 'unknown')],
                    notes=f"Answered question about {question_context.get('concept', 'unknown')}"
                )
                progress_service.update_progress(progress_request)
            except Exception as e:
                logger.error(f"Error logging progress for user {user_id}: {e}")
            
            result = {
                "is_correct": is_correct,
                "score": score,
                "feedback": evaluation.get("feedback", ""),
                "explanation": evaluation.get("explanation", ""),
                "improvement_suggestions": evaluation.get("improvement_suggestions", [])
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error evaluating answer for user {user_id}: {e}")
            # Return default evaluation in case of error
            is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
            score = 100 if is_correct else 0
            
            return {
                "is_correct": is_correct,
                "score": score,
                "feedback": f"{'Correct!' if is_correct else 'Incorrect.'}",
                "explanation": f"The correct answer is: {correct_answer}",
                "improvement_suggestions": []
            }
    
    def _get_llm_evaluation(
        self, 
        user_answer: str, 
        correct_answer: str, 
        question_context: Dict[str, Any], 
        tutor_persona: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get enhanced evaluation from LLM based on user's answer.
        
        Args:
            user_answer: The answer provided by the user
            correct_answer: The correct answer to the question
            question_context: Context about the question
            tutor_persona: The tutor's persona for feedback style
            
        Returns:
            Dictionary with detailed feedback and explanation.
        """
        try:
            if not teaching_llm.model:
                # Return mock evaluation when LLM is not available
                return {
                    "feedback": "Your answer was reviewed.",
                    "explanation": f"The correct answer is: {correct_answer}",
                    "improvement_suggestions": ["Review the concept material for better understanding."]
                }
            
            # Use default tutor persona if none provided
            if not tutor_persona:
                tutor_persona = {
                    "character_style": "friendly",
                    "humor_level": "medium", 
                    "tone": "encouraging",
                    "complexity": "simple"
                }
            
            # Get persona attributes with defaults
            character_style = tutor_persona.get('character_style', 'friendly')
            humor_level = tutor_persona.get('humor_level', 'medium')
            tone = tutor_persona.get('tone', 'encouraging')
            complexity = tutor_persona.get('complexity', 'simple')
            
            # Map humor level to specific instructions
            humor_instructions = {
                'low': 'Avoid jokes or humorous content in feedback',
                'medium': 'Include occasional light humor when appropriate',
                'high': 'Make the feedback engaging with jokes, puns, or humorous elements'
            }
            
            # Map character style to specific instructions
            style_instructions = {
                'friendly': 'Be warm and supportive in feedback',
                'professional': 'Use formal language and maintain a professional tone',
                'funny': 'Keep the feedback light-hearted and humorous',
                'motivational': 'Include encouraging messages and positive reinforcement'
            }
            
            # Map tone to specific instructions
            tone_instructions = {
                'encouraging': 'Provide positive reinforcement and encouragement',
                'direct': 'Be straightforward and to the point',
                'casual': 'Use informal language and a relaxed approach'
            }
            
            # Map complexity to specific instructions
            complexity_instructions = {
                'simple': 'Use basic language and simple explanations',
                'moderate': 'Include some technical terms but with clear explanations',
                'complex': 'Use advanced terminology and in-depth analysis'
            }
            
            # Create the prompt for evaluation
            prompt = f"""
            You are an AI tutor with the following persona:
            - Character Style: {character_style} - {style_instructions.get(character_style, 'Be warm and supportive in feedback')}
            - Humor Level: {humor_level} - {humor_instructions.get(humor_level, 'Include occasional light humor when appropriate')}
            - Tone: {tone} - {tone_instructions.get(tone, 'Provide positive reinforcement and encouragement')}
            - Complexity: {complexity} - {complexity_instructions.get(complexity, 'Use basic language and simple explanations')}
            
            Please evaluate the user's answer to the following question:
            - Subject: {question_context.get('subject', 'Unknown')}
            - Topic: {question_context.get('topic', 'Unknown')}
            - Concept: {question_context.get('concept', 'Unknown')}
            - Question: {question_context.get('question', 'Unknown')}
            - Correct Answer: {correct_answer}
            - User's Answer: {user_answer}
            
            Respond in the following JSON format:
            {{
                "feedback": "Brief feedback on the user's answer",
                "explanation": "Detailed explanation of the correct answer and why it's correct",
                "improvement_suggestions": ["Suggestion 1", "Suggestion 2"]
            }}
            
            Requirements:
            1. Provide constructive feedback appropriate to the tutor's persona
            2. Give a detailed explanation of the correct answer
            3. Suggest specific ways the user can improve their understanding
            4. Match the tone, style, and complexity to the tutor's persona
            5. Return ONLY valid JSON, no additional text
            """
            
            # Generate the evaluation
            response = teaching_llm.model.generate_content(
                prompt,
                generation_config=teaching_llm.model._prepare_generate_content_request(
                    generation_config={
                        "temperature": 0.7,
                        "max_output_tokens": 800,
                        "response_mime_type": "application/json"
                    }
                ).generation_config
            )
            
            # Parse the JSON response
            evaluation_data = response.text
            import json
            return json.loads(evaluation_data)
            
        except Exception as e:
            logger.error(f"Error getting LLM evaluation: {e}")
            # Return mock data as fallback
            return {
                "feedback": "Your answer was reviewed.",
                "explanation": f"The correct answer is: {correct_answer}",
                "improvement_suggestions": ["Review the concept material for better understanding."]
            }
    
    def _record_performance(self, user_id: str, question_context: Dict[str, Any], is_correct: bool, score: float):
        """
        Record user performance for adaptive learning.
        
        Args:
            user_id: The ID of the user
            question_context: Context about the question
            is_correct: Whether the answer was correct
            score: The numerical score of the answer
        """
        if user_id not in self.user_performance:
            self.user_performance[user_id] = []
        
        performance_entry = {
            "timestamp": self._get_current_timestamp(),
            "subject": question_context.get("subject", "Unknown"),
            "topic": question_context.get("topic", "Unknown"),
            "concept": question_context.get("concept", "Unknown"),
            "is_correct": is_correct,
            "score": score
        }
        
        self.user_performance[user_id].append(performance_entry)
        
        # Keep only the last 50 performance entries per user
        if len(self.user_performance[user_id]) > 50:
            self.user_performance[user_id] = self.user_performance[user_id][-50:]
    
    def get_user_performance_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get a summary of user's performance for adaptive learning.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            Dictionary containing performance statistics.
        """
        if user_id not in self.user_performance:
            return {
                "user_id": user_id,
                "total_questions": 0,
                "correct_answers": 0,
                "accuracy_percentage": 0,
                "recent_performance": [],
                "subject_performance": {}
            }
        
        user_data = self.user_performance[user_id]
        
        # Calculate overall stats
        total_questions = len(user_data)
        correct_answers = sum(1 for entry in user_data if entry["is_correct"])
        accuracy_percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        # Get recent performance (last 10 entries)
        recent_performance = user_data[-10:]
        
        # Calculate performance by subject
        subject_performance = {}
        for entry in user_data:
            subject = entry["subject"]
            if subject not in subject_performance:
                subject_performance[subject] = {
                    "total_questions": 0,
                    "correct_answers": 0
                }
            subject_performance[subject]["total_questions"] += 1
            if entry["is_correct"]:
                subject_performance[subject]["correct_answers"] += 1
        
        # Calculate accuracy per subject
        for subject, stats in subject_performance.items():
            stats["accuracy_percentage"] = (stats["correct_answers"] / stats["total_questions"]) * 100
        
        return {
            "user_id": user_id,
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "accuracy_percentage": round(accuracy_percentage, 2),
            "recent_performance": recent_performance,
            "subject_performance": subject_performance
        }
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()


    def generate_hint(
        self, 
        question_context: Dict[str, Any], 
        hint_level: str = "starter", 
        tutor_persona: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a hint for a question based on the requested level.
        
        Args:
            question_context: Context about the question (subject, topic, concept, etc.)
            hint_level: Level of hint ("starter", "intermediate", "advanced")
            tutor_persona: The tutor's persona for hint style
            
        Returns:
            Dictionary containing the hint and its attributes.
        """
        try:
            if not teaching_llm.model:
                # Return mock hint when LLM is not available
                return {
                    "hint_level": hint_level,
                    "hint": f"This is a {hint_level} hint for the question about {question_context.get('concept', 'unknown concept')}.",
                    "relevance": 0.8
                }
            
            # Use default tutor persona if none provided
            if not tutor_persona:
                tutor_persona = {
                    "character_style": "friendly",
                    "humor_level": "medium", 
                    "tone": "encouraging",
                    "complexity": "simple"
                }
            
            # Get persona attributes with defaults
            character_style = tutor_persona.get('character_style', 'friendly')
            humor_level = tutor_persona.get('humor_level', 'medium')
            tone = tutor_persona.get('tone', 'encouraging')
            complexity = tutor_persona.get('complexity', 'simple')
            
            # Map humor level to specific instructions
            humor_instructions = {
                'low': 'Avoid jokes or humorous content in hints',
                'medium': 'Include occasional light humor when appropriate',
                'high': 'Make the hint engaging with jokes, puns, or humorous elements'
            }
            
            # Map character style to specific instructions
            style_instructions = {
                'friendly': 'Be warm and supportive in the hint',
                'professional': 'Use formal language and maintain a professional tone',
                'funny': 'Keep the hint light-hearted and humorous',
                'motivational': 'Include encouraging messages in the hint'
            }
            
            # Map tone to specific instructions
            tone_instructions = {
                'encouraging': 'Provide positive reinforcement in the hint',
                'direct': 'Be straightforward and to the point',
                'casual': 'Use informal language and a relaxed approach'
            }
            
            # Map complexity to specific instructions
            complexity_instructions = {
                'simple': 'Use basic language and simple hints',
                'moderate': 'Include some technical terms but with clear explanations in hints',
                'complex': 'Use advanced terminology and complex hints'
            }
            
            # Define hint complexity based on level
            hint_complexity = {
                "starter": "Provide a simple hint that gives a basic clue without revealing the answer",
                "intermediate": "Provide a more detailed hint that points toward the solution",
                "advanced": "Provide a substantial hint that almost gives the answer"
            }
            
            # Create the prompt for hint generation
            prompt = f"""
            You are an AI tutor with the following persona:
            - Character Style: {character_style} - {style_instructions.get(character_style, 'Be warm and supportive in the hint')}
            - Humor Level: {humor_level} - {humor_instructions.get(humor_level, 'Include occasional light humor when appropriate')}
            - Tone: {tone} - {tone_instructions.get(tone, 'Provide positive reinforcement in the hint')}
            - Complexity: {complexity} - {complexity_instructions.get(complexity, 'Use basic language and simple hints')}
            
            Please generate a hint for the following question:
            - Subject: {question_context.get('subject', 'Unknown')}
            - Topic: {question_context.get('topic', 'Unknown')}
            - Concept: {question_context.get('concept', 'Unknown')}
            - Question: {question_context.get('question', 'Unknown')}
            
            The hint should be at the '{hint_level}' level: {hint_complexity.get(hint_level, 'Provide a hint that helps the user progress')}.
            
            Respond in the following JSON format:
            {{
                "hint_level": "{hint_level}",
                "hint": "The generated hint text",
                "relevance": 0.8
            }}
            
            Requirements:
            1. Generate a helpful hint appropriate to the hint level
            2. Match the tone, style, and complexity to the tutor's persona
            3. Ensure the hint is relevant to the question
            4. Don't give away the answer completely for starter or intermediate hints
            5. Return ONLY valid JSON, no additional text
            """
            
            # Generate the hint
            response = teaching_llm.model.generate_content(
                prompt,
                generation_config=teaching_llm.model._prepare_generate_content_request(
                    generation_config={
                        "temperature": 0.7,
                        "max_output_tokens": 500,
                        "response_mime_type": "application/json"
                    }
                ).generation_config
            )
            
            # Parse the JSON response
            hint_data = response.text
            import json
            result = json.loads(hint_data)
            
            # Track hint history for this user and question
            question_id = question_context.get("question_id", f"{question_context.get('subject')}_{question_context.get('topic')}_{question_context.get('concept')}")
            if question_id not in self.hint_history:
                self.hint_history[question_id] = []
            
            self.hint_history[question_id].append(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating hint: {e}")
            # Return mock data as fallback
            return {
                "hint_level": hint_level,
                "hint": f"This is a {hint_level} hint for the question about {question_context.get('concept', 'unknown concept')}.",
                "relevance": 0.8
            }
    
    def get_progressive_hint(
        self, 
        user_id: str, 
        question_context: Dict[str, Any], 
        tutor_persona: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get the next progressive hint based on user's current position in the hint sequence.
        
        Args:
            user_id: The ID of the user requesting the hint
            question_context: Context about the question
            tutor_persona: The tutor's persona for hint style
            
        Returns:
            Dictionary containing the next progressive hint.
        """
        # Determine the appropriate hint level based on how many hints have already been shown
        question_id = question_context.get("question_id", f"{question_context.get('subject')}_{question_context.get('topic')}_{question_context.get('concept')}")
        
        if question_id in self.hint_history:
            hint_count = len(self.hint_history[question_id])
        else:
            hint_count = 0
        
        # Define hint progression
        hint_levels = ["starter", "intermediate", "advanced"]
        
        # Select hint level based on number of previous hints
        if hint_count < len(hint_levels):
            hint_level = hint_levels[hint_count]
        else:
            # If user has seen all standard hints, repeat the most detailed one
            hint_level = hint_levels[-1]
        
        return self.generate_hint(question_context, hint_level, tutor_persona)
    
    def adjust_complexity(
        self, 
        user_id: str, 
        subject: str, 
        topic: str, 
        current_performance: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Adjust the complexity of lessons based on user's performance.
        
        Args:
            user_id: The ID of the user
            subject: The subject being taught
            topic: The topic within the subject
            current_performance: Current performance data (if available)
            
        Returns:
            Dictionary containing adjusted complexity parameters.
        """
        if current_performance is None:
            current_performance = self.get_user_performance_summary(user_id)
        
        # Calculate accuracy for the specific subject and topic
        subject_accuracy = 0
        topic_accuracy = 0
        
        if subject in current_performance["subject_performance"]:
            subject_accuracy = current_performance["subject_performance"][subject]["accuracy_percentage"]
        
        # Find topic-specific performance if available
        for entry in current_performance["recent_performance"]:
            if entry["topic"] == topic:
                topic_accuracy = entry["score"]
                break
        
        # Calculate overall accuracy
        overall_accuracy = current_performance["accuracy_percentage"]
        
        # Determine complexity level based on performance
        # Higher accuracy = more complex, lower accuracy = simpler
        avg_accuracy = (subject_accuracy + topic_accuracy + overall_accuracy) / 3
        
        if avg_accuracy >= 80:
            complexity_level = "complex"
            message = "Based on your excellent performance, we're increasing the complexity."
        elif avg_accuracy >= 60:
            complexity_level = "moderate"
            message = "Based on your performance, the material is appropriately challenging."
        else:
            complexity_level = "simple"
            message = "Based on your performance, we're simplifying the content to help you build understanding."
        
        # Use teaching LLM to adjust lesson content based on performance
        complexity_adjustment = teaching_llm.update_lesson_complexity(
            subject=subject,
            topic=topic,
            concept=topic,  # For now, using topic as concept
            current_user_performance="good" if avg_accuracy >= 70 else ("average" if avg_accuracy >= 50 else "poor"),
            tutor_persona={"complexity": complexity_level}  # Simplified tutor persona for adjustment
        )
        
        return {
            "complexity_level": complexity_level,
            "message": message,
            "recommended_actions": complexity_adjustment.get("recommendation", []),
            "adjusted_content": complexity_adjustment.get("content", ""),
            "current_accuracy": {
                "overall": overall_accuracy,
                "subject": subject_accuracy,
                "topic": topic_accuracy
            }
        }

# Global instance
evaluation_service = EvaluationService()