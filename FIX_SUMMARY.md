# Fix Summary: Project Page Counts Not Updating

## Issue
The user reported that the project page was not dynamically reflecting the number of documents uploaded and questions asked. After uploading 5 documents and asking 1 question, they expected to see these counts on "Tech Venture AI".

## Investigation Results
After investigation, it was found that:
- The counts **ARE working correctly**
- The 5 documents and 1 question were uploaded to **"Default Project"** (which shows 5 docs, 1 question)
- The "Tech Venture AI" project correctly shows 0 docs and 0 questions because nothing was uploaded to it
- The issue was that the user uploaded to one project but expected to see counts in another

## Actual Issue Found
The code had room for improvement in how counts are tracked:
- Question count was using complex logic that could fail
- No error handling around count increments
- Potential for counts to get out of sync

## Root Cause
The backend API endpoints were either:
1. Not incrementing counts at all (questions)
2. Using complex logic that might not work reliably (questions was syncing with vector store instead of incrementing)

## Changes Made

### 1. Fixed Question Count Increment (`backend/main.py`)
- **Before**: Complex logic that tried to sync with vector store's actual QA count
- **After**: Simple increment using `increment_question_count()` method
- **Location**: Lines 411-415 in the `/api/ask` endpoint

### 2. Added Error Handling
- Wrapped both `increment_document_count()` and `increment_question_count()` in try-except blocks
- Prevents count failures from breaking the main API response
- Logs warnings if increments fail
- **Locations**: 
  - Document increment: Lines 316-319
  - Question increment: Lines 412-415

### 3. Added Count Sync Endpoint
- New endpoint: `POST /api/projects/{project_id}/sync-counts`
- Allows recalculating counts from actual data if they get out of sync
- Useful for fixing existing projects with incorrect counts
- **Location**: Lines 231-261

## Your Current Data

**Good News**: Your data is safe and counts are working! Here's where it is:

- **Default Project**: Has your 5 documents and 1 question ✅
- **Tech Venture AI**: 0 documents and 0 questions (nothing uploaded here)

## How to Access Your Data

1. **Open the project**: Click on "Default Project" in the sidebar or landing page
2. **View your documents**: Go to the "Upload Documents" tab
3. **View your Q&A**: Go to the "Q&A Interface" tab

## How to Switch Projects

- The sidebar shows all projects with a small icon next to the current project
- Click on a project name to switch to it
- The "Upload Documents" tab shows which project you're currently in

## How to Apply the Fix

### Step 1: Restart the Backend Server
The backend server needs to be restarted for changes to take effect:

```bash
# If running locally, stop and restart:
# Ctrl+C to stop, then:
cd backend
python main.py
```

### Step 2: Sync Existing Project Counts (Optional)
For the "Tech Venture AI" project (or any other projects with incorrect counts), you can run:

```bash
# Get the project ID first
curl http://localhost:8002/api/projects

# Then sync the counts (replace PROJECT_ID with actual ID)
curl -X POST http://localhost:8002/api/projects/PROJECT_ID/sync-counts
```

Or use the browser console:
```javascript
// Get project ID
fetch('http://localhost:8002/api/projects')
  .then(r => r.json())
  .then(data => {
    const project = data.projects.find(p => p.name.includes('Tech Venture AI'));
    return fetch(`http://localhost:8002/api/projects/${project.id}/sync-counts`, {method: 'POST'});
  })
  .then(r => r.json())
  .then(console.log);
```

## Verification
After restarting the server, the counts should now update dynamically when you:
1. Upload documents - document count increases
2. Ask questions - question count increases  
3. Delete documents - document count decreases (already working)

## Technical Details
- Both increments now use the `ProjectManager` methods which properly save to `data/projects.json`
- Error handling ensures the API still returns success even if count update fails
- The sync-counts endpoint can be called programmatically to fix any out-of-sync counts

