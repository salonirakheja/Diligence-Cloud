# ⚡ Quick Start Guide

Get up and running with Autonomous Diligence Cloud in 5 minutes!

## 🎯 What You'll Need

- ✅ Python 3.9 or higher installed
- ✅ An OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- ✅ 5 minutes of your time

## 📋 Step-by-Step Instructions

### Step 1: Get Your API Key (2 minutes)

1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click **"Create new secret key"**
4. Copy the key (it starts with `sk-...`)
5. Keep it safe - you'll need it in the next step!

💡 **Alternative**: You can also use [OpenRouter](https://openrouter.ai/) if you prefer.

### Step 2: Configure the Application (1 minute)

1. In the project folder, find `env_template.txt`
2. Rename it to `.env` (just remove the "_template.txt" part)
3. Open `.env` in any text editor
4. Replace `your_openai_api_key_here` with your actual API key
5. Save and close the file

Your `.env` should look like:
```env
OPENAI_API_KEY=sk-abc123xyz789...
```

### Step 3: Start the Server (1 minute)

**Windows (Command Prompt):**
```bash
start_server.cmd
```

**Windows (PowerShell):**
```bash
.\start_server.ps1
```

The script will:
- ✅ Create a virtual environment
- ✅ Install all dependencies
- ✅ Create necessary folders
- ✅ Start the server

Wait for the message: **"Server running at: http://localhost:8002"**

### Step 4: Open the Application (30 seconds)

1. Open your web browser
2. Go to: **http://localhost:8002**
3. You should see the Autonomous Diligence Cloud interface!

### Step 5: Try It Out! (30 seconds)

**Upload a Document:**
1. Click the **"Upload Documents"** tab
2. Drag & drop a PDF, Excel, or Word file
3. Wait for "uploaded successfully" message

**Ask a Question:**
1. Click the **"Q&A Interface"** tab
2. Type a question like: "What is this document about?"
3. Click **"Ask"**
4. Get your AI-powered answer! 🎉

## 🎉 You're Done!

You now have a fully functional AI document intelligence system!

## 🆘 Common Issues

### "Python is not installed"
👉 Download Python from [python.org](https://python.org) and install it

### "No API key configured"
👉 Make sure you renamed `env_template.txt` to `.env` and added your API key

### "Port 8002 already in use"
👉 Change the PORT in `.env` to 8003 or another number

### Server won't start
👉 Make sure you're running the script from the project folder

## 💡 Pro Tips

1. **Ask Multiple Questions**: Click "Add Question" to ask several questions at once
2. **Export Results**: Use "Export to Excel" to save your Q&A for reports
3. **Upload Multiple Files**: The AI can answer questions across all your documents
4. **Check Confidence**: Green = high confidence, Yellow = medium, Red = low

## 📚 Next Steps

- Read the full [README.md](README.md) for detailed features
- Check out the [PRD](my_agent_prd.md) for product vision
- Explore the API docs at http://localhost:8002/docs

## 🎓 Example Use Cases

### Financial Analyst
- Upload quarterly reports
- Ask: "What was the YoY revenue growth?"
- Export results for your presentation

### Legal Review
- Upload contracts
- Ask: "What are all the termination clauses?"
- Get instant citations with page numbers

### Due Diligence
- Upload company documents
- Ask: "What are the main business risks?"
- Get a comprehensive answer from multiple sources

---

**Need Help?** Check the [README.md](README.md) troubleshooting section or open an issue.

**Enjoy using Autonomous Diligence Cloud! 🚀**

