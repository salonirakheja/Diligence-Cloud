# Fix Render Deployment - Dashboard Settings

## The Problem
Render is trying to run `diligence_cloud` command which doesn't exist. This is configured in the Render dashboard.

## The Solution

### Step 1: Open Your Service
1. Go to https://dashboard.render.com
2. Click on your service: **Diligence-Cloud**

### Step 2: Go to Settings
- Click on the **"Settings"** tab at the top

### Step 3: Find the Start Command
Scroll down to find the **"Start Command"** field.

### Step 4: Update the Start Command
Replace whatever is there (likely `diligence_cloud`) with:

```
cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Step 5: Update Build Command (if visible)
If you see **"Build Command"**, set it to:

```
pip install -r requirements.txt && pip install -r backend/requirements.txt
```

### Step 6: Save and Deploy
1. Click **"Save Changes"** button
2. Go to **"Manual Deploy"** tab
3. Click **"Deploy latest commit"**
4. Wait for deployment to complete

## Expected Result
You should see logs like:
```
==> Running 'cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT'
==> Started...
```

Instead of:
```
==> Running 'diligence_cloud'
bash: line 1: diligence_cloud: command not found
```

## Alternative: Recreate the Service
If you can't find the settings, delete the current service and create a new one. Render will auto-detect from `render.yaml` and `Procfile`.

