#!/usr/bin/env python3
"""
Generate realistic due diligence data for testing Diligence Cloud
Creates projects, documents, and Q&A data
"""

import json
import random
import os
from datetime import datetime, timedelta
from pathlib import Path

# Sample company names and industries
COMPANIES = [
    {"name": "TechVenture AI", "industry": "Artificial Intelligence", "revenue": "$45M", "employees": 120},
    {"name": "GreenEnergy Solutions", "industry": "Renewable Energy", "revenue": "$78M", "employees": 250},
    {"name": "FinanceHub Inc", "industry": "FinTech", "revenue": "$92M", "employees": 180},
    {"name": "HealthTech Innovations", "industry": "Healthcare Technology", "revenue": "$63M", "employees": 150},
    {"name": "RetailNext Corp", "industry": "E-Commerce", "revenue": "$110M", "employees": 300},
]

# Document templates by category
DOCUMENT_CATEGORIES = {
    "financial": [
        "Annual Financial Statements",
        "Quarterly Reports Q1-Q4",
        "Cash Flow Analysis",
        "Revenue Projections 2024-2026",
        "Tax Returns 2021-2023",
        "Accounts Receivable Aging Report",
        "EBITDA Analysis",
        "Capital Expenditure Summary",
    ],
    "legal": [
        "Articles of Incorporation",
        "Shareholder Agreement",
        "Employment Contracts",
        "Intellectual Property Portfolio",
        "Pending Litigation Summary",
        "Regulatory Compliance Report",
        "Customer Contracts (Top 10)",
        "Vendor Agreements",
    ],
    "operational": [
        "Organizational Chart",
        "Key Employee Bios",
        "IT Infrastructure Overview",
        "Customer Acquisition Analysis",
        "Supply Chain Documentation",
        "Product Roadmap",
        "Market Analysis Report",
        "Competitive Landscape",
    ],
    "hr": [
        "Employee Handbook",
        "Compensation & Benefits Summary",
        "Turnover Analysis",
        "Key Person Dependencies",
        "Recruitment Strategy",
        "Training Programs Overview",
    ],
}

# Q&A templates by category
QA_TEMPLATES = {
    "financial": [
        ("What is the current revenue run rate?", "Based on the most recent quarterly reports, the annual revenue run rate is approximately {revenue}, showing {growth}% year-over-year growth."),
        ("What are the main revenue streams?", "The company generates revenue from three primary sources: {stream1} ({pct1}%), {stream2} ({pct2}%), and {stream3} ({pct3}%)."),
        ("What is the EBITDA margin?", "The EBITDA margin for the most recent fiscal year is {margin}%, which is {comparison} the industry average of {industry_avg}%."),
        ("Are there any outstanding debts?", "The company has ${debt}M in outstanding debt, consisting of {type1} and {type2}, with an average interest rate of {rate}%."),
        ("What are the major expenses?", "Major expense categories include: Personnel costs ({exp1}%), Technology/Infrastructure ({exp2}%), and Sales/Marketing ({exp3}%)."),
    ],
    "legal": [
        ("Are there any pending lawsuits?", "There are currently {num} pending litigation cases: {case1} and {case2}. Management estimates total exposure at ${exposure}M."),
        ("What IP does the company own?", "The company owns {patents} patents, {trademarks} trademarks, and has {copyright} copyrighted materials. Key patents include: {key_patent}."),
        ("Are all employees under contract?", "Yes, {pct}% of employees have signed employment agreements. {num} key employees have non-compete clauses extending {months} months post-employment."),
        ("What are the major customer contracts?", "Top 3 customer contracts represent {pct}% of revenue: {customer1} (${amt1}M/year), {customer2} (${amt2}M/year), {customer3} (${amt3}M/year)."),
        ("Any regulatory compliance issues?", "The company is {status} with all major regulatory requirements. Recent audit found {findings} minor findings, all addressed within {days} days."),
    ],
    "operational": [
        ("What is the customer acquisition cost?", "Current CAC is ${cac}, with an LTV/CAC ratio of {ratio}. The payback period is approximately {months} months."),
        ("How many customers does the company have?", "The company serves {total} customers, with {num_enterprise} enterprise clients accounting for {pct}% of revenue."),
        ("What is the customer churn rate?", "Annual churn rate is {rate}%, which is {comparison} the industry benchmark of {benchmark}%. Net retention rate is {retention}%."),
        ("What is the technology stack?", "The platform is built on {stack1}, {stack2}, and {stack3}. Infrastructure is hosted on {cloud_provider} with {reliability}% uptime."),
        ("How scalable is the infrastructure?", "Current infrastructure can support {multiple}x growth. Recent load testing showed capacity for {users}M concurrent users with {response}ms average response time."),
    ],
    "strategic": [
        ("What are the growth opportunities?", "Key growth opportunities include: {opp1}, {opp2}, and {opp3}. Management projects these could add ${revenue}M in revenue over {years} years."),
        ("Who are the main competitors?", "Primary competitors are {comp1}, {comp2}, and {comp3}. The company differentiates through {diff1} and {diff2}."),
        ("What are the key risks?", "Main risks identified: {risk1}, {risk2}, and {risk3}. Mitigation strategies are documented in the risk management framework."),
        ("What is the market size?", "The total addressable market is estimated at ${tam}B, with a serviceable addressable market of ${sam}B. Current market share is approximately {share}%."),
        ("What is the management team's experience?", "The executive team has an average of {years} years of industry experience. CEO previously {ceo_exp}, CFO led {cfo_exp}."),
    ],
}

