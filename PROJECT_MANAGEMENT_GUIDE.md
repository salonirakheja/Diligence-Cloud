# Project Management Feature Guide

## Overview

The Diligence Cloud now supports **multiple projects** with isolated Q&A sessions and document repositories. This allows you to manage different due diligence projects (e.g., Acme Corp, Nordic Telecoms, etc.) with completely separate document sets and conversation histories.

## Key Features

### ✅ What's New

1. **Project Selector** - Switch between projects in the header
2. **Project Isolation** - Each project has its own documents and Q&A history
3. **Project Creation** - Create new projects with name and description
4. **Project Statistics** - Track document and question counts per project
5. **Automatic Default Project** - A "Default Project" is created on first startup

## User Interface

### Header Changes

The header now includes a **Project Selector**:

```
┌──────────────────────────────────────────────────────────┐
│  🅳 Diligence Cloud                                      │
│     AI-Powered Document Intelligence Platform           │
│                                                          │
│  [Project: Default Project ▼] [+ New]  📊 Docs  📊 Q&A │
└──────────────────────────────────────────────────────────┘
```

### Creating a New Project

1. Click the **"+ New"** button in the header
2. Enter a project name (e.g., "Acme Corp Due Diligence")
3. Optionally add a description
4. Click **"Create Project"**
5. The new project will be automatically selected

### Switching Projects

1. Click the project dropdown in the header
2. Select the project you want to work with
3. The interface will reload with that project's documents and Q&A

## Backend Architecture

### New Components

#### 1. `backend/project_manager.py`
Manages project lifecycle and metadata:
- `create_project(name, description)` - Create new project
- `get_project(project_id)` - Get project details
- `list_projects()` - List all projects
- `update_project(project_id, ...)` - Update project info
- `delete_project(project_id)` - Delete project and all its data

#### 2. Updated `backend/simple_vector_store.py`
Vector store now supports project isolation:
- `add_document(..., project_id)` - Associate documents with projects
- `search(..., project_id)` - Filter search by project
- `list_documents(project_id)` - List documents for specific project

#### 3. Updated `backend/main.py`
New API endpoints for project management:
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create new project
- `GET /api/projects/{id}` - Get project details
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project and all documents

### Data Storage

Projects are stored in:
```
data/
├── projects.json           # Project metadata
└── vector_db/
    └── documents.json      # Documents with project_id field
```

Each document now includes a `project_id` field in its metadata for filtering.

## API Examples

### Create a New Project

```bash
curl -X POST http://localhost:8002/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Corp Acquisition",
    "description": "Due diligence for Acme Corp acquisition"
  }'
```

**Response:**
```json
{
  "success": true,
  "project": {
    "id": "abc123...",
    "name": "Acme Corp Acquisition",
    "description": "Due diligence for Acme Corp acquisition",
    "created_at": "2025-10-26T20:00:00",
    "updated_at": "2025-10-26T20:00:00",
    "document_count": 0,
    "question_count": 0
  }
}
```

### List All Projects

```bash
curl http://localhost:8002/api/projects
```

**Response:**
```json
{
  "success": true,
  "count": 2,
  "projects": [
    {
      "id": "abc123...",
      "name": "Acme Corp Acquisition",
      "description": "Due diligence for Acme Corp acquisition",
      "document_count": 5,
      "question_count": 12
    },
    {
      "id": "def456...",
      "name": "Nordic Telecoms",
      "description": "Telecom company evaluation",
      "document_count": 3,
      "question_count": 8
    }
  ]
}
```

### Upload Document to Project

```bash
curl -X POST "http://localhost:8002/api/upload?project_id=abc123..." \
  -F "file=@document.pdf"
```

### Ask Question in Project Context

```bash
curl -X POST http://localhost:8002/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the key risks?",
    "project_id": "abc123..."
  }'
```

### Get Project Statistics

```bash
curl http://localhost:8002/api/projects/abc123...
```

**Response:**
```json
{
  "success": true,
  "project": {
    "id": "abc123...",
    "name": "Acme Corp Acquisition",
    "description": "Due diligence for Acme Corp acquisition",
    "document_count": 5,
    "question_count": 12,
    "created_at": "2025-10-26T20:00:00",
    "updated_at": "2025-10-26T20:15:00"
  }
}
```

### Delete Project

```bash
curl -X DELETE http://localhost:8002/api/projects/abc123...
```

**Response:**
```json
{
  "success": true,
  "message": "Project and 5 documents deleted successfully"
}
```

## Frontend Integration

### JavaScript Variables

```javascript
let currentProjectId = null;  // Currently selected project
let projects = [];            // List of all projects
```

### Key Functions

- `loadProjects()` - Load and populate project dropdown
- `switchProject()` - Switch to different project
- `showNewProjectModal()` - Show project creation modal
- `createProject()` - Create new project
- `updateProjectStats()` - Update document/question counts

### Automatic Behaviors

1. **On Page Load**: Loads all projects and selects the first one
2. **On Project Switch**: Clears Q&A table and reloads documents
3. **On Document Upload**: Updates project document count
4. **On Question Answered**: Updates project question count

