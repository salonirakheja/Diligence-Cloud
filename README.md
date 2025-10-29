# 🧠 Autonomous Diligence Cloud

An AI-powered document intelligence platform that reads PDFs, Excel files, Word documents, and answers questions using advanced RAG (Retrieval Augmented Generation) technology.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## 🌟 Features

### 📄 Multi-Format Document Processing
- **PDF Documents** - Extract text from any PDF file
- **Excel Files** - Process .xlsx, .xls, and .csv files
- **Word Documents** - Read .docx files
- **Text Files** - Support for .txt files

### 💬 Intelligent Q&A Interface
- Ask questions in natural language
- Get AI-powered answers with source citations
- Batch question processing (ask multiple questions at once)
- Confidence scoring for each answer
- Export results to Excel for reporting

### 🎯 Advanced Features
- **Semantic Search** - Find relevant information regardless of exact wording
- **Multi-Document Synthesis** - Combine information from multiple files
- **Source Attribution** - Every answer cites its sources with page numbers
- **Real-time Processing** - Upload and query documents instantly
- **Beautiful UI** - Modern, responsive interface

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- OpenAI API key (or OpenRouter API key)

### Installation

1. **Clone or Download** this repository
2. **Get an API Key**
   - OpenAI: https://platform.openai.com/api-keys
   - Or use OpenRouter: https://openrouter.ai/

3. **Configure Environment**
   - Rename `env_template.txt` to `.env`
   - Add your API key:
     ```env
     OPENAI_API_KEY=your_key_here
     ```

4. **Start the Server**
   ```bash
   # Windows Command Prompt
   start_server.cmd
   
   # Windows PowerShell
   .\start_server.ps1
   ```

5. **Open Your Browser**
   - Navigate to: http://localhost:8002
   - Start uploading documents and asking questions!

## 📖 Usage Guide

### Step 1: Upload Documents
1. Click the **"Upload Documents"** tab
2. Drag & drop your files or click to select
3. Wait for processing to complete (usually a few seconds)
4. View your uploaded documents in the grid

### Step 2: Ask Questions
1. Click the **"Q&A Interface"** tab
2. Type your question in the input field
3. Click **"Ask"** to get an answer
4. Review the answer, sources, and confidence score
5. Add more questions as needed

### Step 3: Export Results
1. After asking multiple questions
2. Click **"Export to Excel"**
3. Download your Q&A results as a spreadsheet

## 💡 Example Questions

### Financial Analysis
```
What was the revenue for Q3 2024?
Compare profit margins across all quarters
What are the key financial risks mentioned?
```

### Legal Review
```
Summarize all termination clauses
What are the payment terms in these contracts?
List all parties mentioned in the agreements
```

### Due Diligence
```
What are the main business risks?
Summarize the management team's background
What is the company's competitive advantage?
```

### Data Analysis
```
What is the average salary by department?
How many employees joined in the last year?
Compare sales performance across regions
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│           Frontend (HTML/JavaScript)             │
│  - Q&A Interface (Excel-like table)              │
│  - Document Upload (Drag & drop)                 │
└─────────────────┬───────────────────────────────┘
                  │ HTTP/REST API
┌─────────────────▼───────────────────────────────┐
│              FastAPI Backend                     │
│  - Document Processing (PDF, Excel, Word)        │
│  - Vector Store (ChromaDB)                       │
│  - AI Agents (OpenAI/OpenRouter)                 │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│             Data Layer                           │
│  - Uploaded Files (backend/uploads/)             │
│  - Vector Database (data/vector_db/)             │
└──────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
Diligence Cloud/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── agents.py            # AI agents
│   ├── document_processor.py # File parsing
│   ├── vector_store.py      # Vector database
│   ├── requirements.txt     # Python dependencies
│   └── uploads/             # Temporary file storage
├── frontend/
│   └── index.html           # Two-page interface
├── data/
│   └── vector_db/           # Vector database storage
├── my_agent_prd.md          # Product requirements
├── README.md                # This file
├── env_template.txt         # Environment template
├── start_server.cmd         # Windows startup script
└── start_server.ps1         # PowerShell startup script
```

## 🔧 Configuration

### Environment Variables

Edit your `.env` file to configure:

```env
# AI Provider (required)
OPENAI_API_KEY=your_key_here

# Server Settings (optional)
HOST=0.0.0.0
PORT=8002

# Document Processing (optional)
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### Supported File Types

| Format | Extension | Notes |
|--------|-----------|-------|
| PDF | .pdf | Text extraction (OCR coming soon) |
| Excel | .xlsx, .xls, .csv | All sheets processed |
| Word | .docx | Text and tables |
| Text | .txt | Plain text files |

## 🎨 API Documentation

Once the server is running, access the interactive API docs at:
- **Swagger UI**: http://localhost:8002/docs
- **ReDoc**: http://localhost:8002/redoc

### Key Endpoints

```
POST   /api/upload              Upload a document
POST   /api/ask                 Ask a question
POST   /api/batch-ask           Ask multiple questions
GET    /api/documents           List all documents
GET    /api/documents/{id}      Get document details
DELETE /api/documents/{id}      Delete a document
GET    /api/export              Export Q&A to Excel
GET    /health                  Health check
```

## 🚨 Troubleshooting

### Server Won't Start

**Problem**: "Python is not installed"
- **Solution**: Install Python 3.9+ from [python.org](https://python.org)

**Problem**: "No API key configured"
- **Solution**: Create `.env` file and add your `OPENAI_API_KEY`

**Problem**: "Port 8002 already in use"
- **Solution**: Change `PORT` in `.env` file to a different number (e.g., 8003)

### Upload Fails

**Problem**: "Unsupported file type"
- **Solution**: Only upload PDF, Excel, Word, or Text files

**Problem**: "Upload timeout"
- **Solution**: Large files (>50MB) may take longer. Check your internet connection.

### Questions Not Answering

**Problem**: "I don't have enough information"
- **Solution**: Upload relevant documents first before asking questions

**Problem**: Low confidence scores
- **Solution**: Ensure your documents contain the information you're asking about

## 🔒 Security & Privacy

- All documents are stored locally on your machine
- No data is shared with third parties (except AI provider for processing)
- API keys are stored in `.env` file (never commit to git)
- Uploaded files can be deleted at any time

## 🛣️ Roadmap

### Phase 2 (Coming Soon)
- [ ] OCR support for scanned PDFs
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Document comparison tool

### Phase 3 (Future)
- [ ] User authentication
- [ ] Team collaboration features
- [ ] Cloud storage integration (Google Drive, Dropbox)
- [ ] Real-time collaboration
- [ ] Mobile app

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [OpenAI](https://openai.com/)
- Vector database by [ChromaDB](https://www.trychroma.com/)

## 📧 Support

For questions or support:
- Check the troubleshooting section above
- Review the API documentation at `/docs`
- Open an issue on GitHub

---

**Built with ❤️ for due diligence professionals**