# Sample data for filling templates
SAMPLE_DATA = {
    "revenue_streams": ["SaaS subscriptions", "Professional services", "Enterprise licensing", "API usage fees", "Maintenance contracts"],
    "debt_types": ["term loan", "credit line", "convertible notes", "equipment financing", "working capital facility"],
    "litigation_cases": ["vendor dispute", "IP infringement claim", "employment matter", "customer contract dispute", "regulatory inquiry"],
    "patent_areas": ["machine learning algorithms", "data processing methods", "user interface designs", "security protocols", "API frameworks"],
    "customers": ["Fortune 500 manufacturer", "Global financial services firm", "Leading healthcare provider", "Major retail chain", "Technology conglomerate"],
    "tech_stack": ["React/Node.js", "Python/Django", "AWS Lambda", "Kubernetes", "PostgreSQL", "Redis", "Elasticsearch", "GraphQL"],
    "cloud_providers": ["AWS", "Google Cloud", "Azure"],
    "growth_opps": ["international expansion", "new product lines", "strategic partnerships", "vertical integration", "M&A opportunities"],
    "competitors": ["MarketLeader Inc", "IndustryGiant Corp", "StartupDisruptor", "Legacy Systems Ltd", "NewEntrant Tech"],
    "differentiators": ["proprietary AI technology", "superior customer support", "lower pricing model", "faster implementation", "better integration capabilities"],
    "risks": ["customer concentration", "key person dependency", "technology obsolescence", "regulatory changes", "competitive pressure", "market saturation"],
}


