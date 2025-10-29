"""
Vector Store Module
Handles document embeddings storage and semantic search using ChromaDB
"""

import os
from typing import List, Dict, Optional
import uuid
from pathlib import Path

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False


class VectorStore:
    """Manage document embeddings and semantic search"""
    
    def __init__(self, persist_directory: str = "./data/vector_db"):
        """
        Initialize the vector store
        
        Args:
            persist_directory: Directory to persist the vector database
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError("chromadb not installed. Install with: pip install chromadb")
        
        # Create directory if it doesn't exist
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection with OpenAI embeddings (no onnxruntime needed)
        try:
            from chromadb.utils import embedding_functions
            
            # Use OpenAI embeddings if API key is available
            openai_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY")
            if openai_key:
                # Use OpenAI embedding function
                embedding_function = embedding_functions.OpenAIEmbeddingFunction(
                    api_key=openai_key,
                    model_name="text-embedding-ada-002"
                )
            else:
                # Fallback to sentence transformers (requires onnxruntime)
                embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="all-MiniLM-L6-v2"
                )
            
            self.collection = self.client.get_or_create_collection(
                name="diligence_documents",
                embedding_function=embedding_function,
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            print(f"Error creating collection with embedding function: {e}")
            print("Trying without custom embedding function...")
            # If collection exists but with different settings, delete and recreate
            try:
                self.client.delete_collection("diligence_documents")
                # Create without embedding function as last resort
                self.collection = self.client.create_collection(
                    name="diligence_documents",
                    metadata={"hnsw:space": "cosine"}
                )
            except Exception as e2:
                raise Exception(f"Failed to initialize collection: {e2}")
        
        self.chunk_size = int(os.getenv("CHUNK_SIZE", 1000))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 200))
    
    def add_document(self, doc_id: str, text: str, metadata: Dict) -> None:
        """
        Add a document to the vector store
        
        Args:
            doc_id: Unique document identifier
            text: Document text content
            metadata: Document metadata (filename, type, pages, etc.)
        """
        try:
            # Split text into chunks
            chunks = self._chunk_text(text, self.chunk_size, self.chunk_overlap)
            
            # Prepare data for ChromaDB
            chunk_ids = []
            documents = []
            metadatas = []
            
            for i, chunk in enumerate(chunks):
                if chunk.strip():  # Only add non-empty chunks
                    chunk_id = f"{doc_id}_chunk_{i}"
                    chunk_ids.append(chunk_id)
                    documents.append(chunk)
                    metadatas.append({
                        **metadata,
                        'doc_id': doc_id,
                        'chunk_index': i,
                        'total_chunks': len(chunks)
                    })
            
            # Add to collection
            if chunk_ids:
                self.collection.add(
                    ids=chunk_ids,
                    documents=documents,
                    metadatas=metadatas
                )
                
                print(f"Added document {doc_id} with {len(chunk_ids)} chunks")
        
        except Exception as e:
            raise Exception(f"Failed to add document to vector store: {str(e)}")
    
    def search(self, query: str, document_ids: Optional[List[str]] = None, 
               top_k: int = 5) -> List[Dict]:
        """
        Search for relevant document chunks
        
        Args:
            query: Search query
            document_ids: Optional list of document IDs to search within
            top_k: Number of top results to return
            
        Returns:
            List of relevant document chunks with metadata and scores
        """
        try:
            # Prepare query filter
            where_filter = None
            if document_ids:
                where_filter = {"doc_id": {"$in": document_ids}}
            
            # Perform search
            results = self.collection.query(
                query_texts=[query],
                n_results=min(top_k, self.collection.count()),
                where=where_filter
            )
            
            # Format results
            relevant_docs = []
            
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    # Convert distance to similarity score (0-1, higher is better)
                    similarity = 1 / (1 + distance)
                    
                    relevant_docs.append({
                        'text': doc,
                        'metadata': metadata,
                        'score': similarity,
                        'rank': i + 1
                    })
            
            return relevant_docs
        
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def get_document(self, doc_id: str) -> Optional[Dict]:
        """
        Get document metadata by ID
        
        Args:
            doc_id: Document identifier
            
        Returns:
            Document metadata or None if not found
        """
        try:
            # Query for all chunks of this document
            results = self.collection.get(
                where={"doc_id": doc_id},
                limit=1
            )
            
            if results['metadatas']:
                # Return first chunk's metadata (all chunks have same doc metadata)
                metadata = results['metadatas'][0].copy()
                
                # Remove chunk-specific fields
                metadata.pop('chunk_index', None)
                metadata.pop('total_chunks', None)
                
                return metadata
            
            return None
        
        except Exception as e:
            print(f"Error getting document: {e}")
            return None
    
    def list_documents(self) -> List[Dict]:
        """
        List all documents in the vector store
        
        Returns:
            List of document metadata dictionaries
        """
        try:
            # Get all items from collection
            all_results = self.collection.get()
            
            # Extract unique documents
            seen_docs = set()
            documents = []
            
            for metadata in all_results['metadatas']:
                doc_id = metadata.get('doc_id')
                if doc_id and doc_id not in seen_docs:
                    seen_docs.add(doc_id)
                    
                    # Create clean metadata dict
                    doc_metadata = {
                        'id': doc_id,
                        'filename': metadata.get('filename', 'Unknown'),
                        'file_type': metadata.get('file_type', 'unknown'),
                        'pages': metadata.get('pages'),
                        'upload_date': metadata.get('upload_date'),
                        'size': metadata.get('size')
                    }
                    documents.append(doc_metadata)
            
            # Sort by upload date (newest first)
            documents.sort(
                key=lambda x: x.get('upload_date', ''),
                reverse=True
            )
            
            return documents
        
        except Exception as e:
            print(f"Error listing documents: {e}")
            return []
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document and all its chunks
        
        Args:
            doc_id: Document identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get all chunk IDs for this document
            results = self.collection.get(
                where={"doc_id": doc_id}
            )
            
            if results['ids']:
                # Delete all chunks
                self.collection.delete(ids=results['ids'])
                print(f"Deleted document {doc_id} ({len(results['ids'])} chunks)")
                return True
            
            return False
        
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
    
    def _chunk_text(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            chunk_size: Maximum size of each chunk
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            # Get chunk end position
            end = start + chunk_size
            
            # If not the last chunk, try to break at sentence or word boundary
            if end < text_length:
                # Look for sentence end within last 100 chars
                search_start = max(start, end - 100)
                last_period = text.rfind('.', search_start, end)
                last_newline = text.rfind('\n', search_start, end)
                
                break_point = max(last_period, last_newline)
                if break_point > start:
                    end = break_point + 1
            
            # Extract chunk
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position for next chunk
            start = end - overlap if end < text_length else text_length
        
        return chunks
    
    def get_statistics(self) -> Dict:
        """
        Get vector store statistics
        
        Returns:
            Dictionary with statistics
        """
        try:
            count = self.collection.count()
            documents = self.list_documents()
            
            return {
                'total_chunks': count,
                'total_documents': len(documents),
                'collection_name': self.collection.name
            }
        except Exception as e:
            return {
                'error': str(e)
            }

