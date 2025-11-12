"""
Simple Vector Store Module - No ChromaDB Dependencies
Uses OpenAI embeddings and simple similarity search
"""

import os
import json
import numpy as np
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime
import openai
import sys


class SimpleVectorStore:
    """Simple vector store using OpenAI embeddings and JSON storage"""
    
    def __init__(self, persist_directory: str = "./data/vector_db"):
        """Initialize the simple vector store"""
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        self.db_file = self.persist_directory / "documents.json"
        self.qa_file = self.persist_directory / "qa_history.json"
        
        print(f"[VECTOR_STORE] Initializing with directory: {self.persist_directory}", file=sys.stderr, flush=True)
        print(f"[VECTOR_STORE] DB file: {self.db_file}", file=sys.stderr, flush=True)
        print(f"[VECTOR_STORE] DB file exists: {self.db_file.exists()}", file=sys.stderr, flush=True)
        
        self.documents = self._load_documents()
        self.qa_history = self._load_qa_history()
        
        print(f"[VECTOR_STORE] Loaded {len(self.documents)} documents", file=sys.stderr, flush=True)
        print(f"[VECTOR_STORE] Document IDs: {list(self.documents.keys())[:5]}...", file=sys.stderr, flush=True)
        
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
                print(f"[VECTOR_STORE] Loading documents from {self.db_file}", file=sys.stderr, flush=True)
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    docs = json.load(f)
                    print(f"[VECTOR_STORE] Loaded {len(docs)} documents from file", file=sys.stderr, flush=True)
                    return docs
            except Exception as e:
                print(f"[VECTOR_STORE] ERROR loading documents: {e}", file=sys.stderr, flush=True)
                return {}
        else:
            print(f"[VECTOR_STORE] DB file does not exist, starting with empty store", file=sys.stderr, flush=True)
        return {}
    
    def _save_documents(self):
        """Save documents to JSON file"""
        import sys
        try:
            print(f"[VECTOR_STORE] Saving {len(self.documents)} documents to {self.db_file}", file=sys.stderr, flush=True)
            print(f"[VECTOR_STORE] Parent directory exists: {self.db_file.parent.exists()}", file=sys.stderr, flush=True)
            print(f"[VECTOR_STORE] Parent directory: {self.db_file.parent}", file=sys.stderr, flush=True)
            
            # Ensure parent directory exists
            self.db_file.parent.mkdir(parents=True, exist_ok=True)
            print(f"[VECTOR_STORE] Directory created/verified", file=sys.stderr, flush=True)
            
            # Write to a temporary file first, then rename (atomic operation)
            temp_file = self.db_file.with_suffix('.json.tmp')
            print(f"[VECTOR_STORE] Writing to temp file: {temp_file}", file=sys.stderr, flush=True)
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.documents, f, indent=2)
                f.flush()
                os.fsync(f.fileno())  # Force write to disk
            print(f"[VECTOR_STORE] Temp file written, size: {temp_file.stat().st_size} bytes", file=sys.stderr, flush=True)
            
            # Atomic rename
            temp_file.replace(self.db_file)
            print(f"[VECTOR_STORE] Renamed temp file to {self.db_file}", file=sys.stderr, flush=True)
            
            # Verify file was written
            if self.db_file.exists():
                file_size = self.db_file.stat().st_size
                print(f"[VECTOR_STORE] Successfully saved documents (file size: {file_size} bytes)", file=sys.stderr, flush=True)
            else:
                raise Exception(f"File was not created at {self.db_file}")
                
        except Exception as e:
            print(f"[VECTOR_STORE] ERROR saving documents: {e}", file=sys.stderr, flush=True)
            import traceback
            traceback.print_exc(file=sys.stderr)
            raise
    
    def _load_qa_history(self) -> Dict:
        """Load Q&A history from JSON file"""
        if self.qa_file.exists():
            try:
                with open(self.qa_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_qa_history(self):
        """Save Q&A history to JSON file"""
        with open(self.qa_file, 'w', encoding='utf-8') as f:
            json.dump(self.qa_history, f, indent=2)
    
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
            print(f"[VECTOR_STORE] About to save documents to disk...", file=sys.stderr, flush=True)
            self._save_documents()
            print(f"[VECTOR_STORE] Documents saved successfully", file=sys.stderr, flush=True)
            
            print(f"Added document {doc_id} with {len(chunks)} chunks", file=sys.stderr, flush=True)
        
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
    
    def save_qa(self, qa_id: str, question: str, answer: str, sources: List[Dict], 
                project_id: str, confidence: float = 0.0, row_number: Optional[int] = None) -> None:
        """Save a Q&A pair"""
        if project_id not in self.qa_history:
            self.qa_history[project_id] = []
        
        qa_entry = {
            'id': qa_id,
            'question': question,
            'answer': answer,
            'sources': sources,
            'confidence': confidence,
            'created_at': datetime.now().isoformat(),
            'row_number': row_number
        }
        
        self.qa_history[project_id].append(qa_entry)
        self._save_qa_history()
    
    def list_qa(self, project_id: str) -> List[Dict]:
        """List all Q&A pairs for a project"""
        if project_id in self.qa_history:
            return self.qa_history[project_id]
        return []
    
    def delete_qa(self, qa_id: str, project_id: str) -> bool:
        """Delete a specific Q&A entry"""
        if project_id not in self.qa_history:
            return False
        
        # Find and remove the Q&A entry
        qa_list = self.qa_history[project_id]
        original_length = len(qa_list)
        self.qa_history[project_id] = [qa for qa in qa_list if qa.get('id') != qa_id]
        
        if len(self.qa_history[project_id]) < original_length:
            # Renumber remaining rows
            for i, qa in enumerate(self.qa_history[project_id]):
                qa['row_number'] = i + 1
            self._save_qa_history()
            return True
        return False
    
    def delete_project_qa(self, project_id: str) -> bool:
        """Delete all Q&A for a project"""
        if project_id in self.qa_history:
            del self.qa_history[project_id]
            self._save_qa_history()
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