def generate_project_data(company_info, project_id):
    """Generate a complete project with documents and Q&A"""
    
    project_name = f"{company_info['name']} - Due Diligence"
    
    # Generate documents
    documents = []
    doc_id = 1
    
    for category, doc_types in DOCUMENT_CATEGORIES.items():
        for doc_name in doc_types:
            documents.append({
                "id": f"{project_id}_doc_{doc_id}",
                "name": doc_name,
                "category": category,
                "upload_date": (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
                "pages": random.randint(5, 150),
                "status": random.choice(["reviewed", "pending", "reviewed", "reviewed"]),
            })
            doc_id += 1
    
    # Generate Q&A pairs
    qa_pairs = []
    qa_id = 1
    
    for category, templates in QA_TEMPLATES.items():
        num_questions = random.randint(2, len(templates))
        selected_templates = random.sample(templates, num_questions)
        
        for question_template, answer_template in selected_templates:
            # Fill in the template with random data
            answer = fill_answer_template(answer_template, company_info)
            
            qa_pairs.append({
                "id": qa_id,
                "question": question_template,
                "answer": answer,
                "category": category,
                "source": random.choice([doc["name"] for doc in documents if doc["category"] == category] or ["General Analysis"]),
                "status": random.choice(["✓ Verified", "⚠ Review", "✓ Verified", "✓ Verified"]),
                "date": (datetime.now() - timedelta(days=random.randint(0, 60))).strftime("%Y-%m-%d"),
                "confidence": random.choice(["95%", "90%", "85%", "95%", "95%"]),
            })
            qa_id += 1
    
    return {
        "project": {
            "id": project_id,
            "name": project_name,
            "company": company_info["name"],
            "industry": company_info["industry"],
            "revenue": company_info["revenue"],
            "employees": company_info["employees"],
            "created_date": (datetime.now() - timedelta(days=random.randint(30, 180))).isoformat(),
            "status": random.choice(["Active", "Active", "In Progress", "Active"]),
        },
        "documents": documents,
        "qa_pairs": qa_pairs,
    }


def fill_answer_template(template, company_info):
    """Fill answer template with random but realistic data"""
    
    replacements = {
        "{revenue}": company_info["revenue"],
        "{growth}": str(random.randint(15, 45)),
        "{stream1}": random.choice(SAMPLE_DATA["revenue_streams"]),
        "{stream2}": random.choice([s for s in SAMPLE_DATA["revenue_streams"]]),
        "{stream3}": random.choice([s for s in SAMPLE_DATA["revenue_streams"]]),
        "{pct1}": str(random.randint(40, 60)),
        "{pct2}": str(random.randint(20, 35)),
        "{pct3}": str(random.randint(10, 25)),
        "{margin}": str(random.randint(18, 35)),
        "{comparison}": random.choice(["above", "in line with", "slightly below"]),
        "{industry_avg}": str(random.randint(20, 30)),
        "{debt}": str(random.randint(5, 25)),
        "{type1}": random.choice(SAMPLE_DATA["debt_types"]),
        "{type2}": random.choice(SAMPLE_DATA["debt_types"]),
        "{rate}": str(round(random.uniform(4.5, 8.5), 1)),
        "{exp1}": str(random.randint(45, 60)),
        "{exp2}": str(random.randint(15, 25)),
        "{exp3}": str(random.randint(15, 25)),
        "{num}": str(random.randint(1, 3)),
        "{case1}": random.choice(SAMPLE_DATA["litigation_cases"]),
        "{case2}": random.choice(SAMPLE_DATA["litigation_cases"]),
        "{exposure}": str(round(random.uniform(0.5, 5.0), 1)),
        "{patents}": str(random.randint(5, 25)),
        "{trademarks}": str(random.randint(3, 12)),
        "{copyright}": str(random.randint(10, 50)),
        "{key_patent}": random.choice(SAMPLE_DATA["patent_areas"]),
        "{pct}": str(random.randint(85, 100)),
        "{months}": str(random.randint(12, 24)),
        "{customer1}": random.choice(SAMPLE_DATA["customers"]),
        "{customer2}": random.choice(SAMPLE_DATA["customers"]),
        "{customer3}": random.choice(SAMPLE_DATA["customers"]),
        "{amt1}": str(round(random.uniform(5, 20), 1)),
        "{amt2}": str(round(random.uniform(3, 15), 1)),
        "{amt3}": str(round(random.uniform(2, 10), 1)),
        "{status}": random.choice(["fully compliant", "substantially compliant"]),
        "{findings}": str(random.randint(0, 5)),
        "{days}": str(random.randint(15, 45)),
        "{cac}": str(random.randint(500, 3000)),
        "{ratio}": str(round(random.uniform(3.0, 8.0), 1)),
        "{total}": str(random.randint(500, 5000)),
        "{num_enterprise}": str(random.randint(25, 150)),
        "{rate}": str(round(random.uniform(5, 15), 1)),
        "{benchmark}": str(round(random.uniform(10, 20), 1)),
        "{retention}": str(random.randint(110, 130)),
        "{stack1}": random.choice(SAMPLE_DATA["tech_stack"]),
        "{stack2}": random.choice(SAMPLE_DATA["tech_stack"]),
        "{stack3}": random.choice(SAMPLE_DATA["tech_stack"]),
        "{cloud_provider}": random.choice(SAMPLE_DATA["cloud_providers"]),
        "{reliability}": str(round(random.uniform(99.5, 99.99), 2)),
        "{multiple}": str(random.randint(3, 10)),
        "{users}": str(round(random.uniform(1, 10), 1)),
        "{response}": str(random.randint(50, 200)),
        "{opp1}": random.choice(SAMPLE_DATA["growth_opps"]),
        "{opp2}": random.choice(SAMPLE_DATA["growth_opps"]),
        "{opp3}": random.choice(SAMPLE_DATA["growth_opps"]),
        "{years}": str(random.randint(2, 5)),
        "{comp1}": random.choice(SAMPLE_DATA["competitors"]),
        "{comp2}": random.choice(SAMPLE_DATA["competitors"]),
        "{comp3}": random.choice(SAMPLE_DATA["competitors"]),
        "{diff1}": random.choice(SAMPLE_DATA["differentiators"]),
        "{diff2}": random.choice(SAMPLE_DATA["differentiators"]),
        "{risk1}": random.choice(SAMPLE_DATA["risks"]),
        "{risk2}": random.choice(SAMPLE_DATA["risks"]),
        "{risk3}": random.choice(SAMPLE_DATA["risks"]),
        "{tam}": str(random.randint(5, 50)),
        "{sam}": str(random.randint(1, 10)),
        "{share}": str(round(random.uniform(2, 15), 1)),
        "{ceo_exp}": random.choice(["built a $100M+ company", "led digital transformation at Fortune 500", "serial entrepreneur with 3 exits"]),
        "{cfo_exp}": random.choice(["IPO at tech unicorn", "M&A at investment bank", "finance transformation at PE firm"]),
    }
    
    result = template
    for key, value in replacements.items():
        result = result.replace(key, value)
    
    return result


def generate_sample_document_content(doc_info):
    """Generate sample document text content"""
    
    content_templates = {
        "financial": """
FINANCIAL STATEMENT ANALYSIS

Company: {company}
Period: FY 2023
Prepared: {date}

EXECUTIVE SUMMARY:
The company demonstrates strong financial performance with revenue of {revenue} and year-over-year growth of {growth}%. 
Key financial metrics indicate healthy operations with positive cash flow and sustainable growth trajectory.

REVENUE BREAKDOWN:
- Primary revenue stream: {stream1}
- Secondary streams: {stream2}, {stream3}
- Customer concentration: Top 10 customers represent {concentration}% of revenue

PROFITABILITY:
- Gross Margin: {gross_margin}%
- EBITDA: ${ebitda}M
- Net Income: ${net_income}M

CASH POSITION:
- Cash and equivalents: ${cash}M
- Working capital: ${working_capital}M
- Burn rate: ${burn_rate}M/month
""",
        "legal": """
LEGAL DUE DILIGENCE SUMMARY

Company: {company}
Review Date: {date}

CORPORATE STRUCTURE:
The company is incorporated in Delaware as a C-Corporation. Corporate records are complete and up-to-date.

INTELLECTUAL PROPERTY:
- {patents} patents (granted and pending)
- {trademarks} registered trademarks
- Comprehensive IP assignment agreements in place

CONTRACTS:
- Customer contracts: {num_customer} active agreements
- Vendor agreements: {num_vendor} active relationships
- All material contracts reviewed and documented

LITIGATION:
Current status: {litigation_status}
{litigation_details}

COMPLIANCE:
The company maintains compliance with all applicable regulations including data privacy (GDPR, CCPA) and industry-specific requirements.
""",
        "operational": """
OPERATIONAL DUE DILIGENCE REPORT

Company: {company}
Assessment Date: {date}

BUSINESS MODEL:
{business_model_desc}

CUSTOMER BASE:
- Total customers: {total_customers}
- Customer segments: {segments}
- Retention rate: {retention}%

TECHNOLOGY INFRASTRUCTURE:
- Platform: {tech_platform}
- Hosting: {cloud_provider}
- Uptime: {uptime}%
- Security: SOC 2 Type II certified

KEY METRICS:
- Monthly Recurring Revenue: ${mrr}M
- Average Contract Value: ${acv}K
- Customer Acquisition Cost: ${cac}

TEAM:
- Total employees: {employees}
- Engineering: {eng_pct}%
- Sales/Marketing: {sales_pct}%
- G&A: {ga_pct}%
""",
    }
    
    category = doc_info.get("category", "operational")
    template = content_templates.get(category, content_templates["operational"])
    
    # Generate random but realistic values
    content = template.format(
        company=doc_info.get("company", "TechCo"),
        date=datetime.now().strftime("%B %Y"),
        revenue=f"${random.randint(50, 200)}M",
        growth=random.randint(25, 60),
        stream1=random.choice(SAMPLE_DATA["revenue_streams"]),
        stream2=random.choice(SAMPLE_DATA["revenue_streams"]),
        stream3=random.choice(SAMPLE_DATA["revenue_streams"]),
        concentration=random.randint(30, 60),
        gross_margin=random.randint(65, 85),
        ebitda=round(random.uniform(10, 40), 1),
        net_income=round(random.uniform(5, 25), 1),
        cash=round(random.uniform(15, 50), 1),
        working_capital=round(random.uniform(10, 30), 1),
        burn_rate=round(random.uniform(1, 5), 1),
        patents=random.randint(5, 25),
        trademarks=random.randint(3, 12),
        num_customer=random.randint(50, 200),
        num_vendor=random.randint(20, 80),
        litigation_status=random.choice(["No active litigation", "Minor pending matters", "Standard commercial disputes"]),
        litigation_details=random.choice(["", "See detailed litigation schedule for specifics."]),
        business_model_desc="SaaS-based platform with subscription pricing model. Mix of self-service and enterprise sales.",
        total_customers=random.randint(500, 5000),
        segments="SMB (60%), Mid-Market (30%), Enterprise (10%)",
        retention=random.randint(85, 95),
        tech_platform=random.choice(SAMPLE_DATA["tech_stack"]),
        cloud_provider=random.choice(SAMPLE_DATA["cloud_providers"]),
        uptime=round(random.uniform(99.5, 99.99), 2),
        mrr=round(random.uniform(5, 20), 1),
        acv=random.randint(15, 75),
        cac=random.randint(800, 3500),
        employees=random.randint(100, 500),
        eng_pct=random.randint(40, 60),
        sales_pct=random.randint(25, 35),
        ga_pct=random.randint(10, 20),
    )
    
    return content


def main():
    """Generate all test data"""
    
    print("🚀 Generating Diligence Cloud Test Data...")
    print("=" * 70)
    
    # Create output directory
    output_dir = Path(__file__).parent / "generated_data"
    output_dir.mkdir(exist_ok=True)
    
    all_projects = []
    
    # Generate data for each company
    for idx, company in enumerate(COMPANIES, 1):
        project_id = f"project_{idx}"
        print(f"\n📁 Generating project {idx}/{len(COMPANIES)}: {company['name']}")
        
        project_data = generate_project_data(company, project_id)
        all_projects.append(project_data)
        
        print(f"   ✓ {len(project_data['documents'])} documents")
        print(f"   ✓ {len(project_data['qa_pairs'])} Q&A pairs")
        
        # Save individual project
        project_file = output_dir / f"{project_id}.json"
        with open(project_file, 'w') as f:
            json.dump(project_data, f, indent=2)
        print(f"   ✓ Saved to {project_file}")
        
        # Generate sample document content
        sample_docs_dir = output_dir / project_id / "documents"
        sample_docs_dir.mkdir(parents=True, exist_ok=True)
        
        for doc in random.sample(project_data['documents'], min(5, len(project_data['documents']))):
            doc_content = generate_sample_document_content({
                **doc,
                "company": company["name"]
            })
            doc_file = sample_docs_dir / f"{doc['id']}.txt"
            with open(doc_file, 'w') as f:
                f.write(doc_content)
    
    # Save combined data
    combined_file = output_dir / "all_projects.json"
    with open(combined_file, 'w') as f:
        json.dump(all_projects, f, indent=2)
    
    print("\n" + "=" * 70)
    print("✅ Data generation complete!")
    print(f"\n📊 SUMMARY:")
    print(f"   • Projects: {len(all_projects)}")
    print(f"   • Total documents: {sum(len(p['documents']) for p in all_projects)}")
    print(f"   • Total Q&A pairs: {sum(len(p['qa_pairs']) for p in all_projects)}")
    print(f"\n📂 Output directory: {output_dir}")
    print(f"\n💡 TIP: Use the JSON files to import data into your Diligence Cloud instance!")
    print("=" * 70)


if __name__ == "__main__":
    main()


