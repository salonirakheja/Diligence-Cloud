#!/usr/bin/env python3
"""
Import generated test data into Diligence Cloud
Uploads projects, documents, and Q&A data via API
"""

import argparse
import json
import mimetypes
import time
from pathlib import Path

import requests

DEFAULT_API_BASE = "http://localhost:8002"
API_BASE = DEFAULT_API_BASE

def _ensure_trailing_slash(url: str) -> str:
    return url[:-1] if url.endswith("/") else url

def get_existing_projects(api_base: str):
    """Return list of existing projects from the server"""
    response = requests.get(f"{api_base}/api/projects", timeout=30)
    if response.status_code != 200:
        raise RuntimeError(f"Failed to list projects: {response.status_code} {response.text}")
    return response.json().get("projects", [])

def create_or_get_project(api_base: str, name: str, description: str = ""):
    """Create project if it doesn't already exist"""
    projects = get_existing_projects(api_base)
    for proj in projects:
        if proj.get("name") == name:
            print(f"   ↪ Project already exists: {proj['id']} ({name})")
            return proj

    response = requests.post(
        f"{api_base}/api/projects",
        json={"name": name, "description": description},
        timeout=30,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Failed to create project '{name}': {response.status_code} {response.text}")
    project = response.json()["project"]
    print(f"   ✓ Project created: {project['id']}")
    return project

def upload_document(api_base: str, project_id: str, doc_path: Path):
    """Upload a document file to the specified project"""
    mime_type, _ = mimetypes.guess_type(doc_path.name)
    if mime_type is None:
        # default to plain text
        mime_type = "text/plain"

    with open(doc_path, "rb") as f:
        files = {
            "file": (doc_path.name, f, mime_type),
        }
        response = requests.post(
            f"{api_base}/api/upload",
            files=files,
            params={"project_id": project_id},
            timeout=120,
        )

    if response.status_code != 200:
        raise RuntimeError(
            f"      ❌ Upload failed for {doc_path.name}: {response.status_code} {response.text}"
        )

    payload = response.json()
    print(f"      📄 Uploaded {doc_path.name} ({payload.get('size', 0)} bytes)")

def import_project_data(project_file):
    """Import a single project from JSON file"""
    with open(project_file, 'r') as f:
        data = json.load(f)
    
    project_info = data["project"]
    print(f"\n📁 Importing: {project_info['name']}")
    
    # Create project
    project = create_or_get_project(
        API_BASE,
        name=project_info["name"],
        description=f"{project_info['industry']} | Revenue: {project_info['revenue']} | Employees: {project_info['employees']}"
    )
    
    if not project:
        return
    
    project_id = project["id"]
    
    # Import documents
    print(f"   📚 Documents: {len(data['documents'])}")
    doc_dir = project_file.parent / project_info["id"] / "documents"
    if doc_dir.exists():
        for doc_file in doc_dir.glob("*.txt"):
            upload_document(API_BASE, project_id, doc_file)
    else:
        print("      ⚠️ Document directory not found:", doc_dir)
    
    # Import Q&A pairs
    print(f"   💬 Q&A pairs: {len(data['qa_pairs'])}")
    
    time.sleep(0.5)  # Rate limiting
    
    return project

def main():
    """Import all generated data"""
    parser = argparse.ArgumentParser(description="Import generated diligence data via API")
    parser.add_argument(
        "--base-url",
        help=f"API base URL (default: {DEFAULT_API_BASE})",
        default=DEFAULT_API_BASE,
    )
    args = parser.parse_args()

    global API_BASE
    API_BASE = _ensure_trailing_slash(args.base_url.rstrip("/"))
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


