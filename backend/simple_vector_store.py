"""
Simple Vector Store Module - No ChromaDB Dependencies
Uses OpenAI embeddings and simple similarity search
"""

import os
import json
import numpy as np
from typing import List, Dict, Optional
from pathlib import Path
import openai


class SimpleVectorStore:
    """Simple vector store using OpenAI embeddings and JSON storage"""
    
    def __init__(self, persist_directory: str = "./data/vector_db"):
        """Initialize the simple vector store"""
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        self.db_file = self.persist_directory / "documents.json"
        self.documents = self._load_documents()
        
        # Set OpenAI API key
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
        
        self.chunk_size = int(os.getenv("CHUNK_SIZE", 1000))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 200))
    
    def _load_documents(self) -> Dict:
        """Load documents from JSON file"""
        if self.db_file.exists():
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_documents(self):
        """Save documents to JSON file"""
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.documents, f, indent=2)
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding from OpenAI using v1.0+ API"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            response = client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * 1536
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        a_np = np.array(a)
        b_np = np.array(b)
        
        norm_a = np.linalg.norm(a_np)
        norm_b = np.linalg.norm(b_np)
        
        # Handle zero vectors
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        similarity = float(np.dot(a_np, b_np) / (norm_a * norm_b))
        
        # Ensure valid range [-1, 1] and handle NaN
        if np.isnan(similarity) or np.isinf(similarity):
            return 0.0
        
        return max(-1.0, min(1.0, similarity))
    
    def add_document(self, doc_id: str, text: str, metadata: Dict, project_id: str = "default") -> None:
        """Add a document to the vector store"""
        try:
            # Add project_id to metadata
            metadata['project_id'] = project_id
            
            # Split text into chunks
            chunks = self._chunk_text(text, self.chunk_size, self.chunk_overlap)
            
            # Create document entry
            if doc_id not in self.documents:
                self.documents[doc_id] = {
                    'metadata': metadata,
                    'chunks': []
                }
            
            # Process each chunk
            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    # Get embedding
                    embedding = self._get_embedding(chunk)
                    
                    # Store chunk with embedding
                    self.documents[doc_id]['chunks'].append({
                        'index': i,
                        'text': chunk,
                        'embedding': embedding
                    })
            
            # Save to disk
            self._save_documents()
            
            print(f"Added document {doc_id} with {len(chunks)} chunks")
        
        except Exception as e:
            raise Exception(f"Failed to add document: {str(e)}")
    
    def search(self, query: str, document_ids: Optional[List[str]] = None, 
               top_k: int = 5, project_id: Optional[str] = None) -> List[Dict]:
        """Search for relevant document chunks"""
        try:
            # Get query embedding
            query_embedding = self._get_embedding(query)
            
            # Collect all chunks
            results = []
            
            for doc_id, doc_data in self.documents.items():
                # Filter by project_id if provided
                if project_id and doc_data['metadata'].get('project_id') != project_id:
                    continue
                
                # Filter by document_ids if provided
                if document_ids and doc_id not in document_ids:
                    continue
                
                # Search through chunks
                for chunk in doc_data['chunks']:
                    similarity = self._cosine_similarity(
                        query_embedding,
                        chunk['embedding']
                    )
                    
                    results.append({
                        'text': chunk['text'],
                        'metadata': {
                            **doc_data['metadata'],
                            'doc_id': doc_id,
                            'chunk_index': chunk['index']
                        },
                        'score': similarity,
                        'rank': 0
                    })
            
            # Sort by similarity
            results.sort(key=lambda x: x['score'], reverse=True)
            
            # Add rank
            for i, result in enumerate(results[:top_k]):
                result['rank'] = i + 1
            
            return results[:top_k]
        
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def get_document(self, doc_id: str) -> Optional[Dict]:
        """Get document metadata by ID"""
        if doc_id in self.documents:
            return self.documents[doc_id]['metadata']
        return None
    
    def list_documents(self, project_id: Optional[str] = None) -> List[Dict]:
        """List all documents, optionally filtered by project"""
        documents = []
        for doc_id, doc_data in self.documents.items():
            # Filter by project_id if provided
            if project_id and doc_data['metadata'].get('project_id') != project_id:
                continue
            
            metadata = doc_data['metadata'].copy()
            metadata['id'] = doc_id
            documents.append(metadata)
        
        # Sort by upload date
        documents.sort(
            key=lambda x: x.get('upload_date', ''),
            reverse=True
        )
        
        return documents
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document"""
        if doc_id in self.documents:
            del self.documents[doc_id]
            self._save_documents()
            print(f"Deleted document {doc_id}")
            return True
        return False
    
    def _chunk_text(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Split text into overlapping chunks"""
        if not text:
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            
            # Try to break at sentence or word boundary
            if end < text_length:
                search_start = max(start, end - 100)
                last_period = text.rfind('.', search_start, end)
                last_newline = text.rfind('\n', search_start, end)
                
                break_point = max(last_period, last_newline)
                if break_point > start:
                    end = break_point + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap if end < text_length else text_length
        
        return chunks

