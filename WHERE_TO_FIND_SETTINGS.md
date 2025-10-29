# Where to Find Start Command in Render Dashboard

## You're Currently On: Overview Page
You're looking at the services list. You need to go to the Settings page.

## Steps:

### 1. Look at the Left Sidebar
On the left side of your screen, you should see a section called **"MANAGE"**

### 2. Click on "Settings"
Under "MANAGE", click on **"Settings"** (it has a gear icon ⚙️)

### 3. Scroll Down
On the Settings page, scroll down until you see these fields:

- **Environment**: Python 3
- **Build Command**: This is what you need to check
- **Start Command**: This is what you need to change

### 4. Update the Start Command
- Find the **"Start Command"** field
- It probably says: `diligence_cloud`
- Change it to: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
- Click **"Save Changes"**

### 5. Deploy
After saving, you can manually trigger a deployment or it will auto-deploy.

## Navigation Path:
Dashboard → **Settings** (left sidebar) → Scroll to "Start Command" field

