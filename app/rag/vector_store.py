"""
Vector store using FAISS for efficient similarity search.
"""

import faiss
import numpy as np
from typing import List, Tuple, Optional
import pickle
import os


class VectorStore:
    """FAISS-based vector store for efficient similarity search."""
    
    def __init__(self, embedding_dim: int):
        """
        Initialize FAISS vector store.
        
        Args:
            embedding_dim: Dimension of embeddings
        """
        self.embedding_dim = embedding_dim
        self.index = faiss.IndexFlatL2(embedding_dim)
        self.documents = []
        self.metadata = []
    
    def add_documents(self, embeddings: np.ndarray, texts: List[str], 
                     metadata: Optional[List[dict]] = None):
        """
        Add documents with their embeddings to the store.
        
        Args:
            embeddings: numpy array of shape (n_docs, embedding_dim)
            texts: List of text documents
            metadata: Optional list of metadata dicts for each document
        """
        if embeddings.shape[0] != len(texts):
            raise ValueError("Number of embeddings must match number of texts")
        
        # Convert to float32 if needed
        embeddings = embeddings.astype(np.float32)
        
        # Add to FAISS index
        self.index.add(embeddings)
        
        # Store documents and metadata
        self.documents.extend(texts)
        
        if metadata is None:
            metadata = [{} for _ in texts]
        
        self.metadata.extend(metadata)
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Tuple[str, float]]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query embedding of shape (embedding_dim,)
            k: Number of results to return
            
        Returns:
            List of (document, distance) tuples
        """
        # Reshape query and convert to float32
        query = query_embedding.astype(np.float32).reshape(1, -1)
        
        # Search
        distances, indices = self.index.search(query, k)
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.documents):
                results.append((self.documents[idx], float(distance)))
        
        return results
    
    def search_with_metadata(self, query_embedding: np.ndarray, k: int = 5) -> List[dict]:
        """
        Search and return documents with metadata.
        
        Args:
            query_embedding: Query embedding
            k: Number of results
            
        Returns:
            List of dicts with 'document', 'distance', and 'metadata'
        """
        results = self.search(query_embedding, k)
        
        result_dicts = []
        for doc, distance in results:
            # Find document index
            doc_idx = self.documents.index(doc)
            result_dicts.append({
                'document': doc,
                'distance': distance,
                'metadata': self.metadata[doc_idx]
            })
        
        return result_dicts
    
    def get_size(self) -> int:
        """Get number of documents in the store."""
        return self.index.ntotal
    
    def save(self, filepath: str):
        """Save vector store to disk."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save FAISS index
        faiss_path = filepath + '.faiss'
        faiss.write_index(self.index, faiss_path)
        
        # Save documents and metadata
        metadata_path = filepath + '.pkl'
        with open(metadata_path, 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'metadata': self.metadata
            }, f)
    
    def load(self, filepath: str):
        """Load vector store from disk."""
        # Load FAISS index
        faiss_path = filepath + '.faiss'
        self.index = faiss.read_index(faiss_path)
        
        # Load documents and metadata
        metadata_path = filepath + '.pkl'
        with open(metadata_path, 'rb') as f:
            data = pickle.load(f)
            self.documents = data['documents']
            self.metadata = data['metadata']