## Use Cases

### Scenario 1: Multiple Acquisitions

Managing due diligence for multiple potential acquisitions:

1. **Project: "Acme Corp"**
   - Documents: Financial statements, legal contracts
   - Q&A: Questions about revenue, risks, liabilities

2. **Project: "Beta Industries"**
   - Documents: IP portfolio, customer contracts
   - Q&A: Questions about intellectual property, customer base

3. **Project: "Gamma LLC"**
   - Documents: Market research, competitor analysis
   - Q&A: Questions about market position, growth potential

### Scenario 2: Investment Portfolio

Managing analysis for different investment opportunities:

1. **Project: "Tech Startup A"** - Series A evaluation
2. **Project: "Real Estate Fund B"** - Property portfolio review
3. **Project: "Public Company C"** - Quarterly earnings analysis

### Scenario 3: Legal Cases

Organizing documents for different legal matters:

1. **Project: "Case #2025-001"** - Contract dispute
2. **Project: "Case #2025-002"** - Employment litigation
3. **Project: "Case #2025-003"** - IP infringement

## Best Practices

### Naming Conventions

Use clear, descriptive project names:
- ✅ "Acme Corp Acquisition 2025"
- ✅ "Nordic Telecoms Due Diligence"
- ✅ "Q4 2024 Investment Review"
- ❌ "Project 1"
- ❌ "Stuff"
- ❌ "Test"

### Project Descriptions

Include key information:
- Purpose of the project
- Key dates or deadlines
- Stakeholders involved
- Project status

Example:
```
"Due diligence for Acme Corp acquisition. 
Target closing: Q1 2025. 
Lead: Sarah Johnson. 
Status: Document review phase."
```

### Document Organization

- Upload all related documents to the same project
- Use consistent file naming conventions
- Keep projects focused and specific
- Archive or delete old projects when complete

### Q&A Management

- Each project maintains its own Q&A history
- Questions are only answered using documents from the current project
- Switch projects to access different conversation contexts

## Technical Details

### Database Schema

**Project Object:**
```json
{
  "id": "uuid-string",
  "name": "Project Name",
  "description": "Optional description",
  "created_at": "ISO-8601 timestamp",
  "updated_at": "ISO-8601 timestamp",
  "document_count": 0,
  "question_count": 0
}
```

**Document Metadata (with project_id):**
```json
{
  "id": "document-uuid",
  "filename": "report.pdf",
  "file_type": "pdf",
  "pages": 50,
  "upload_date": "ISO-8601 timestamp",
  "size": 1024000,
  "project_id": "project-uuid"
}
```

### Performance Considerations

- Projects are loaded once on page load
- Document lists are filtered by project_id on the server
- Vector search is scoped to current project for faster results
- Project switching clears the UI but doesn't reload the page

### Security & Data Isolation

- Each project's documents are strictly isolated
- Q&A searches only return results from the current project
- Deleting a project removes all associated documents and files
- No cross-project data leakage

## Migration Notes

### Existing Data

If you had documents before adding project management:
1. A "Default Project" is automatically created on first startup
2. Existing documents will need to be re-uploaded or manually assigned
3. The project_id field is added to all new documents

### Backward Compatibility

- Old API calls without `project_id` will use the first available project
- Document uploads without `project_id` require manual specification
- Existing vector store files are preserved

## Troubleshooting

### Issue: "Please select or create a project first"

**Solution:** Create a new project using the "+ New" button before uploading documents.

### Issue: Documents not showing up

**Solution:** Ensure you're viewing the correct project in the dropdown.

### Issue: Questions returning "no documents" error

**Solution:** Verify the current project has documents uploaded.

### Issue: Project dropdown is empty

**Solution:** The server will auto-create a "Default Project" on startup. Refresh the page.

## Future Enhancements

Potential improvements for project management:

1. **Project Archiving** - Mark projects as complete/archived
2. **Project Sharing** - Share projects with team members
3. **Project Templates** - Create project templates with default settings
4. **Project Export** - Export entire project (documents + Q&A) as PDF
5. **Project Search** - Search across all projects
6. **Project Tags** - Add tags/categories to projects
7. **Project Dashboard** - Overview of all projects with statistics
8. **Access Control** - Per-project permissions and user roles

## Summary

The project management feature provides essential organization for managing multiple due diligence workflows. Each project maintains complete isolation of documents and Q&A history, enabling efficient context switching and better organization of your work.

**Key Benefits:**
- 📁 Organized document management
- 🔒 Complete data isolation per project
- 📊 Per-project statistics and tracking
- 🚀 Fast project switching
- 💡 Clear project context for AI responses

## Testing the Feature

1. **Open the application**: http://localhost:8002
2. **Check the header**: You should see the project dropdown with "Default Project"
3. **Create a test project**: Click "+ New" and create "Test Project"
4. **Upload a document**: Switch to the Upload tab and upload a test file
5. **Ask a question**: Return to Q&A tab and ask about the document
6. **Switch projects**: Use the dropdown to switch between projects
7. **Verify isolation**: Notice how each project has its own documents and Q&A

Enjoy your new multi-project capabilities! 🎉

