# Data Generation Guide

Generate realistic test data for your Diligence Cloud instance.

## 📋 Overview

The data generation system creates:
- **5 realistic company due diligence projects**
- **150+ documents** across financial, legal, operational, and HR categories
- **70+ Q&A pairs** with detailed answers
- **Sample document content** for testing

## 🚀 Quick Start

### Step 1: Generate Data

```bash
python3 generate_diligence_data.py
```

This creates:
- `generated_data/` directory
- Individual project JSON files (`project_1.json`, `project_2.json`, etc.)
- `all_projects.json` with combined data
- Sample document text files

### Step 2: Import Data (Optional)

```bash
# Make sure your server is running first
python3 backend/main.py

# In another terminal, run the import script
python3 import_generated_data.py
```

## 📊 Generated Companies

The script generates due diligence data for 5 fictional companies:

1. **TechVenture AI** - Artificial Intelligence ($45M revenue, 120 employees)
2. **GreenEnergy Solutions** - Renewable Energy ($78M revenue, 250 employees)
3. **FinanceHub Inc** - FinTech ($92M revenue, 180 employees)
4. **HealthTech Innovations** - Healthcare Technology ($63M revenue, 150 employees)
5. **RetailNext Corp** - E-Commerce ($110M revenue, 300 employees)

## 📁 Document Categories

Each project includes documents in these categories:

### Financial
- Annual Financial Statements
- Quarterly Reports Q1-Q4
- Cash Flow Analysis
- Revenue Projections 2024-2026
- Tax Returns 2021-2023
- EBITDA Analysis
- Capital Expenditure Summary

### Legal
- Articles of Incorporation
- Shareholder Agreement
- Employment Contracts
- Intellectual Property Portfolio
- Pending Litigation Summary
- Regulatory Compliance Report
- Customer Contracts (Top 10)

### Operational
- Organizational Chart
- Key Employee Bios
- IT Infrastructure Overview
- Customer Acquisition Analysis
- Supply Chain Documentation
- Product Roadmap
- Market Analysis Report

### HR
- Employee Handbook
- Compensation & Benefits Summary
- Turnover Analysis
- Key Person Dependencies
- Recruitment Strategy

## 💬 Q&A Categories

Generated Q&A pairs cover:

### Financial Questions
- Revenue run rate and growth
- Revenue streams breakdown
- EBITDA margins
- Outstanding debts
- Major expense categories

### Legal Questions
- Pending lawsuits
- Intellectual property ownership
- Employment contracts
- Customer contracts
- Regulatory compliance

### Operational Questions
- Customer acquisition cost
- Customer count and churn
- Technology stack
- Infrastructure scalability

### Strategic Questions
- Growth opportunities
- Competitive landscape
- Key risks
- Market size
- Management team experience

## 📂 Output Structure

```
generated_data/
├── all_projects.json           # Combined data for all projects
├── project_1.json              # TechVenture AI data
├── project_1/
│   └── documents/
│       ├── project_1_doc_1.txt
│       ├── project_1_doc_2.txt
│       └── ...
├── project_2.json              # GreenEnergy Solutions data
├── project_2/
│   └── documents/
│       └── ...
└── ...
```

## 🎨 Customization

### Add More Companies

Edit `generate_diligence_data.py` and add to the `COMPANIES` list:

```python
COMPANIES = [
    {"name": "Your Company", "industry": "Your Industry", "revenue": "$XXM", "employees": XXX},
    # ... existing companies
]
```

### Add Custom Document Types

Add to `DOCUMENT_CATEGORIES`:

```python
DOCUMENT_CATEGORIES = {
    "your_category": [
        "Document Type 1",
        "Document Type 2",
    ],
    # ... existing categories
}
```

### Add Custom Q&A Templates

Add to `QA_TEMPLATES`:

```python
QA_TEMPLATES = {
    "your_category": [
        ("Question?", "Answer with {placeholder} variables"),
    ],
    # ... existing templates
}
```

## 📈 Data Statistics

Per project:
- **30 documents** on average
- **12-18 Q&A pairs**
- **5 sample document files**

Total across all projects:
- **150 documents**
- **70+ Q&A pairs**
- **25 sample document files**

## 💡 Use Cases

### 1. Demo & Presentations
Generate realistic data to showcase Diligence Cloud capabilities

### 2. Testing
Test the system with substantial data before real deployment

### 3. Development
Develop new features against realistic data sets

### 4. Training
Train users on the system with safe, fictional data

### 5. Performance Testing
Test system performance with multiple projects and documents

## 🔧 Technical Details

### Data Generation
- Uses templates with placeholder variables
- Generates random but realistic values
- Maintains data consistency within projects
- Creates unique IDs for all entities

### Sample Data Includes
- Financial metrics (revenue, margins, growth rates)
- Legal information (patents, contracts, litigation)
- Operational metrics (CAC, churn, retention)
- Strategic insights (market size, competitors, risks)

## 📝 JSON Schema

### Project Structure
```json
{
  "project": {
    "id": "project_1",
    "name": "TechVenture AI - Due Diligence",
    "company": "TechVenture AI",
    "industry": "Artificial Intelligence",
    "revenue": "$45M",
    "employees": 120,
    "created_date": "2024-01-15T10:30:00",
    "status": "Active"
  },
  "documents": [...],
  "qa_pairs": [...]
}
```

### Document Structure
```json
{
  "id": "project_1_doc_1",
  "name": "Annual Financial Statements",
  "category": "financial",
  "upload_date": "2024-03-15T14:20:00",
  "pages": 45,
  "status": "reviewed"
}
```

### Q&A Structure
```json
{
  "id": 1,
  "question": "What is the current revenue run rate?",
  "answer": "Based on the most recent quarterly reports...",
  "category": "financial",
  "source": "Quarterly Reports Q1-Q4",
  "status": "✓ Verified",
  "date": "2024-03-20",
  "confidence": "95%"
}
```

## 🛠 Troubleshooting

### "No module named 'requests'"
```bash
pip3 install requests
```

### "Generated data not found"
Run the generation script first:
```bash
python3 generate_diligence_data.py
```

### "Cannot connect to server"
Make sure the Diligence Cloud server is running:
```bash
python3 backend/main.py
```

## 🎯 Next Steps

1. **Generate data**: `python3 generate_diligence_data.py`
2. **Review JSON files** in `generated_data/`
3. **Customize** companies, documents, or Q&A as needed
4. **Import data** manually or via API
5. **Test** your Diligence Cloud features

## 📚 Related Files

- `generate_diligence_data.py` - Main data generation script
- `import_generated_data.py` - API import helper (template)
- `generated_data/` - Output directory (created on first run)

---

**Note**: All generated data is fictional and created for testing purposes only. Company names, financial figures, and other details are randomly generated and do not represent real entities.


