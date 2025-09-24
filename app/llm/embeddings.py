"""
Embeddings module for generating vector representations of content and user knowledge states.
"""

import logging
from typing import List, Dict, Any, Optional
from app.config import settings
from app.utils.logger import get_logger

# Attempt to import Google Generative AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    genai = None
    GEMINI_AVAILABLE = False

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

class EmbeddingService:
    """Service for generating and working with text embeddings."""
    
    def __init__(self):
        """Initialize the Embedding Service."""
        # Configure the Gemini API if available and API key is set
        if GEMINI_AVAILABLE and settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            # Use the embedding model
            self.model = "text-embedding-004"  # Using a specific embedding model
        else:
            self.model = None
            logger.warning("GEMINI_API_KEY not set or Google Generative AI not available. Embedding service will operate in mock mode.")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate an embedding for the given text.
        
        Args:
            text: The input text to generate an embedding for
            
        Returns:
            A list of floats representing the embedding vector
        """
        if not self.model:
            return self._generate_mock_embedding(text)
        
        try:
            # Use the embedding API
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="semantic_similarity"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Error generating embedding for text '{text[:50]}...': {e}")
            # Return mock embedding as fallback
            return self._generate_mock_embedding(text)
    
    def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts.
        
        Args:
            texts: A list of input texts to generate embeddings for
            
        Returns:
            A list of embedding vectors (each vector is a list of floats)
        """
        embeddings = []
        for text in texts:
            embedding = self.generate_embedding(text)
            embeddings.append(embedding)
        return embeddings
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate the cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score between 0 and 1
        """
        # Convert to numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Calculate cosine similarity
        cosine_similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        
        # Ensure the result is between 0 and 1
        # Cosine similarity is actually between -1 and 1, so we normalize it
        normalized_similarity = (cosine_similarity + 1) / 2
        return float(normalized_similarity)
    
    def find_most_similar(self, query_embedding: List[float], 
                         candidate_embeddings: List[List[float]], 
                         top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find the most similar embeddings to the query embedding.
        
        Args:
            query_embedding: The embedding to compare against
            candidate_embeddings: List of candidate embeddings to compare with
            top_k: Number of top results to return
            
        Returns:
            List of dictionaries with 'index' and 'similarity' keys
        """
        similarities = []
        for i, candidate in enumerate(candidate_embeddings):
            similarity = self.calculate_similarity(query_embedding, candidate)
            similarities.append({
                'index': i,
                'similarity': similarity
            })
        
        # Sort by similarity in descending order
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Return top_k results
        return similarities[:top_k]
    
    def _generate_mock_embedding(self, text: str) -> List[float]:
        """
        Generate a mock embedding when the API is not available.
        
        Args:
            text: The input text to generate a mock embedding for
            
        Returns:
            A mock embedding vector
        """
        # Create a deterministic mock embedding based on the text
        # This ensures the same text always produces the same mock embedding
        text_hash = hash(text) % (2**32)
        np.random.seed(text_hash)
        
        # Generate a vector of 128 dimensions (common for embeddings)
        embedding = np.random.random(128).tolist()
        
        # Normalize the embedding
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = [val / norm for val in embedding]
        
        return embedding
    
    def generate_user_knowledge_embedding(self, user_progress_data: Dict[str, Any]) -> List[float]:
        """
        Generate an embedding representing a user's knowledge state.
        
        Args:
            user_progress_data: Dictionary containing user progress information
            
        Returns:
            An embedding vector representing the user's knowledge state
        """
        # Create a textual representation of the user's knowledge state
        knowledge_segments = []
        
        # Add information about completed lessons/modules
        if 'completed_modules' in user_progress_data:
            completed_modules = user_progress_data['completed_modules']
            knowledge_segments.append(f"Completed modules: {', '.join(completed_modules)}")
        
        if 'completed_lessons' in user_progress_data:
            completed_lessons = user_progress_data['completed_lessons']
            knowledge_segments.append(f"Completed lessons: {', '.join(completed_lessons)}")
        
        # Add information about strengths and weaknesses
        if 'strengths' in user_progress_data:
            strengths = user_progress_data['strengths']
            knowledge_segments.append(f"Strengths: {', '.join(strengths)}")
        
        if 'weaknesses' in user_progress_data:
            weaknesses = user_progress_data['weaknesses']
            knowledge_segments.append(f"Weaknesses: {', '.join(weaknesses)}")
        
        # Add overall score information
        if 'overall_score' in user_progress_data:
            score = user_progress_data['overall_score']
            knowledge_segments.append(f"Overall performance score: {score}")
        
        # Combine all knowledge segments into one text
        knowledge_text = " ".join(knowledge_segments)
        
        # Generate embedding for the knowledge text
        return self.generate_embedding(knowledge_text)
    
    def generate_content_embedding(self, content_data: Dict[str, Any]) -> List[float]:
        """
        Generate an embedding for content (lesson, module, etc.).
        
        Args:
            content_data: Dictionary containing content information
            
        Returns:
            An embedding vector representing the content
        """
        # Create a textual representation of the content
        content_segments = []
        
        # Add title and description
        if 'title' in content_data:
            content_segments.append(f"Title: {content_data['title']}")
        
        if 'description' in content_data:
            content_segments.append(f"Description: {content_data['description']}")
        
        # Add content type information
        if 'type' in content_data:
            content_segments.append(f"Type: {content_data['type']}")
        
        # Add concepts covered
        if 'concepts' in content_data:
            concepts = content_data['concepts']
            if isinstance(concepts, list):
                content_segments.append(f"Concepts: {', '.join(concepts)}")
            else:
                content_segments.append(f"Concepts: {concepts}")
        
        # Add difficulty level
        if 'difficulty' in content_data:
            content_segments.append(f"Difficulty: {content_data['difficulty']}")
        
        # Combine all content segments into one text
        content_text = " ".join(content_segments)
        
        # Generate embedding for the content text
        return self.generate_embedding(content_text)


# Global instance
embedding_service = EmbeddingService()