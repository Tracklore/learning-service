"""
Knowledge state embeddings service for creating and managing vector representations of user knowledge.
"""

from typing import List, Dict, Optional
from app.models.progress_model import KnowledgeEmbedding, UserProgress
from app.models.curriculum_model import Module
from app.utils.logger import get_logger
from datetime import datetime

# Attempt to import numpy
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    # Define a simple fallback if numpy is not available
    class NumpyFallback:
        @staticmethod
        def random(size):
            import random
            return [random.random() for _ in range(size[0] if isinstance(size, tuple) else size)]
        
        @staticmethod
        def linalg_norm(vector):
            return sum(x * x for x in vector) ** 0.5
    
    np = NumpyFallback()
    NUMPY_AVAILABLE = False

logger = get_logger(__name__)

class KnowledgeStateEmbeddingsService:
    """Service for creating and managing knowledge state embeddings."""
    
    def __init__(self):
        """Initialize the Knowledge State Embeddings Service."""
        self.embedding_dimension = 128  # Standard dimension for knowledge embeddings
        self.topic_vectors = {}  # Store vectors for different topics
    
    def generate_knowledge_embedding(
        self, 
        user_id: str, 
        subject: str, 
        user_progress: UserProgress,
        modules: List[Module]
    ) -> KnowledgeEmbedding:
        """
        Generate a knowledge embedding vector for a user based on their progress.
        
        Args:
            user_id: The ID of the user
            subject: The subject being studied
            user_progress: User's progress information
            modules: List of modules in the curriculum
            
        Returns:
            KnowledgeEmbedding with the vector representation
        """
        # Create a vector based on user's mastery of different topics
        topics_mastery = {}
        
        # Calculate mastery for each topic/module
        for module in modules:
            # Determine how well the user knows this topic
            topic_mastery = self._calculate_topic_mastery(module, user_progress)
            topics_mastery[module.title] = topic_mastery
        
        # Create embedding vector based on topic mastery
        embedding_vector = self._create_embedding_vector(topics_mastery)
        
        # Create the knowledge embedding object
        knowledge_embedding = KnowledgeEmbedding(
            embedding_vector=embedding_vector,
            embedding_version="1.0",
            generated_at=datetime.now(),
            topics_covered=list(topics_mastery.keys()),
            topics_mastery=topics_mastery
        )
        
        logger.info(f"Generated knowledge embedding for user {user_id} in subject {subject}")
        return knowledge_embedding
    
    def _calculate_topic_mastery(self, module: Module, user_progress: UserProgress) -> float:
        """
        Calculate the user's mastery level for a specific topic/module.
        
        Args:
            module: The module/topic to calculate mastery for
            user_progress: User's progress information
            
        Returns:
            Mastery level as a float between 0 and 1
        """
        # This is a simplified calculation - in practice, this would use more complex logic
        # considering lesson completion, quiz scores, time spent, etc.
        
        # Check if this module's topic is in the user's completed lessons
        module_in_completed = any(module.module_id in lesson_id for lesson_id in user_progress.weaknesses + user_progress.strengths)
        
        if module.title.lower() in [w.lower() for w in user_progress.weaknesses]:
            # If it's a weakness, low mastery
            return 0.2
        elif module.title.lower() in [s.lower() for s in user_progress.strengths]:
            # If it's a strength, high mastery
            return 0.9
        elif module_in_completed and user_progress.overall_score:
            # If completed and we have an overall score, use a proportion
            return min(user_progress.overall_score / 100, 1.0)
        else:
            # Default mastery
            return 0.5
    
    def _create_embedding_vector(self, topics_mastery: Dict[str, float]) -> List[float]:
        """
        Create an embedding vector from topic mastery levels.
        
        Args:
            topics_mastery: Dictionary mapping topics to mastery levels
            
        Returns:
            Embedding vector as a list of floats
        """
        # Create a vector with random values and then adjust based on topic mastery
        vector = np.random.random(self.embedding_dimension).tolist()
        
        # Update parts of the vector based on topic mastery
        for i, (topic, mastery) in enumerate(topics_mastery.items()):
            # Use a hash of the topic to determine which parts of the vector to modify
            topic_hash = hash(topic) % self.embedding_dimension
            vector[topic_hash % self.embedding_dimension] = mastery
        
        # Normalize the vector
        vector = self._normalize_vector(vector)
        return vector
    
    def _normalize_vector(self, vector: List[float]) -> List[float]:
        """Normalize a vector to unit length."""
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return [v / norm for v in vector]
    
    def find_similar_users(self, user_embedding: KnowledgeEmbedding, all_user_embeddings: List[KnowledgeEmbedding]) -> List[Dict[str, any]]:
        """
        Find users with similar knowledge states.
        
        Args:
            user_embedding: The embedding for the target user
            all_user_embeddings: Embeddings for all users
            
        Returns:
            List of dictionaries containing similar users and similarity scores
        """
        similarities = []
        
        for other_embedding in all_user_embeddings:
            if other_embedding.embedding_vector:
                similarity = self._cosine_similarity(
                    user_embedding.embedding_vector,
                    other_embedding.embedding_vector
                )
                
                similarities.append({
                    "user_embedding": other_embedding,
                    "similarity": similarity
                })
        
        # Sort by similarity score (highest first)
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        return similarities
    
    def find_similar_content(self, user_embedding: KnowledgeEmbedding, modules: List[Module]) -> List[Module]:
        """
        Find content that is appropriate for the user's knowledge state.
        
        Args:
            user_embedding: The user's knowledge embedding
            modules: List of modules to evaluate
            
        Returns:
            List of modules that match the user's knowledge state
        """
        # For now, just return modules that are neither too easy nor too hard
        # based on the user's knowledge embedding
        matching_modules = []
        
        # This is a simplified implementation - in reality, this would use more complex algorithms
        # to compare the content's embedding with the user's embedding
        for module in modules:
            # If the module isn't too far from the user's current knowledge level, include it
            # This is a placeholder logic
            matching_modules.append(module)
        
        return matching_modules
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0
        
        return dot_product / (norm1 * norm2)


# Global instance of the knowledge state embeddings service
knowledge_state_embeddings_service = KnowledgeStateEmbeddingsService()