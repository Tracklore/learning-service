"""
Vector database service for storing and searching embeddings.
This is a simulated implementation that demonstrates the interface
that would be used with a real vector database like Pinecone, Weaviate, or Qdrant.
"""

import json
import os
from typing import List, Dict, Any, Optional
from app.utils.logger import get_logger
from app.llm.embeddings import embedding_service

logger = get_logger(__name__)

class VectorDBService:
    """Service for interacting with a vector database."""
    
    def __init__(self, db_path: str = "./vector_store.json"):
        """Initialize the Vector Database Service."""
        self.db_path = db_path
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        """Load vector data from file."""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load vector store from {self.db_path}: {e}")
                return {"embeddings": {}, "metadata": {}}
        else:
            return {"embeddings": {}, "metadata": {}}
    
    def _save_data(self):
        """Save vector data to file."""
        try:
            with open(self.db_path, 'w') as f:
                json.dump(self.data, f)
        except Exception as e:
            logger.error(f"Could not save vector store to {self.db_path}: {e}")
    
    def upsert_embedding(self, 
                        id: str, 
                        embedding: List[float], 
                        metadata: Dict[str, Any],
                        namespace: str = "default") -> bool:
        """
        Upsert an embedding into the vector database.
        
        Args:
            id: Unique identifier for the embedding
            embedding: The embedding vector
            metadata: Additional metadata to store with the embedding
            namespace: Namespace for organizing embeddings
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure namespace exists
            if namespace not in self.data["embeddings"]:
                self.data["embeddings"][namespace] = {}
                self.data["metadata"][namespace] = {}
            
            # Store embedding and metadata
            self.data["embeddings"][namespace][id] = embedding
            self.data["metadata"][namespace][id] = metadata
            
            # Save to file
            self._save_data()
            
            logger.info(f"Upserted embedding with ID {id} in namespace {namespace}")
            return True
        except Exception as e:
            logger.error(f"Error upserting embedding {id}: {e}")
            return False
    
    def upsert_user_knowledge_state(self, 
                                   user_id: str, 
                                   knowledge_embedding: List[float], 
                                   subject: str) -> bool:
        """
        Upsert a user's knowledge state embedding into the database.
        
        Args:
            user_id: The ID of the user
            knowledge_embedding: The embedding representing the user's knowledge state
            subject: The subject for which this knowledge state applies
            
        Returns:
            True if successful, False otherwise
        """
        metadata = {
            "user_id": user_id,
            "subject": subject,
            "type": "user_knowledge_state",
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        
        embedding_id = f"user_knowledge_{user_id}_{subject}"
        return self.upsert_embedding(embedding_id, knowledge_embedding, metadata, "users")
    
    def upsert_content_embedding(self, 
                                content_id: str, 
                                content_embedding: List[float], 
                                content_type: str, 
                                subject: str,
                                metadata: Dict[str, Any]) -> bool:
        """
        Upsert a content embedding into the database.
        
        Args:
            content_id: The ID of the content
            content_embedding: The embedding representing the content
            content_type: Type of content (lesson, module, etc.)
            subject: Subject of the content
            metadata: Additional metadata
            
        Returns:
            True if successful, False otherwise
        """
        full_metadata = {
            "content_id": content_id,
            "content_type": content_type,
            "subject": subject,
            "type": "content",
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        full_metadata.update(metadata)  # Add any additional metadata
        
        embedding_id = f"content_{content_id}"
        return self.upsert_embedding(embedding_id, content_embedding, full_metadata, "content")
    
    def search(self, 
              query_embedding: List[float], 
              top_k: int = 10, 
              namespace: str = "default",
              filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for similar embeddings to the query embedding.
        
        Args:
            query_embedding: The embedding to search for similar items to
            top_k: Number of results to return
            namespace: Namespace to search in
            filters: Optional filters to apply to metadata
            
        Returns:
            List of dictionaries with 'id', 'similarity', 'metadata', and 'embedding' keys
        """
        if namespace not in self.data["embeddings"]:
            return []
        
        # Get all embeddings in the namespace
        candidate_embeddings = self.data["embeddings"][namespace]
        candidate_metadata = self.data["metadata"][namespace]
        
        # Calculate similarities
        results = []
        for embedding_id, embedding in candidate_embeddings.items():
            # Apply filters if provided
            if filters:
                metadata = candidate_metadata[embedding_id]
                match = True
                for filter_key, filter_value in filters.items():
                    if metadata.get(filter_key) != filter_value:
                        match = False
                        break
                if not match:
                    continue
            
            # Calculate similarity using the embedding service
            similarity = embedding_service.calculate_similarity(query_embedding, embedding)
            
            results.append({
                "id": embedding_id,
                "similarity": similarity,
                "metadata": candidate_metadata[embedding_id],
                "embedding": embedding
            })
        
        # Sort by similarity in descending order
        results.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Return top_k results
        return results[:top_k]
    
    def find_similar_users(self, 
                          user_knowledge_embedding: List[float], 
                          subject: str, 
                          top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find users with similar knowledge states.
        
        Args:
            user_knowledge_embedding: The embedding representing a user's knowledge state
            subject: The subject to compare knowledge states for
            top_k: Number of similar users to return
            
        Returns:
            List of dictionaries with user information and similarity scores
        """
        filters = {
            "subject": subject,
            "type": "user_knowledge_state"
        }
        
        results = self.search(
            query_embedding=user_knowledge_embedding,
            top_k=top_k,
            namespace="users",
            filters=filters
        )
        
        # Format the results appropriately
        similar_users = []
        for result in results:
            user_id = result["metadata"]["user_id"]
            similarity = result["similarity"]
            
            similar_users.append({
                "user_id": user_id,
                "similarity": similarity
            })
        
        return similar_users
    
    def find_relevant_content(self, 
                             query_embedding: List[float], 
                             subject: str, 
                             content_type: Optional[str] = None,
                             top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find content relevant to the query embedding.
        
        Args:
            query_embedding: The embedding representing the knowledge or query
            subject: The subject area to search in
            content_type: Optional content type to filter by
            top_k: Number of relevant content items to return
            
        Returns:
            List of dictionaries with content information and relevance scores
        """
        filters = {
            "subject": subject,
            "type": "content"
        }
        
        if content_type:
            filters["content_type"] = content_type
        
        results = self.search(
            query_embedding=query_embedding,
            top_k=top_k,
            namespace="content",
            filters=filters
        )
        
        # Format the results appropriately
        relevant_content = []
        for result in results:
            content_id = result["metadata"]["content_id"]
            similarity = result["similarity"]
            content_type = result["metadata"]["content_type"]
            
            relevant_content.append({
                "content_id": content_id,
                "content_type": content_type,
                "similarity": similarity,
                "metadata": result["metadata"]
            })
        
        return relevant_content
    
    def get_embedding_by_id(self, id: str, namespace: str = "default") -> Optional[List[float]]:
        """
        Retrieve an embedding by its ID.
        
        Args:
            id: The ID of the embedding
            namespace: The namespace to look in
            
        Returns:
            The embedding vector if found, None otherwise
        """
        if namespace in self.data["embeddings"]:
            return self.data["embeddings"][namespace].get(id)
        return None
    
    def delete_embedding(self, id: str, namespace: str = "default") -> bool:
        """
        Delete an embedding by its ID.
        
        Args:
            id: The ID of the embedding to delete
            namespace: The namespace to delete from
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            if namespace in self.data["embeddings"]:
                if id in self.data["embeddings"][namespace]:
                    del self.data["embeddings"][namespace][id]
                    if id in self.data["metadata"][namespace]:
                        del self.data["metadata"][namespace][id]
                    
                    # Save changes
                    self._save_data()
                    logger.info(f"Deleted embedding with ID {id} from namespace {namespace}")
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error deleting embedding {id}: {e}")
            return False


# Global instance
vector_db_service = VectorDBService()