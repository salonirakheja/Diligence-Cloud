"""
Autonomous Diligence Cloud - Main FastAPI Application
Handles document upload, processing, and Q&A functionality
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import io
import pandas as pd
import time
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

# Import our custom modules
from document_processor import DocumentProcessor
from simple_vector_store import SimpleVectorStore
from multi_agent_system import OrchestratorAgent
from project_manager import ProjectManager
from telemetry import init_tracing

# Configuration
# Get the backend directory and project root
BACKEND_DIR = Path(__file__).parent
PROJECT_ROOT = BACKEND_DIR.parent

# Check if we're on Render (persistent disk mounted at /opt/render/project/src/data)
RENDER_DATA_DIR = Path("/opt/render/project/src/data")
if RENDER_DATA_DIR.exists():
    # Use Render's persistent disk
    DATA_DIR = RENDER_DATA_DIR
    print(f"[CONFIG] Using Render persistent disk: {DATA_DIR}")
else:
    # Use local data directory
    DATA_DIR = PROJECT_ROOT / "data"
    print(f"[CONFIG] Using local data directory: {DATA_DIR}")

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")

# Initialize Phoenix tracing (best effort)
telemetry_provider = init_tracing()

# Initialize FastAPI app
app = FastAPI(
    title="Autonomous Diligence Cloud",
    description="AI-powered document intelligence platform",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    """Log all incoming requests"""
    import time
    import sys
    start_time = time.time()
    print(f"[REQUEST] {request.method} {request.url.path} - Client: {request.client.host if request.client else 'unknown'}", file=sys.stderr, flush=True)
    if request.url.query:
        print(f"[REQUEST] Query params: {request.url.query}", file=sys.stderr, flush=True)
    print(f"[REQUEST] Headers: {dict(request.headers)}", file=sys.stderr, flush=True)
    
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"[REQUEST] {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s", file=sys.stderr, flush=True)
    return response

# Use persistent disk for uploads on Render, otherwise use backend/uploads
if RENDER_DATA_DIR.exists():
    UPLOAD_DIR = RENDER_DATA_DIR / "uploads"
else:
    UPLOAD_DIR = BACKEND_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
print(f"[CONFIG] Upload directory: {UPLOAD_DIR}")

# Initialize components
doc_processor = DocumentProcessor()
vector_store = SimpleVectorStore(persist_directory=str(DATA_DIR / "vector_db"))
project_manager = ProjectManager(projects_file=str(DATA_DIR / "projects.json"))
print(f"[CONFIG] Vector store directory: {DATA_DIR / 'vector_db'}")
print(f"[CONFIG] Projects file: {DATA_DIR / 'projects.json'}")

# Check for API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
AI_ENABLED = bool(OPENAI_API_KEY or OPENROUTER_API_KEY)

# Initialize Multi-Agent Orchestrator
orchestrator = None
if AI_ENABLED:
    # Use gpt-4o-mini for cost-effectiveness, or gpt-4 for highest quality
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    orchestrator = OrchestratorAgent(
        api_key=OPENAI_API_KEY or OPENROUTER_API_KEY,
        model=model
    )

# Pydantic models
class Question(BaseModel):
    question: str
    document_ids: Optional[List[str]] = None
    project_id: Optional[str] = None

class Answer(BaseModel):
    question: str
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    agents_used: Optional[List[str]] = []
    telemetry: Optional[Dict[str, Any]] = None

class BatchQuestion(BaseModel):
    questions: List[str]
    document_ids: Optional[List[str]] = None
    project_id: Optional[str] = None

class DocumentMetadata(BaseModel):
    id: str
    filename: str
    file_type: str
    pages: Optional[int] = None
    upload_date: str
    size: int

class Project(BaseModel):
    name: str
    description: Optional[str] = ""

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


# Routes

@app.get("/")
async def serve_landing():
    """Serve the landing page as homepage"""
    import sys
    print("=" * 80, file=sys.stderr)
    print("LANDING ROUTE HIT!!!", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    landing_path = PROJECT_ROOT / "frontend" / "landing.html"
    print(f"Landing path: {landing_path.absolute()}", file=sys.stderr)
    print(f"Exists: {landing_path.exists()}", file=sys.stderr)
    if landing_path.exists():
        print(f"RETURNING LANDING.HTML", file=sys.stderr)
        return FileResponse(
            path=str(landing_path.absolute()),
            media_type="text/html",
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
        )
    print(f"LANDING PAGE NOT FOUND!", file=sys.stderr)
    return {"message": "Landing page not found."}


@app.get("/app")
async def serve_frontend():
    """Serve the main application"""
    frontend_path = PROJECT_ROOT / "frontend" / "index.html"
    if frontend_path.exists():
        return FileResponse(
            path=str(frontend_path.absolute()),
            media_type="text/html"
        )
    return {"message": "Frontend not found. Please ensure frontend/index.html exists."}


@app.get("/health")
async def health_check():
    """Health check endpoint with debug info"""
    import sys
    return {
        "status": "healthy",
        "service": "autonomous-diligence-cloud",
        "version": "1.0.0",
        "ai_enabled": AI_ENABLED,
        "documents_count": len(vector_store.list_documents()),
        "projects_count": len(project_manager.list_projects()),
        "debug": {
            "data_dir": str(DATA_DIR),
            "data_dir_exists": DATA_DIR.exists(),
            "render_data_dir": str(RENDER_DATA_DIR),
            "render_data_dir_exists": RENDER_DATA_DIR.exists(),
            "vector_store_dir": str(DATA_DIR / "vector_db"),
            "vector_store_dir_exists": (DATA_DIR / "vector_db").exists(),
            "db_file": str(DATA_DIR / "vector_db" / "documents.json"),
            "db_file_exists": (DATA_DIR / "vector_db" / "documents.json").exists(),
            "upload_dir": str(UPLOAD_DIR),
            "upload_dir_exists": UPLOAD_DIR.exists(),
            "documents_in_memory": len(vector_store.documents),
            "telemetry_enabled": telemetry_provider is not None,
        }
    }

@app.get("/debug")
async def debug_info():
    """Debug endpoint to check configuration and state"""
    import sys
    return {
        "data_dir": str(DATA_DIR),
        "data_dir_exists": DATA_DIR.exists(),
        "render_data_dir": str(RENDER_DATA_DIR),
        "render_data_dir_exists": RENDER_DATA_DIR.exists(),
        "vector_store_dir": str(DATA_DIR / "vector_db"),
        "vector_store_dir_exists": (DATA_DIR / "vector_db").exists(),
        "db_file": str(DATA_DIR / "vector_db" / "documents.json"),
        "db_file_exists": (DATA_DIR / "vector_db" / "documents.json").exists(),
        "upload_dir": str(UPLOAD_DIR),
        "upload_dir_exists": UPLOAD_DIR.exists(),
        "documents_in_memory": len(vector_store.documents),
        "documents_list": len(vector_store.list_documents()),
        "telemetry_enabled": telemetry_provider is not None,
        "python_version": sys.version,
        "cwd": str(Path.cwd())
    }

@app.get("/test")
async def test_endpoint():
    """Simple test endpoint to verify backend is receiving requests"""
    import sys
    print(f"[TEST] Test endpoint called!", file=sys.stderr, flush=True)
    return {
        "status": "ok",
        "message": "Backend is receiving requests",
        "timestamp": datetime.now().isoformat()
    }


# ============================================================
# PROJECT MANAGEMENT ENDPOINTS
# ============================================================

@app.get("/api/projects")
async def list_projects():
    """List all projects"""
    try:
        projects = project_manager.list_projects()
        
        # Note: Document and question counts removed per user request
        
        return {
            "success": True,
            "count": len(projects),
            "projects": projects
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list projects: {str(e)}")


@app.post("/api/projects")
async def create_project(project: Project):
    """Create a new project"""
    try:
        new_project = project_manager.create_project(
            name=project.name,
            description=project.description or ""
        )
        return {
            "success": True,
            "project": new_project
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")


@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    """Get a specific project"""
    try:
        project = project_manager.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Note: Document and question counts removed per user request
        
        return {
            "success": True,
            "project": project
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve project: {str(e)}")


@app.put("/api/projects/{project_id}")
async def update_project(project_id: str, update: ProjectUpdate):
    """Update a project"""
    try:
        updated_project = project_manager.update_project(
            project_id=project_id,
            name=update.name,
            description=update.description
        )
        if not updated_project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return {
            "success": True,
            "project": updated_project
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update project: {str(e)}")


@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete a project and all its documents"""
    try:
        # Get all documents for this project
        documents = vector_store.list_documents(project_id=project_id)
        
        # Delete all documents
        for doc in documents:
            # Delete from vector store
            vector_store.delete_document(doc['id'])
            
            # Delete physical file if exists
            if 'file_path' in doc:
                file_path = Path(doc['file_path'])
                if file_path.exists():
                    file_path.unlink()
        
        # Delete Q&A history for this project
        vector_store.delete_project_qa(project_id)
        
        # Delete the project
        success = project_manager.delete_project(project_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return {
            "success": True,
            "message": f"Project and {len(documents)} documents deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete project: {str(e)}")


@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...), project_id: str = "default"):
    """
    Upload and process a document
    Supports: PDF, Excel (.xlsx, .xls, .csv), Word (.docx), Text (.txt)
    """
    import sys
    print(f"[UPLOAD] ========== UPLOAD STARTED ==========", file=sys.stderr, flush=True)
    print(f"[UPLOAD] Received upload request for project_id: {project_id}, filename: {file.filename}", file=sys.stderr, flush=True)
    print(f"[UPLOAD] File content type: {file.content_type}", file=sys.stderr, flush=True)
    print(f"[UPLOAD] Upload directory: {UPLOAD_DIR}", file=sys.stderr, flush=True)
    
    if not AI_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="AI service not configured. Please set OPENAI_API_KEY or OPENROUTER_API_KEY in .env file."
        )
    
    try:
        # Verify project exists
        project = project_manager.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")
        print(f"[UPLOAD] Project verified: {project['name']}", file=sys.stderr)
        
        # Generate unique ID
        doc_id = str(uuid.uuid4())
        print(f"[UPLOAD] Generated doc_id: {doc_id}", file=sys.stderr)
        
        # Save file temporarily
        file_path = UPLOAD_DIR / f"{doc_id}_{file.filename}"
        print(f"[UPLOAD] Saving file to: {file_path}", file=sys.stderr)
        
        # Read and save file
        content = await file.read()
        print(f"[UPLOAD] Read {len(content)} bytes from file", file=sys.stderr)
        with open(file_path, "wb") as f:
            f.write(content)
        print(f"[UPLOAD] File saved to disk: {file_path.exists()}", file=sys.stderr)
        
        # Process document
        print(f"[UPLOAD] Processing document...", file=sys.stderr)
        doc_data = doc_processor.process(str(file_path))
        print(f"[UPLOAD] Document processed: {len(doc_data.get('text', ''))} characters", file=sys.stderr)
        
        # Store in vector database
        print(f"[UPLOAD] Adding document to vector store: doc_id={doc_id}, project_id={project_id}", file=sys.stderr)
        vector_store.add_document(
            doc_id=doc_id,
            text=doc_data['text'],
            metadata={
                'filename': file.filename,
                'file_type': doc_data['type'],
                'pages': doc_data.get('pages'),
                'upload_date': datetime.now().isoformat(),
                'size': len(content),
                'file_path': str(file_path)
            },
            project_id=project_id
        )
        
        # Verify document was saved
        saved_docs = vector_store.list_documents(project_id=project_id)
        print(f"[UPLOAD] Document saved with doc_id: {doc_id}, project_id: {project_id}", file=sys.stderr)
        print(f"[UPLOAD] Total documents in project after save: {len(saved_docs)}", file=sys.stderr)
        print(f"[UPLOAD] Vector store has {len(vector_store.documents)} documents in memory", file=sys.stderr)
        print(f"[UPLOAD] ========== UPLOAD COMPLETED ==========", file=sys.stderr)
        
        # Note: Document and question counts removed per user request
        
        return {
            "success": True,
            "document_id": doc_id,
            "filename": file.filename,
            "file_type": doc_data['type'],
            "pages": doc_data.get('pages'),
            "size": len(content),
            "message": "Document uploaded and processed successfully"
        }
        
    except Exception as e:
        # Clean up on error
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/api/ask", response_model=Answer)
async def ask_question(q: Question):
    """
    Ask a question about uploaded documents using Multi-Agent System
    Returns answer with citations and confidence score
    """
    # Create span for the entire request
    tracer = trace.get_tracer(__name__)
    print(f"[ASK] Telemetry provider: {telemetry_provider}")
    print(f"[ASK] Tracer: {tracer}")
    with tracer.start_as_current_span(
        "api.ask_question",
        attributes={
            "question": q.question[:100],  # Truncate long questions
            "has_document_ids": bool(q.document_ids)
        }
    ) as span:
        print(f"[ASK] Created span: {span.get_span_context()}")
        def build_telemetry_payload() -> Dict[str, str]:
            """Return the trace/span identifiers for the current request span."""
            span_context = span.get_span_context()
            return {
                "trace_id": f"{span_context.trace_id:032x}",
                "span_id": f"{span_context.span_id:016x}",
            }

        if not AI_ENABLED:
            raise HTTPException(
                status_code=503,
                detail="AI service not configured. Please set OPENAI_API_KEY in .env file."
            )
        
        if not orchestrator:
            raise HTTPException(status_code=503, detail="Multi-agent system not initialized")
        
        try:
            start_time = time.time()
            
            # Get project_id, default to first project if not provided
            project_id = q.project_id
            if not project_id:
                projects = project_manager.list_projects()
                if projects:
                    project_id = projects[0]['id']
            
            # Search for relevant documents
            relevant_docs = vector_store.search(
                query=q.question,
                document_ids=q.document_ids,
                top_k=5,
                project_id=project_id
            )
            
            if not relevant_docs:
                # Don't increment question count if there are no documents
                span.set_status(Status(StatusCode.OK))
                return Answer(
                    question=q.question,
                    answer="I don't have any documents to answer this question. Please upload relevant documents first.",
                    sources=[],
                    confidence=0.0,
                    telemetry=build_telemetry_payload()
                )
            
            # Use Multi-Agent Orchestrator for comprehensive answer
            result = orchestrator.orchestrate(
                question=q.question,
                context=relevant_docs
            )
            
            # Add metrics to span
            processing_time = time.time() - start_time
            span.set_attribute("processing.time_ms", processing_time * 1000)
            span.set_attribute("response.confidence", result.get("confidence", 0))
            span.set_attribute("response.sources_count", len(result.get("sources", [])))
            
            # Save Q&A pair to database
            qa_id = None
            if project_id:
                qa_id = str(uuid.uuid4())
                # Calculate row number (count existing Q&A + 1)
                existing_qa = vector_store.list_qa(project_id)
                row_number = len(existing_qa) + 1
                vector_store.save_qa(
                    qa_id=qa_id,
                    question=result["question"],
                    answer=result["answer"],
                    sources=result.get("sources", []),
                    project_id=project_id,
                    confidence=result.get("confidence", 0),
                    row_number=row_number
                )
                
                # Note: Document and question counts removed per user request
                # No need to manually increment it
            
            # Set success status
            span.set_status(Status(StatusCode.OK))
            
            telemetry_payload = build_telemetry_payload()

            answer = Answer(
                question=result["question"],
                answer=result["answer"],
                sources=result["sources"],
                confidence=result["confidence"],
                agents_used=result.get("agents_used", []),
                telemetry=telemetry_payload
            )
            
            # Include qa_id in response for frontend tracking
            answer_dict = answer.dict()
            if qa_id:
                answer_dict["qa_id"] = qa_id
            answer_dict["telemetry"] = telemetry_payload
            
            return answer_dict
            
        except Exception as e:
            # Set error status
            span.set_status(Status(StatusCode.ERROR, description=str(e)))
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            raise HTTPException(status_code=500, detail=f"Question processing failed: {str(e)}")


