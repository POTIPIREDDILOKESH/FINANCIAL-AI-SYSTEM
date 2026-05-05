"""
Embedder module for generating embeddings using Sentence-Transformers.
"""

from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np


class Embedder:
    """Generate embeddings for text using pre-trained models."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedder with a pre-trained model.
        
        Args:
            model_name: Name of the sentence-transformer model
        """
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """
        Encode a list of texts into embeddings.
        
        Args:
            texts: List of text strings to encode
            
        Returns:
            numpy array of embeddings with shape (n_texts, embedding_dim)
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings
    
    def encode_single(self, text: str) -> np.ndarray:
        """
        Encode a single text into an embedding.
        
        Args:
            text: Text string to encode
            
        Returns:
            numpy array of embedding with shape (embedding_dim,)
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def get_dimension(self) -> int:
        """Get the embedding dimension."""
        return self.embedding_dim
