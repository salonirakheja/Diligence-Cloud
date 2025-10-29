# How to Add API Key to Render

## Step-by-Step Instructions:

### 1. Navigate to Your Service
- Go to **"Overview"** in the left sidebar
- Click on **"Diligence-Cloud"** service (the one with the failed deployment)

### 2. Go to Settings
- Once on the service page, click **"Settings"** in the left sidebar

### 3. Find Environment Variables Section
- Scroll down on the Settings page
- Look for a section called **"Environment"** or **"Environment Variables"**
- You'll see a list of existing environment variables

### 4. Add Your API Key
- Click the **"+ Add Environment Variable"** or **"Add Environment Variable"** button
- A form will appear with two fields:
  - **Key**: Type `OPENAI_API_KEY`
  - **Value**: Paste your OpenAI API key (starts with `sk-...`)
- Click **"Save Changes"** or **"Add"**

### 5. Deploy (if needed)
- After adding the environment variable, Render will automatically redeploy
- Or go to **"Manual Deploy"** tab → **"Deploy latest commit"**

## Important Notes:
- Your API key should start with `sk-`
- Don't share this key publicly
- The environment variable name must be exactly: `OPENAI_API_KEY`
- You can find your API key at: https://platform.openai.com/api-keys

## Navigation Path:
Dashboard → Overview → Click "Diligence-Cloud" → Settings → Environment Variables → Add Environment Variable

