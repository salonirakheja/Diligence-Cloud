# Render.com Deployment Guide

## ✅ Deployment Files Created

- `render.yaml` - Render service configuration
- `.renderignore` - Files to exclude from deployment

## 🚀 Deploy to Render.com

### Step 1: Connect Your Repository
1. Go to [render.com](https://render.com)
2. Sign up / Log in
3. Click **"New +"** → **"Web Service"**
4. Connect your GitHub repository: `salonirakheja/Diligence-Cloud`

### Step 2: Configure Service Settings
**⚠️ CRITICAL: Manually set these in the Render dashboard!**

Even though `render.yaml` exists, you need to manually configure these settings:

- **Service Name**: diligence-cloud
- **Region**: Choose closest to you
- **Branch**: main
- **Root Directory**: (leave blank)
- **Runtime**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

**OR** delete the existing service and let Render auto-detect from `render.yaml` on a fresh deployment.

### Step 3: Add Environment Variables
In the Render dashboard → Environment section, add:
- **OPENAI_API_KEY**: `your-openai-api-key-here`
- **PHOENIX_API_URL**: `https://app.phoenix.arize.com/s/<workspace>/v1`
- **PHOENIX_API_KEY**: *your Phoenix user key (Settings → API Keys → User Keys)*
- **PHOENIX_PROJECT**: `Diligence-Cloud` *(or any project label you want in Phoenix)*
- Optional:
  - **OPENAI_MODEL**: `gpt-4o-mini` (default)
  - **OPENROUTER_API_KEY**: If using OpenRouter instead
  - **PHOENIX_SERVICE_NAME**: Override the service name reported in spans
  - **PHOENIX_TRACES_ENDPOINT**: Explicitly set OTLP endpoint (defaults to `${PHOENIX_API_URL}/traces`)

### Step 4: Add Persistent Disk (Important!)
1. In the Render dashboard, go to **"Disks"**
2. Click **"Attach Disk"**
3. Configure:
   - **Name**: diligence-cloud-disk
   - **Mount Path**: `/opt/render/project/src/data`
   - **Size**: 10 GB
4. Attach it to your web service

**⚠️ Important**: Without a persistent disk, your vector database and uploaded documents will be lost on every deployment!

### Step 5: Deploy
Click **"Create Web Service"** and wait for the first deployment to complete.

## 🌐 Access Your App

Once deployed, you'll get a URL like:
- `https://diligence-cloud.onrender.com`

The app will be live at this URL with:
- Frontend: Served via FastAPI at `/`
- API Docs: Available at `/docs`
- Health Check: Available at `/health`

## 📝 Important Notes

### Cold Starts
Render free tier services sleep after 15 minutes of inactivity. The first request after sleeping may take 30-60 seconds to wake up.

### Deployment Tips
1. **First Deployment**: May take 5-10 minutes to build and start
2. **Subsequent Deployments**: Triggered automatically on push to main branch
3. **Logs**: View in Render dashboard → "Logs" tab
4. **Build Status**: Check "Events" tab for deployment progress

### Storage
- **Persistent Data**: Stored on the mounted disk at `/opt/render/project/src/data`
- **Includes**: `projects.json`, `vector_db/`, `uploads/`
- **Resize**: Can increase disk size in Render dashboard (minimum 10GB, increments of 1GB)

### Environment Variables
Manage via Render dashboard → Settings → Environment Variables. Changes require a redeploy.

## 🐛 Troubleshooting

### Build Command Not Working / Requirements.txt Not Found
**Problem**: Error `Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'`

**Solution**: Update the Build Command in Render dashboard:
1. Go to your service in Render dashboard
2. Click **"Settings"** tab
3. Scroll to **"Build Command"**
4. Change it to: `pip install -r backend/requirements.txt`
5. Click **"Save Changes"**
6. Go to **"Manual Deploy"** tab → **"Deploy latest commit"**

### Build Fails
- Check "Logs" tab for error messages
- Verify Python version (3.11.0)
- Ensure `requirements.txt` is correct

### Service Won't Start
- Check startup logs
- Verify `OPENAI_API_KEY` is set
- Check mount path for disk

### Data Loss
- Ensure persistent disk is attached
- Verify mount path matches configuration
- Check disk has available space

### Slow Response
- Free tier has resource limits
- Consider upgrading to paid plan for better performance
- Optimize request timeouts if needed

## 🔗 Resources

- [Render Documentation](https://render.com/docs)
- [FastAPI Deployment Guide](https://render.com/docs/deploy-fastapi)
- [Persistent Disks](https://render.com/docs/disks)

