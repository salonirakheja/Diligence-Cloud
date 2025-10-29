# Dynamic Counts Implementation - Summary

## Problem
Project counts (document_count and question_count) were stored as static fields in `projects.json` and could get out of sync with the actual data in the vector store.

## Solution
**Counts are now calculated dynamically** from the actual data on every API request. The counts are no longer stored or manually incremented/decremented.

## Changes Made

### 1. `backend/main.py`
- **Removed** manual `increment_document_count()` call from upload endpoint (line ~349)
- **Removed** manual `increment_question_count()` call from ask endpoint (line ~447)
- **Removed** manual `decrement_document_count()` call from delete endpoint (line ~554)
- The API endpoints at lines 150-157 already calculate counts dynamically

### 2. `backend/project_manager.py`
- **Removed** `document_count` and `question_count` initialization when creating new projects
- Added comment explaining these are calculated dynamically

### 3. `data/projects.json`
- **Removed** all `document_count` and `question_count` fields from existing projects

## How It Works Now

When the frontend calls `GET /api/projects`, the backend:
1. Loads projects from `projects.json`
2. For each project, queries the vector store to count actual documents and Q&A
3. Returns the projects with dynamic counts attached

This ensures counts always match reality, no matter what happens.

## Next Steps

**You must restart the backend server** for these changes to take effect:

1. Stop the current backend process (Ctrl+C)
2. Start it again: `python main.py` (or however you normally start it)
3. Refresh your browser to see the correct counts

## Verification

After restarting, the counts should show:
- **Default Project**: 0 documents, 0 questions (no data stored under this project_id)
- **Tech Venture AI**: 5 documents, 1 question (all data is stored under this project_id)

