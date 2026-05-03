# embedder.py

"""
FAISS Embedder for RAG
Converts clauses to vectors → stores in FAISS → enables semantic search.

RAG Concept:
1. User asks question
2. Convert question to vector
3. Find similar vectors in FAISS (semantically related clauses)
4. Feed those clauses as context to LLM for answer
"""

import numpy as np
import pickle
from typing import List, Tuple
from sentence_transformers import SentenceTransformer
import faiss
import os


class ContractRAG:
    """
    RAG system for contract Q&A using FAISS.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedder and FAISS index.
        
        Args:
            model_name: Sentence transformer model
                "all-MiniLM-L6-v2" = fast, good quality, 384 dims
        """
        self.model = SentenceTransformer(model_name)
        self.vector_dim = 384  # For MiniLM model
        self.index = faiss.IndexFlatL2(self.vector_dim)  # L2 distance
        self.chunks = []  # Store actual text
        self.vectors = None
    
    def add_chunks(self, chunks: List[dict]):
        """
        Embed chunks and add to FAISS index.
        
        Args:
            chunks: List of chunk dicts with 'content' field
        """
        print(f"Embedding {len(chunks)} chunks...")
        
        texts = [chunk['content'] for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.model.encode(texts, show_progress_bar=True)
        embeddings = np.array(embeddings).astype('float32')
        
        # Add to FAISS
        self.index.add(embeddings)
        self.vectors = embeddings
        self.chunks = chunks
        
        print(f"Added {len(chunks)} vectors to FAISS index")
    
    def search(self, query: str, top_k: int = 3) -> List[Tuple[dict, float]]:
        """
        Search for chunks similar to query.
        
        Args:
            query: User question/search text
            top_k: Return top K results
            
        Returns:
            List of (chunk_dict, similarity_score) tuples
        """
        if not self.chunks:
            return []
        
        # Embed query
        query_vector = self.model.encode([query])[0].astype('float32')
        query_vector = np.array([query_vector])
        
        # Search FAISS
        distances, indices = self.index.search(query_vector, top_k)
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.chunks):
                # Convert L2 distance to similarity score (0-1)
                similarity = 1 / (1 + distance)
                results.append((self.chunks[idx], similarity))
        
        return results
    
    def save(self, directory: str = "./rag_index"):
        """
        Save FAISS index and chunks to disk.
        
        Args:
            directory: Directory to save files
        """
        os.makedirs(directory, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, f"{directory}/faiss.index")
        
        # Save chunks and model info
        with open(f"{directory}/chunks.pkl", "wb") as f:
            pickle.dump(self.chunks, f)
        
        print(f"RAG index saved to {directory}")
    
    def load(self, directory: str = "./rag_index"):
        """
        Load FAISS index and chunks from disk.
        
        Args:
            directory: Directory with saved files
        """
        self.index = faiss.read_index(f"{directory}/faiss.index")
        
        with open(f"{directory}/chunks.pkl", "rb") as f:
            self.chunks = pickle.load(f)
        
        print(f"RAG index loaded from {directory}")