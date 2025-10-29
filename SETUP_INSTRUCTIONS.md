# 🔧 Setup Instructions

## First-Time Setup

Follow these steps to set up Autonomous Diligence Cloud for the first time.

## ✅ Prerequisites Checklist

Before you begin, make sure you have:

- [ ] Python 3.9 or higher installed
- [ ] Internet connection
- [ ] A text editor (Notepad, VS Code, etc.)
- [ ] OpenAI API key ready

### Check Python Installation

Open Command Prompt or PowerShell and run:
```bash
python --version
```

You should see something like: `Python 3.9.x` or higher

If not, download from: https://www.python.org/downloads/

## 📝 Step 1: Configure API Key

### Option A: Using OpenAI (Recommended)

1. **Get your API key:**
   - Visit: https://platform.openai.com/api-keys
   - Sign in or create an account
   - Click "Create new secret key"
   - Copy the key (starts with `sk-`)

2. **Create .env file:**
   - Rename `env_template.txt` to `.env`
   - Open `.env` in a text editor
   - Replace `your_openai_api_key_here` with your actual key:
     ```
     OPENAI_API_KEY=sk-your-actual-key-here
     ```
   - Save the file

### Option B: Using OpenRouter (Alternative)

1. **Get your API key:**
   - Visit: https://openrouter.ai/
   - Sign up and get your key

2. **Configure .env:**
   ```env
   # Comment out OpenAI
   # OPENAI_API_KEY=your_openai_api_key_here
   
   # Add OpenRouter
   OPENROUTER_API_KEY=your_openrouter_key_here
   OPENROUTER_MODEL=openai/gpt-4o-mini
   ```

## 🚀 Step 2: Install Dependencies

### Automatic Installation (Recommended)

Just run the startup script - it will install everything automatically:

**Windows Command Prompt:**
```bash
start_server.cmd
```

**Windows PowerShell:**
```bash
.\start_server.ps1
```

### Manual Installation (Optional)

If you prefer to install manually:

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows CMD:
venv\Scripts\activate.bat

# On Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r backend\requirements.txt
```

## 🎯 Step 3: Verify Installation

After running the startup script, you should see:

```
============================================
  Autonomous Diligence Cloud
  AI-Powered Document Intelligence
============================================

✓ Python found: Python 3.x.x
✓ Virtual environment created
✓ Dependencies installed

============================================
  Starting server...
  Access at: http://localhost:8002
  API Docs: http://localhost:8002/docs
============================================
```

## 🌐 Step 4: Access the Application

1. Open your web browser
2. Navigate to: **http://localhost:8002**
3. You should see the Autonomous Diligence Cloud interface

## ✨ Step 5: Test It Out

### Upload a Test Document

1. Click **"Upload Documents"** tab
2. Drag & drop any PDF, Excel, or Word document
3. Wait for the success message

### Ask a Test Question

1. Click **"Q&A Interface"** tab
2. Type: "What is this document about?"
3. Click **"Ask"**
4. You should get an AI-generated answer!

## 🔍 Verification Checklist

After setup, verify these things work:

- [ ] Server starts without errors
- [ ] Browser opens at http://localhost:8002
- [ ] You can see the two-page interface (Q&A and Upload)
- [ ] You can upload a document successfully
- [ ] You can ask a question and get an answer
- [ ] Answer includes sources and confidence score

## 🆘 Troubleshooting

### Error: "Python is not installed"
**Solution:** Install Python 3.9+ from https://python.org

### Error: "No module named 'fastapi'"
**Solution:** Run `pip install -r backend\requirements.txt`

### Error: "No API key configured"
**Solution:** 
1. Make sure `.env` file exists (not `env_template.txt`)
2. Open `.env` and verify your API key is correctly entered
3. No spaces around the `=` sign
4. No quotes around the key

### Error: "Port 8002 already in use"
**Solution:** 
1. Close any other programs using port 8002
2. Or change PORT in `.env` to 8003

### Error: "Failed to upload document"
**Solution:**
1. Check file format (PDF, Excel, Word, Text only)
2. File size should be reasonable (<100MB)
3. Check server logs for specific errors

### Browser shows "Cannot connect"
**Solution:**
1. Make sure the server is still running
2. Check you're using http:// not https://
3. Try http://127.0.0.1:8002 instead

## 🎓 Understanding the Files

### Core Files
- **backend/main.py** - Main server application
- **backend/agents.py** - AI logic for answering questions
- **backend/document_processor.py** - Reads different file types
- **backend/vector_store.py** - Stores document embeddings
- **frontend/index.html** - User interface

### Configuration Files
- **.env** - Your API keys and settings (NEVER share this!)
- **backend/requirements.txt** - Python dependencies
- **.gitignore** - Files to exclude from git

### Data Directories
- **backend/uploads/** - Temporarily stores uploaded files
- **data/vector_db/** - Stores document embeddings for search

## 🔒 Security Notes

1. **Never commit .env to git** - It contains your API key!
2. **Keep your API key private** - Anyone with it can use your OpenAI account
3. **Monitor API usage** - Check your OpenAI dashboard for costs
4. **Local storage** - All documents are stored locally, not in the cloud

## 📊 Cost Considerations

Using OpenAI API has costs:
- **GPT-4**: ~$0.01-0.03 per question (higher quality)
- **GPT-3.5**: ~$0.001-0.002 per question (faster, cheaper)
- **Embeddings**: ~$0.0001 per document

Tips to reduce costs:
- Use GPT-3.5 for simple questions
- Use OpenRouter for cheaper alternatives
- Process documents in batches
- Monitor usage in OpenAI dashboard

## 🎉 Next Steps

Now that you're set up:

1. **Read the full README.md** for all features
2. **Check out QUICK_START.md** for usage examples
3. **Review my_agent_prd.md** for product vision
4. **Explore API docs** at http://localhost:8002/docs

## 📞 Getting Help

If you're still having issues:

1. Check the full **README.md** troubleshooting section
2. Review error messages carefully
3. Check Python and pip versions
4. Ensure all files are in the correct directories
5. Try restarting the server

---

**Ready to start? Run `start_server.cmd` or `start_server.ps1` and open http://localhost:8002!**

