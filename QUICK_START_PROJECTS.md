# Quick Start: Multi-Project Feature

## 🎉 Your Diligence Cloud Now Supports Multiple Projects!

Based on the screenshot you shared, your vision has been implemented! You can now manage multiple due diligence projects like:
- **Acme Corp**
- **Nordic Telecoms**  
- **Lease Agreements**
- And more!

---

## 🚀 Getting Started (3 Easy Steps)

### Step 1: Open the Application
```
http://localhost:8002
```

You'll see the **Project Selector** in the header:

```
┌─────────────────────────────────────────────────────────────┐
│ 🅳 Diligence Cloud                                          │
│                                                             │
│    Project: [Default Project ▼] [+ New]  📊 Docs  📊 Q&A  │
└─────────────────────────────────────────────────────────────┘
```

### Step 2: Create Your First Project
1. Click the **"+ New"** button
2. Enter a name like **"Acme Corp"**
3. Add description: **"Acme Corp due diligence"**
4. Click **"Create Project"**

### Step 3: Upload Documents
1. Make sure **"Acme Corp"** is selected in the dropdown
2. Go to **"Upload Documents"** tab
3. Upload your documents (PDFs, Excel, Word, etc.)
4. Documents are now associated with Acme Corp project

### Step 4: Ask Questions
1. Go to **"Q&A Interface"** tab
2. Type your question
3. AI answers using ONLY documents from Acme Corp project

---

## 🎯 Example Workflow

### Managing Multiple Deals

#### Deal 1: Acme Corp
```
1. Create project: "Acme Corp Acquisition"
2. Upload: Financial statements, contracts, IP docs
3. Ask: "What are the revenue projections?"
4. Ask: "List all pending litigation"
```

#### Deal 2: Nordic Telecoms
```
1. Switch to: "Nordic Telecoms"
2. Upload: Market research, customer contracts  
3. Ask: "What is the customer retention rate?"
4. Ask: "Identify competitive advantages"
```

#### Deal 3: Real Estate
```
1. Switch to: "Lease Agreements Portfolio"
2. Upload: Lease documents, property reports
3. Ask: "Summarize lease terms expiring in 2025"
4. Ask: "What are the maintenance obligations?"
```

---

## 💡 Key Features

### ✅ Complete Isolation
- Each project has its own documents
- Q&A searches only within current project
- No mixing of data between projects

### ✅ Easy Switching
- Use dropdown to switch projects instantly
- UI reloads with selected project's data
- Previous project's Q&A is preserved

### ✅ Statistics Tracking
- Document count per project
- Question count per project
- Updated in real-time

### ✅ Organization
- Name projects clearly
- Add descriptions for context
- Keep related documents together

---

## 📱 User Interface Guide

### Header Layout
```
┌──────────────────────────────────────────────────────────┐
│  LOGO  Diligence Cloud                                   │
│         AI-Powered Platform                              │
│                                                          │
│  [Project Dropdown ▼] [+ New]  [📊 5 Docs] [📊 12 Q&A] │
└──────────────────────────────────────────────────────────┘
```

### Project Dropdown
```
┌─────────────────────────┐
│ ✓ Acme Corp            │  ← Currently selected
│   Nordic Telecoms       │
│   Lease Agreements      │
│   Beta Industries       │
│   Gamma LLC             │
└─────────────────────────┘
```

### Create Project Modal
```
┌────────────────────────────────────┐
│  Create New Project                │
├────────────────────────────────────┤
│                                    │
│  Project Name                      │
│  ┌──────────────────────────────┐ │
│  │ Acme Corp Acquisition        │ │
│  └──────────────────────────────┘ │
│                                    │
│  Description (Optional)            │
│  ┌──────────────────────────────┐ │
│  │ Due diligence for Acme Corp  │ │
│  │ acquisition Q1 2025          │ │
│  └──────────────────────────────┘ │
│                                    │
│        [Cancel]  [Create Project]  │
└────────────────────────────────────┘
```

---

## 🔄 Switching Projects

### Before Switch (Project: Acme Corp)
```
Documents: acme_financials.pdf, acme_contracts.pdf
Q&A: "What are the revenue streams?"
Answer: "Acme Corp has three main revenue streams..."
```

### After Switch (Project: Nordic Telecoms)
```
Documents: nordic_market.pdf, nordic_customers.xlsx
Q&A: [New empty table - ready for Nordic-specific questions]
```

### Switch Back (Project: Acme Corp)
```
Documents: acme_financials.pdf, acme_contracts.pdf
Q&A: [Previous questions preserved]
    "What are the revenue streams?"
    Answer: "Acme Corp has three main revenue streams..."
```

---

## 🎨 Visual Example (Based on Your Screenshot)

Your original vision:
```
Projects
  📁 Project Alpha
  📁 Co
  📁 Acme Corp
      📄 Acme Revenue
      📄 Acme Investment Risks
  📁 Nordic Telecoms
  📁 Lease Agreements
```

Now implemented as:
```
Project Selector (Dropdown)
  [Acme Corp]  ← Select this
  
  Documents Tab:
    📄 Acme Revenue.pdf
    📄 Acme Investment Risks.pdf
    
  Q&A Tab:
    Q: "What are the investment risks?"
    A: [AI answers using only Acme Corp documents]
```

---

## 🔧 API Testing

### Test the Feature via API

```bash
# 1. List all projects
curl http://localhost:8002/api/projects

# 2. Create "Acme Corp" project
curl -X POST http://localhost:8002/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Corp", 
    "description": "Acme acquisition"
  }'

# 3. Create "Nordic Telecoms" project  
curl -X POST http://localhost:8002/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Nordic Telecoms",
    "description": "Telecom evaluation"
  }'

# 4. List projects again (should see 3 total)
curl http://localhost:8002/api/projects
```

---

## ✅ Current Status

**Server Status:**
- ✅ Running on http://localhost:8002
- ✅ Phoenix observability on http://localhost:6006
- ✅ Project API endpoints active
- ✅ 2 projects currently exist:
  - Default Project
  - Acme Corp Acquisition

**Test It Now:**
```bash
# Open in browser
open http://localhost:8002

# Or test API
curl http://localhost:8002/api/projects
```

---

## 📚 More Information

- **Complete Guide**: See `PROJECT_MANAGEMENT_GUIDE.md`
- **Implementation Details**: See `PROJECT_FEATURE_SUMMARY.md`  
- **API Documentation**: Visit http://localhost:8002/docs

---

## 💬 Need Help?

### Common Questions

**Q: Can I rename a project?**  
A: Yes, use the UPDATE endpoint (PUT /api/projects/{id})

**Q: What happens to Q&A when I switch projects?**  
A: It's cleared from view but preserved per project

**Q: Can I move documents between projects?**  
A: Currently no, but you can re-upload to a different project

**Q: How do I delete a project?**  
A: Use DELETE /api/projects/{id} - this removes all documents too

**Q: Is there a limit on number of projects?**  
A: No limit, create as many as you need

---

## 🎊 Enjoy Your Multi-Project Setup!

You now have the power to:
- ✅ Organize multiple due diligence projects
- ✅ Keep documents and Q&A completely separate
- ✅ Switch between projects instantly
- ✅ Track statistics per project
- ✅ Scale to unlimited projects

**Happy analyzing!** 🚀

