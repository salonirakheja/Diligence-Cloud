#!/usr/bin/env python3
"""
Helper script to sync document and question counts for all projects.
Useful if counts have gotten out of sync.
"""

import json
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).parent
PROJECTS_FILE = PROJECT_ROOT / "data" / "projects.json"
VECTOR_DB_DIR = PROJECT_ROOT / "data" / "vector_db"
QA_HISTORY_FILE = VECTOR_DB_DIR / "qa_history.json"


def load_qa_history():
    """Load Q&A history from vector store"""
    if QA_HISTORY_FILE.exists():
        with open(QA_HISTORY_FILE, 'r') as f:
            return json.load(f)
    return {}


def get_document_count(project_id):
    """Get document count from vector store"""
    documents_file = VECTOR_DB_DIR / "documents.json"
    if not documents_file.exists():
        return 0
    
    with open(documents_file, 'r') as f:
        documents = json.load(f)
    
    # Count documents for this project
    # documents.json is a dict with doc_id as keys
    count = 0
    for doc_id, doc_data in documents.items():
        if isinstance(doc_data, dict) and doc_data.get('metadata', {}).get('project_id') == project_id:
            count += 1
    return count


def get_qa_count(project_id, qa_history):
    """Get Q&A count for a project"""
    if project_id in qa_history:
        return len(qa_history[project_id])
    return 0


def sync_all_projects():
    """Sync counts for all projects"""
    # Load projects
    if not PROJECTS_FILE.exists():
        print("Projects file not found!")
        return
    
    with open(PROJECTS_FILE, 'r') as f:
        projects = json.load(f)
    
    # Load Q&A history
    qa_history = load_qa_history()
    
    # Update each project
    updated = False
    for project in projects:
        project_id = project['id']
        project_name = project['name']
        
        # Get actual counts
        actual_doc_count = get_document_count(project_id)
        actual_qa_count = get_qa_count(project_id, qa_history)
        
        # Check if counts need updating
        stored_doc_count = project.get('document_count', 0)
        stored_qa_count = project.get('question_count', 0)
        
        if actual_doc_count != stored_doc_count or actual_qa_count != stored_qa_count:
            print(f"Updating {project_name}:")
            print(f"  Documents: {stored_doc_count} → {actual_doc_count}")
            print(f"  Questions: {stored_qa_count} → {actual_qa_count}")
            
            project['document_count'] = actual_doc_count
            project['question_count'] = actual_qa_count
            from datetime import datetime
            project['updated_at'] = datetime.now().isoformat()
            updated = True
    
    # Save if updated
    if updated:
        with open(PROJECTS_FILE, 'w') as f:
            json.dump(projects, f, indent=2)
        print("\n✓ Projects file updated!")
    else:
        print("\n✓ All project counts are already in sync.")


if __name__ == "__main__":
    print("Syncing project counts...\n")
    sync_all_projects()

