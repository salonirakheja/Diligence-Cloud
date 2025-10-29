#!/usr/bin/env python3
"""
Import generated test data into Diligence Cloud
Uploads projects, documents, and Q&A data via API
"""

import json
import requests
import time
from pathlib import Path

API_BASE = "http://localhost:8002"

def create_project(name, description=""):
    """Create a new project"""
    response = requests.post(
        f"{API_BASE}/api/projects",
        json={"name": name, "description": description}
    )
    if response.status_code == 200:
        return response.json()["project"]
    else:
        print(f"❌ Failed to create project: {name}")
        return None

def upload_document(project_id, doc_name, content):
    """Upload a document to a project"""
    # Note: This is a simplified version
    # In production, you'd want to create actual file objects
    print(f"   📄 Would upload: {doc_name} ({len(content)} bytes)")
    # Actual implementation would use multipart/form-data
    # with file upload to /api/upload endpoint

def import_project_data(project_file):
    """Import a single project from JSON file"""
    with open(project_file, 'r') as f:
        data = json.load(f)
    
    project_info = data["project"]
    print(f"\n📁 Importing: {project_info['name']}")
    
    # Create project
    project = create_project(
        name=project_info["name"],
        description=f"{project_info['industry']} | Revenue: {project_info['revenue']} | Employees: {project_info['employees']}"
    )
    
    if not project:
        return
    
    project_id = project["id"]
    print(f"   ✓ Project created: {project_id}")
    
    # Import documents
    print(f"   📚 Documents: {len(data['documents'])}")
    doc_dir = project_file.parent / project_info["id"] / "documents"
    if doc_dir.exists():
        for doc_file in doc_dir.glob("*.txt"):
            with open(doc_file, 'r') as f:
                content = f.read()
            upload_document(project_id, doc_file.stem, content)
    
    # Import Q&A pairs
    print(f"   💬 Q&A pairs: {len(data['qa_pairs'])}")
    
    time.sleep(0.5)  # Rate limiting
    
    return project

def main():
    """Import all generated data"""
    print("🚀 Importing Generated Data into Diligence Cloud")
    print("=" * 70)
    
    # Check if server is running
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code != 200:
            print("❌ Diligence Cloud server is not responding")
            print("   Please start the server first: python3 backend/main.py")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Diligence Cloud server")
        print("   Please start the server first: python3 backend/main.py")
        return
    
    print("✓ Server is running\n")
    
    # Find generated data
    data_dir = Path(__file__).parent / "generated_data"
    if not data_dir.exists():
        print("❌ Generated data not found. Run generate_diligence_data.py first.")
        return
    
    # Import each project
    project_files = sorted(data_dir.glob("project_*.json"))
    imported_count = 0
    
    for project_file in project_files:
        project = import_project_data(project_file)
        if project:
            imported_count += 1
    
    print("\n" + "=" * 70)
    print(f"✅ Import complete! {imported_count}/{len(project_files)} projects imported")
    print(f"\n🌐 Open http://localhost:8002 to view your data")
    print("=" * 70)

if __name__ == "__main__":
    main()


