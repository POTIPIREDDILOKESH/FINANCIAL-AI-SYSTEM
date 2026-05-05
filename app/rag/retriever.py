"""
Retriever for RAG system - retrieves relevant documents from vector store.
"""

from typing import List, Optional
import os
from .embedder import Embedder
from .vector_store import VectorStore


class RAGRetriever:
    """Retrieves relevant documents from the vector store based on queries."""
    
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize the RAG retriever.
        
        Args:
            embedding_model: Name of the sentence-transformer model
        """
        self.embedder = Embedder(embedding_model)
        self.vector_store = VectorStore(self.embedder.get_dimension())
        self.initialized = False
    
    def initialize_from_documents(self, documents: List[str], chunk_size: int = 500, 
                                  overlap: int = 100):
        """
        Initialize the retriever from a list of documents.
        Chunks long documents for better retrieval.
        
        Args:
            documents: List of document texts
            chunk_size: Size of text chunks in characters
            overlap: Overlap between chunks
        """
        # Chunk documents
        chunks = []
        metadata = []
        
        for doc_idx, doc in enumerate(documents):
            # Simple chunking by character count
            for i in range(0, len(doc), chunk_size - overlap):
                chunk = doc[i:i + chunk_size]
                if len(chunk.strip()) > 0:
                    chunks.append(chunk)
                    metadata.append({
                        'source_doc': doc_idx,
                        'chunk_start': i
                    })
        
        # Generate embeddings
        embeddings = self.embedder.encode(chunks)
        
        # Add to vector store
        self.vector_store.add_documents(embeddings, chunks, metadata)
        self.initialized = True
    
    def initialize_from_docs_file(self, filepath: str, separator: str = "---", 
                                  chunk_size: int = 500, overlap: int = 100):
        """
        Initialize from a file with documents separated by a delimiter.
        
        Args:
            filepath: Path to the documents file
            separator: Separator between documents
            chunk_size: Size of text chunks
            overlap: Overlap between chunks
        """
        # Read and split documents
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by common document separators
        if separator in content:
            documents = content.split(separator)
        else:
            # If no separator found, treat entire file as one document
            # and split by sections (looking for numbered documents)
            documents = [content]
        
        # Clean documents
        documents = [doc.strip() for doc in documents if doc.strip()]
        
        self.initialize_from_documents(documents, chunk_size, overlap)
    
    def retrieve(self, query: str, k: int = 5) -> List[dict]:
        """
        Retrieve top-k relevant documents for a query.
        
        Args:
            query: Query string
            k: Number of results to return
            
        Returns:
            List of dicts with 'document', 'distance', 'metadata'
        """
        if not self.initialized:
            raise RuntimeError("Retriever not initialized. Call initialize_from_documents first.")
        
        # Embed query
        query_embedding = self.embedder.encode_single(query)
        
        # Search
        results = self.vector_store.search_with_metadata(query_embedding, k)
        
        return results
    
    def retrieve_text_only(self, query: str, k: int = 5) -> List[str]:
        """
        Retrieve top-k documents as text only.
        
        Args:
            query: Query string
            k: Number of results
            
        Returns:
            List of document texts
        """
        results = self.retrieve(query, k)
        return [r['document'] for r in results]
    
    def get_store_info(self) -> dict:
        """Get information about the vector store."""
        return {
            'initialized': self.initialized,
            'num_documents': self.vector_store.get_size(),
            'embedding_dim': self.embedder.get_dimension()
        }
