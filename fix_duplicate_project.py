#!/usr/bin/env python3
"""
Fix duplicate Tech Venture AI projects
Keeps the one with documents, deletes the empty one
"""

import requests
import json

API_BASE = "http://localhost:8002"

def main():
    print("🔍 Checking for duplicate projects...")
    
    # Get all projects
    response = requests.get(f"{API_BASE}/api/projects")
    if response.status_code != 200:
        print("❌ Failed to get projects")
        return
    
    projects = response.json().get("projects", [])
    
    # Find all Tech Venture AI projects
    tech_projects = [p for p in projects if "Tech Venture" in p["name"] or "TechVenture" in p["name"]]
    
    print(f"Found {len(tech_projects)} Tech Venture AI projects:")
    for i, p in enumerate(tech_projects, 1):
        print(f"  {i}. {p['name']} (ID: {p['id'][:8]}..., Docs: {p.get('document_count', 0)})")
    
    if len(tech_projects) < 2:
        print("✅ No duplicates found!")
        return
    
    # Find the one with documents
    project_with_docs = None
    empty_projects = []
    
    for p in tech_projects:
        if p.get('document_count', 0) > 0:
            project_with_docs = p
        else:
            empty_projects.append(p)
    
    if not project_with_docs:
        print("⚠️  None of the projects have documents!")
        return
    
    if not empty_projects:
        print("✅ No empty duplicates to delete!")
        return
    
    print(f"\n📋 Plan:")
    print(f"  KEEP: {project_with_docs['name']} ({project_with_docs.get('document_count', 0)} documents)")
    for ep in empty_projects:
        print(f"  DELETE: {ep['name']} ({ep.get('document_count', 0)} documents)")
    
    # Ask for confirmation
    response = input("\n⚠️  Delete empty projects? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Cancelled")
        return
    
    # Delete empty projects
    for ep in empty_projects:
        print(f"🗑️  Deleting {ep['name']}...")
        delete_response = requests.delete(f"{API_BASE}/api/projects/{ep['id']}")
        if delete_response.status_code == 200:
            print(f"  ✅ Deleted successfully")
        else:
            print(f"  ❌ Failed to delete: {delete_response.text}")
    
    print(f"\n✅ Done! Kept project: {project_with_docs['name']}")
    print(f"   Now run: python3 run_evals.py --limit 5")

if __name__ == "__main__":
    main()