@app.post("/api/batch-ask")
async def batch_ask_questions(batch: BatchQuestion):
    """
    Ask multiple questions in batch
    Returns list of answers
    """
    if not AI_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="AI service not configured"
        )
    
    results = []
    for question in batch.questions:
        try:
            q = Question(question=question, document_ids=batch.document_ids)
            answer = await ask_question(q)
            results.append(answer.dict())
        except Exception as e:
            results.append({
                "question": question,
                "answer": f"Error: {str(e)}",
                "sources": [],
                "confidence": 0.0
            })
    
    return {"results": results}


@app.get("/api/documents")
async def list_documents(project_id: Optional[str] = None):
    """
    List all uploaded documents with metadata, optionally filtered by project
    """
    try:
        documents = vector_store.list_documents(project_id=project_id)
        return {
            "success": True,
            "count": len(documents),
            "documents": documents
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@app.get("/api/documents/{doc_id}")
async def get_document(doc_id: str):
    """
    Get specific document details
    """
    try:
        doc = vector_store.get_document(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        return doc
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve document: {str(e)}")


@app.delete("/api/documents/{doc_id}")
async def delete_document(doc_id: str):
    """
    Delete a document and its associated data
    """
    try:
        # Get document metadata to find file path and project
        doc = vector_store.get_document(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        project_id = doc.get('project_id')
        
        # Delete from vector store
        deleted = vector_store.delete_document(doc_id)
        if not deleted:
            raise HTTPException(status_code=500, detail="Failed to delete document from vector store")
        
        # Delete physical file if exists
        if doc and 'file_path' in doc:
            file_path = Path(doc['file_path'])
            if file_path.exists():
                file_path.unlink()
        
        # Note: Document and question counts removed per user request
        # No need to manually decrement it
        
        return {
            "success": True,
            "message": "Document deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")


@app.get("/api/export")
async def export_results(questions: str, answers: str):
    """
    Export Q&A results to Excel
    Expects comma-separated questions and answers
    """
    try:
        q_list = questions.split("|||")
        a_list = answers.split("|||")
        
        df = pd.DataFrame({
            "Question": q_list,
            "Answer": a_list,
            "Timestamp": [datetime.now().isoformat()] * len(q_list)
        })
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Q&A Results')
        
        output.seek(0)
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=qa_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@app.get("/api/stats")
async def get_statistics():
    """
    Get system statistics
    """
    try:
        documents = vector_store.list_documents()
        
        file_types = {}
        total_pages = 0
        
        for doc in documents:
            file_type = doc.get('file_type', 'unknown')
            file_types[file_type] = file_types.get(file_type, 0) + 1
            total_pages += doc.get('pages', 0)
        
        return {
            "total_documents": len(documents),
            "total_pages": total_pages,
            "file_types": file_types,
            "ai_enabled": AI_ENABLED
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@app.get("/api/qa")
async def get_qa_history(project_id: Optional[str] = None):
    """Get Q&A history for a project"""
    try:
        if project_id:
            qa_list = vector_store.list_qa(project_id)
        else:
            # Return all Q&A from all projects
            qa_list = []
            for proj_id, qas in vector_store.qa_history.items():
                for qa in qas:
                    qa_list.append(qa)
        
        return {
            "success": True,
            "count": len(qa_list),
            "qa_list": qa_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve Q&A history: {str(e)}")


@app.delete("/api/qa/{qa_id}")
async def delete_qa(qa_id: str, project_id: Optional[str] = None):
    """Delete a specific Q&A entry"""
    try:
        if not project_id:
            raise HTTPException(status_code=400, detail="project_id is required")
        
        success = vector_store.delete_qa(qa_id, project_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Q&A entry not found")
        
        return {
            "success": True,
            "message": "Q&A entry deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete Q&A entry: {str(e)}")


@app.get("/api/view/{doc_id}")
async def view_document(doc_id: str, page: int = 1):
    """
    Serve a document file for viewing
    Supports page parameter for PDFs
    """
    try:
        doc = vector_store.get_document(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        file_path = Path(doc.get('file_path', ''))
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found on disk")
        
        # Return the file
        return FileResponse(
            path=str(file_path),
            filename=doc.get('filename', 'document'),
            media_type='application/pdf' if doc.get('file_type') == 'pdf' else 'application/octet-stream'
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve document: {str(e)}")


# Startup message
@app.on_event("startup")
async def startup_event():
    print("\n" + "=" * 60)
    print("  Autonomous Diligence Cloud - MULTI-AGENT SYSTEM")
    print("=" * 60)
    print(f"AI Enabled: {AI_ENABLED}")
    if AI_ENABLED:
        if OPENROUTER_API_KEY:
            print(f"AI Provider: OpenRouter")
        elif OPENAI_API_KEY:
            print(f"AI Provider: OpenAI")
        print(f"\nActive Agents:")
        print(f"   * DocumentAgent - Document retrieval & citation")
        print(f"   * AnalysisAgent - Deep analysis & insights")
        print(f"   * DataExtractionAgent - Numbers & metrics")
        print(f"   * FactCheckAgent - Verification & validation")
        print(f"   * OrchestratorAgent - Coordination & synthesis")
    else:
        print("⚠️  WARNING: No API key configured!")
        print("   Set OPENAI_API_KEY or OPENROUTER_API_KEY in .env file")
    print("=" * 60)
    print(f"Server running at: http://localhost:{os.getenv('PORT', 8002)}")
    print(f"API Docs: http://localhost:{os.getenv('PORT', 8002)}/docs")
    print("=" * 60 + "\n")


# Main entry point
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8002))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )

