"""
Project Manager Module
Handles project creation, management, and isolation of documents/Q&A per project
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import uuid


class ProjectManager:
    """Manage multiple projects with isolated document stores"""
    
    def __init__(self, projects_file: str = "./data/projects.json"):
        """
        Initialize the project manager
        
        Args:
            projects_file: Path to the projects JSON file
        """
        self.projects_file = Path(projects_file)
        self.projects_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load or initialize projects
        self.projects = self._load_projects()
        
        # Ensure default project exists
        if not self.projects:
            self.create_project("Default Project", "Your first project")
    
    def _load_projects(self) -> List[Dict]:
        """Load projects from JSON file"""
        if self.projects_file.exists():
            try:
                with open(self.projects_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading projects: {e}")
                return []
        return []
    
    def _save_projects(self) -> None:
        """Save projects to JSON file"""
        try:
            with open(self.projects_file, 'w') as f:
                json.dump(self.projects, f, indent=2)
        except Exception as e:
            print(f"Error saving projects: {e}")
    
    def create_project(self, name: str, description: str = "") -> Dict:
        """
        Create a new project
        
        Args:
            name: Project name
            description: Project description
            
        Returns:
            Created project dict
        """
        project_id = str(uuid.uuid4())
        # Note: document_count and question_count are calculated dynamically by the API, not stored here
        project = {
            "id": project_id,
            "name": name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.projects.append(project)
        self._save_projects()
        
        print(f"Created project: {name} (ID: {project_id})")
        return project
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """Get project by ID"""
        for project in self.projects:
            if project["id"] == project_id:
                return project
        return None
    
    def list_projects(self) -> List[Dict]:
        """List all projects"""
        return self.projects
    
    def update_project(self, project_id: str, name: Optional[str] = None, 
                      description: Optional[str] = None) -> Optional[Dict]:
        """
        Update project details
        
        Args:
            project_id: Project ID
            name: New name (optional)
            description: New description (optional)
            
        Returns:
            Updated project or None if not found
        """
        project = self.get_project(project_id)
        if not project:
            return None
        
        if name:
            project["name"] = name
        if description is not None:
            project["description"] = description
        
        project["updated_at"] = datetime.now().isoformat()
        self._save_projects()
        
        return project
    
    def delete_project(self, project_id: str) -> bool:
        """
        Delete a project
        
        Args:
            project_id: Project ID
            
        Returns:
            True if deleted, False if not found
        """
        initial_count = len(self.projects)
        self.projects = [p for p in self.projects if p["id"] != project_id]
        
        if len(self.projects) < initial_count:
            self._save_projects()
            print(f"Deleted project: {project_id}")
            return True
        
        return False
    
    def get_project_vector_store_path(self, project_id: str) -> str:
        """Get the vector store path for a project"""
        return f"./data/vector_db/project_{project_id}"
    
    def get_project_uploads_path(self, project_id: str) -> Path:
        """Get the uploads directory path for a project"""
        uploads_dir = Path(f"./backend/uploads/project_{project_id}")
        uploads_dir.mkdir(parents=True, exist_ok=True)
        return uploads_dir

