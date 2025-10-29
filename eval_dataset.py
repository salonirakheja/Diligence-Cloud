"""
Evaluation Dataset for Diligence Cloud
Generated from realistic due diligence test data
"""

import json
from pathlib import Path

# Load generated data
DATA_DIR = Path(__file__).parent / "generated_data"

def load_generated_data():
    """Load all generated projects"""
    with open(DATA_DIR / "all_projects.json", 'r') as f:
        return json.load(f)

# Evaluation test cases
EVAL_DATASET = [
    # ===================================================================
    # FINANCIAL QUESTIONS
    # ===================================================================
    {
        "id": "fin_001",
        "question": "What is the current revenue run rate?",
        "category": "financial",
        "project_name": "Tech Venture AI - Due Diligence",
        "difficulty": "easy",
        "expected_answer_contains": ["revenue", "million", "growth"],
        "expected_sources": ["project_1_doc"],  # Flexible matching
        "expected_agents": ["DocumentAgent", "AnalysisAgent"],
        "ground_truth": "Based on the most recent quarterly reports, the annual revenue run rate shows the company's financial performance.",
        "eval_criteria": {
            "has_revenue_figure": True,
            "has_growth_metric": True,
            "cites_financial_docs": True,
        }
    },
    {
        "id": "fin_002",
        "question": "What is the EBITDA margin?",
        "category": "financial",
        "project_name": "Tech Venture AI - Due Diligence",
        "difficulty": "easy",
        "expected_answer_contains": ["EBITDA", "margin", "%"],
        "expected_sources": ["EBITDA Analysis", "Annual Financial Statements"],
        "expected_agents": ["DocumentAgent", "DataExtractionAgent"],
        "ground_truth": "The EBITDA margin is a key profitability metric that should be compared to industry averages.",
        "eval_criteria": {
            "has_percentage": True,
            "mentions_ebitda": True,
            "has_comparison": False,  # Optional
        }
    },
    {
        "id": "fin_003",
        "question": "Are there any outstanding debts?",
        "category": "financial",
        "project_name": "Tech Venture AI - Due Diligence",
        "difficulty": "medium",
        "expected_answer_contains": ["debt", "outstanding", "million", "interest"],
        "expected_sources": ["Annual Financial Statements", "Cash Flow Analysis"],
        "expected_agents": ["DocumentAgent", "AnalysisAgent", "DataExtractionAgent"],
        "ground_truth": "The company has outstanding debt that should be detailed with amounts, types, and interest rates.",
        "eval_criteria": {
            "has_debt_amount": True,
            "has_debt_type": True,
            "has_interest_rate": True,
        }
    },
    {
        "id": "fin_004",
        "question": "What are the main revenue streams?",
        "category": "financial",
        "project_name": "Tech Venture AI - Due Diligence",
        "difficulty": "medium",
        "expected_answer_contains": ["revenue", "stream", "%"],
        "expected_sources": ["Annual Financial Statements", "Revenue Projections"],
        "expected_agents": ["DocumentAgent", "AnalysisAgent"],
        "ground_truth": "Revenue streams should be broken down by category with percentage contributions.",
        "eval_criteria": {
            "lists_multiple_streams": True,
            "has_percentages": True,
            "has_breakdown": True,
        }
    },
    {
        "id": "fin_005",
        "question": "What are the major expenses?",
        "category": "financial",
        "project_name": "Tech Venture AI - Due Diligence",
        "difficulty": "medium",
        "expected_answer_contains": ["expense", "cost", "%"],
        "expected_sources": ["Annual Financial Statements", "EBITDA Analysis"],
        "expected_agents": ["DocumentAgent", "AnalysisAgent"],
        "ground_truth": "Major expense categories should be listed with their relative sizes.",
        "eval_criteria": {
            "lists_expense_categories": True,
            "has_percentages": True,
        }
    },
    
    # ===================================================================
    # LEGAL QUESTIONS
    # ===================================================================
    {
        "id": "legal_001",
        "question": "Are there any pending lawsuits?",
        "category": "legal",
        "project_name": "Tech Venture AI - Due Diligence",
        "difficulty": "easy",
        "expected_answer_contains": ["litigation", "lawsuit", "pending"],
        "expected_sources": ["Pending Litigation Summary"],
        "expected_agents": ["DocumentAgent", "AnalysisAgent"],
        "ground_truth": "Litigation status should be clearly stated with number of cases and exposure amounts.",
        "eval_criteria": {
            "states_litigation_status": True,
            "has_case_count": True,
            "mentions_exposure": True,
        }
    },
    {
        "id": "legal_002",
        "question": "What intellectual property does the company own?",
        "category": "legal",
        "project_name": "Tech Venture AI - Due Diligence",
        "difficulty": "medium",
        "expected_answer_contains": ["patent", "trademark", "intellectual property", "IP"],
        "expected_sources": ["Intellectual Property Portfolio"],
        "expected_agents": ["DocumentAgent", "AnalysisAgent"],
        "ground_truth": "IP portfolio should list patents, trademarks, and copyrights with key assets.",
        "eval_criteria": {
            "mentions_patents": True,
            "mentions_trademarks": True,
            "has_counts": True,
        }
    },
    {
        "id": "legal_003",
        "question": "Are all employees under contract?",
        "category": "legal",
        "project_name": "Tech Venture AI - Due Diligence",
        "difficulty": "easy",
        "expected_answer_contains": ["employee", "contract", "%"],
        "expected_sources": ["Employment Contracts"],
        "expected_agents": ["DocumentAgent"],
        "ground_truth": "Employment contract coverage should be stated as a percentage with details on key employees.",
        "eval_criteria": {
            "has_percentage": True,
            "mentions_contracts": True,
        }
    },
    {
        "id": "legal_004",
        "question": "What are the major customer contracts?",
        "category": "legal",
        "project_name": "Tech Venture AI - Due Diligence",
        "difficulty": "medium",
        "expected_answer_contains": ["customer", "contract", "revenue"],
        "expected_sources": ["Customer Contracts (Top 10)"],
        "expected_agents": ["DocumentAgent", "AnalysisAgent", "DataExtractionAgent"],
        "ground_truth": "Major customer contracts should list top customers with contract values.",
        "eval_criteria": {
            "lists_customers": True,
            "has_contract_values": True,
            "shows_revenue_impact": True,
        }
    },
    {
        "id": "legal_005",
        "question": "Any regulatory compliance issues?",
        "category": "legal",
        "project_name": "Tech Venture AI - Due Diligence",
        "difficulty": "medium",
        "expected_answer_contains": ["compliance", "regulatory", "audit"],
        "expected_sources": ["Regulatory Compliance Report"],
        "expected_agents": ["DocumentAgent", "AnalysisAgent"],
        "ground_truth": "Compliance status should be stated with any findings and remediation.",
        "eval_criteria": {
            "states_compliance_status": True,
            "mentions_audit": True,
        }
    },
    
    # ===================================================================
    # OPERATIONAL QUESTIONS
    # ===================================================================
    {
        "id": "ops_001",
        "question": "What is the customer acquisition cost?",
        "category": "operational",
        "project_name": "Tech Venture AI - Due Diligence",
        "difficulty": "easy",
        "expected_answer_contains": ["CAC", "customer acquisition", "$", "LTV"],
        "expected_sources": ["Customer Acquisition Analysis"],
        "expected_agents": ["DocumentAgent", "DataExtractionAgent"],
        "ground_truth": "CAC should be stated with LTV/CAC ratio and payback period.",
        "eval_criteria": {
            "has_cac_value": True,
            "has_ltv_ratio": True,
            "has_payback_period": False,  # Optional
        }
    },
    {
        "id": "ops_002",
        "question": "How many customers does the company have?",
        "category": "operational",
        "project_name": "Tech Venture AI - Due Diligence",
        "difficulty": "easy",
        "expected_answer_contains": ["customer", "clients"],
        "expected_sources": ["Customer Acquisition Analysis", "Market Analysis Report"],
        "expected_agents": ["DocumentAgent", "DataExtractionAgent"],
        "ground_truth": "Customer count should include total and breakdown by segment.",
        "eval_criteria": {
            "has_customer_count": True,
            "has_segment_breakdown": False,  # Optional
        }
    },
    {
        "id": "ops_003",
        "question": "What is the customer churn rate?",
        "category": "operational",
        "project_name": "Tech Venture AI - Due Diligence",
        "difficulty": "medium",
        "expected_answer_contains": ["churn", "%", "retention"],
        "expected_sources": ["Customer Acquisition Analysis"],
        "expected_agents": ["DocumentAgent", "DataExtractionAgent", "AnalysisAgent"],
        "ground_truth": "Churn rate should be stated with comparison to industry benchmarks and net retention.",
        "eval_criteria": {
            "has_churn_rate": True,
            "has_benchmark_comparison": True,
            "has_retention_metric": True,
        }
    },
    {
        "id": "ops_004",
        "question": "What is the technology stack?",
        "category": "operational",
        "project_name": "Tech Venture AI - Due Diligence",
        "difficulty": "easy",
        "expected_answer_contains": ["technology", "stack", "platform"],
        "expected_sources": ["IT Infrastructure Overview"],
        "expected_agents": ["DocumentAgent"],
        "ground_truth": "Tech stack should list major technologies, infrastructure, and hosting.",
        "eval_criteria": {
            "lists_technologies": True,
            "mentions_infrastructure": True,
            "mentions_cloud_provider": False,  # Optional
        }
    },
    {
        "id": "ops_005",
        "question": "How scalable is the infrastructure?",
        "category": "operational",
        "project_name": "Tech Venture AI - Due Diligence",
        "difficulty": "hard",
        "expected_answer_contains": ["scalable", "capacity", "infrastructure"],
        "expected_sources": ["IT Infrastructure Overview"],
        "expected_agents": ["DocumentAgent", "AnalysisAgent"],
        "ground_truth": "Scalability assessment should include current capacity, growth potential, and performance metrics.",
        "eval_criteria": {
            "mentions_capacity": True,
            "has_growth_multiple": True,
            "has_performance_metrics": True,
        }
    },
    
    # ===================================================================
    # STRATEGIC QUESTIONS
    # ===================================================================
    {
        "id": "strat_001",
        "question": "What are the growth opportunities?",
        "category": "strategic",
        "project_name": "Tech Venture AI - Due Diligence",
        "difficulty": "medium",
        "expected_answer_contains": ["growth", "opportunity", "expansion"],
        "expected_sources": ["Market Analysis Report", "Product Roadmap"],
        "expected_agents": ["DocumentAgent", "AnalysisAgent"],
        "ground_truth": "Growth opportunities should list key areas with revenue potential and timeframes.",
        "eval_criteria": {
            "lists_opportunities": True,
            "has_revenue_impact": False,  # Optional
            "has_timeframe": False,  # Optional
        }
    },
    {
        "id": "strat_002",
        "question": "Who are the main competitors?",
        "category": "strategic",
        "project_name": "Tech Venture AI - Due Diligence",
        "difficulty": "easy",
        "expected_answer_contains": ["competitor", "competitive"],
        "expected_sources": ["Competitive Landscape", "Market Analysis Report"],
        "expected_agents": ["DocumentAgent", "AnalysisAgent"],
        "ground_truth": "Competitors should be listed with differentiation factors.",
        "eval_criteria": {
            "lists_competitors": True,
            "mentions_differentiation": True,
        }
    },
    {
        "id": "strat_003",
        "question": "What are the key risks?",
        "category": "strategic",
        "project_name": "Tech Venture AI - Due Diligence",
        "difficulty": "medium",
        "expected_answer_contains": ["risk", "challenge"],
        "expected_sources": ["Market Analysis Report"],
        "expected_agents": ["DocumentAgent", "AnalysisAgent"],
        "ground_truth": "Key risks should be identified with mitigation strategies.",
        "eval_criteria": {
            "lists_risks": True,
            "mentions_mitigation": False,  # Optional
        }
    },
    {
        "id": "strat_004",
        "question": "What is the market size?",
        "category": "strategic",
        "project_name": "Tech Venture AI - Due Diligence",
        "difficulty": "medium",
        "expected_answer_contains": ["market", "TAM", "SAM", "billion"],
        "expected_sources": ["Market Analysis Report"],
        "expected_agents": ["DocumentAgent", "DataExtractionAgent"],
        "ground_truth": "Market size should include TAM, SAM, and current market share.",
        "eval_criteria": {
            "has_tam": True,
            "has_sam": True,
            "has_market_share": True,
        }
    },
    {
        "id": "strat_005",
        "question": "What is the management team's experience?",
        "category": "strategic",
        "project_name": "Tech Venture AI - Due Diligence",
        "difficulty": "easy",
        "expected_answer_contains": ["management", "team", "experience", "CEO", "CFO"],
        "expected_sources": ["Key Employee Bios", "Organizational Chart"],
        "expected_agents": ["DocumentAgent", "AnalysisAgent"],
        "ground_truth": "Management experience should highlight key executives and their backgrounds.",
        "eval_criteria": {
            "mentions_executives": True,
            "has_experience_details": True,
        }
    },
    
    # ===================================================================
    # CROSS-FUNCTIONAL QUESTIONS (More Complex)
    # ===================================================================
    {
        "id": "cross_001",
        "question": "Summarize the financial health of the company",
        "category": "summary",
        "project_name": "Tech Venture AI - Due Diligence",
        "difficulty": "hard",
        "expected_answer_contains": ["revenue", "profit", "cash", "debt", "financial"],
        "expected_sources": ["Annual Financial Statements", "Cash Flow Analysis", "EBITDA Analysis"],
        "expected_agents": ["DocumentAgent", "AnalysisAgent", "DataExtractionAgent", "FactCheckAgent"],
        "ground_truth": "Financial health summary should cover revenue, profitability, cash position, and debt.",
        "eval_criteria": {
            "covers_revenue": True,
            "covers_profitability": True,
            "covers_cash": True,
            "covers_debt": True,
            "synthesizes_info": True,
        }
    },
    {
        "id": "cross_002",
        "question": "What are the biggest concerns in this due diligence?",
        "category": "summary",
        "project_name": "Tech Venture AI - Due Diligence",
        "difficulty": "hard",
        "expected_answer_contains": ["risk", "concern", "issue"],
        "expected_sources": [],  # Should pull from multiple docs
        "expected_agents": ["DocumentAgent", "AnalysisAgent", "FactCheckAgent"],
        "ground_truth": "Key concerns should synthesize risks across financial, legal, operational areas.",
        "eval_criteria": {
            "identifies_multiple_concerns": True,
            "covers_different_areas": True,
            "provides_context": True,
        }
    },
    {
        "id": "cross_003",
        "question": "Compare the customer metrics to industry benchmarks",
        "category": "comparison",
        "project_name": "Tech Venture AI - Due Diligence",
        "difficulty": "hard",
        "expected_answer_contains": ["CAC", "churn", "benchmark", "industry", "comparison"],
        "expected_sources": ["Customer Acquisition Analysis"],
        "expected_agents": ["DocumentAgent", "AnalysisAgent", "DataExtractionAgent"],
        "ground_truth": "Comparison should show how company metrics stack up against industry standards.",
        "eval_criteria": {
            "has_company_metrics": True,
            "has_benchmarks": True,
            "makes_comparison": True,
        }
    },
    {
        "id": "cross_004",
        "question": "Is this a good investment opportunity?",
        "category": "analysis",
        "project_name": "Tech Venture AI - Due Diligence",
        "difficulty": "very_hard",
        "expected_answer_contains": ["investment", "opportunity", "growth", "risk"],
        "expected_sources": [],  # Should synthesize from many sources
        "expected_agents": ["DocumentAgent", "AnalysisAgent", "FactCheckAgent"],
        "ground_truth": "Investment assessment should weigh positives (growth, market) against negatives (risks, challenges).",
        "eval_criteria": {
            "discusses_positives": True,
            "discusses_negatives": True,
            "provides_balanced_view": True,
            "uses_evidence": True,
        }
    },
]

# Additional test cases for other projects
def generate_multi_project_tests():
    """Generate test cases across all projects"""
    data = load_generated_data()
    
    additional_tests = []
    
    # Project-specific questions based on industry
    project_templates = {
        "Tech Venture AI": {
            "financial": [
                "What is Tech Venture AI's revenue?",
                "What is Tech Venture AI's profit margin?",
                "What are Tech Venture AI's operating expenses?",
            ],
            "operational": [
                "How many employees does Tech Venture AI have?",
                "What is Tech Venture AI's customer acquisition cost?",
                "What is Tech Venture AI's technology infrastructure?",
            ],
            "strategic": [
                "Who are Tech Venture AI's main competitors?",
                "What is Tech Venture AI's market position?",
            ],
        },
        "GreenEnergy Solutions": {
            "financial": [
                "What is GreenEnergy Solutions's revenue?",
                "What is GreenEnergy Solutions's gross margin?",
                "What are GreenEnergy Solutions's capital expenditures?",
            ],
            "operational": [
                "How many employees does GreenEnergy Solutions have?",
                "What are GreenEnergy Solutions's production facilities?",
                "What is GreenEnergy Solutions's energy generation capacity?",
            ],
            "strategic": [
                "What is GreenEnergy Solutions's regulatory compliance status?",
                "What are GreenEnergy Solutions's growth opportunities?",
            ],
        },
        "FinanceHub Inc": {
            "financial": [
                "What is FinanceHub Inc's revenue?",
                "What is FinanceHub Inc's net income?",
                "What are FinanceHub Inc's primary revenue streams?",
            ],
            "operational": [
                "How many employees does FinanceHub Inc have?",
                "How many customers does FinanceHub Inc have?",
                "What is FinanceHub Inc's customer retention rate?",
            ],
            "strategic": [
                "What is FinanceHub Inc's competitive advantage?",
                "What are FinanceHub Inc's regulatory risks?",
            ],
        },
        "HealthTech Innovations": {
            "financial": [
                "What is HealthTech Innovations's revenue?",
                "What is HealthTech Innovations's R&D spending?",
                "What is HealthTech Innovations's operating cash flow?",
            ],
            "operational": [
                "How many employees does HealthTech Innovations have?",
                "What products does HealthTech Innovations offer?",
                "What regulatory approvals does HealthTech Innovations have?",
            ],
            "strategic": [
                "What is HealthTech Innovations's FDA approval status?",
                "What is HealthTech Innovations's clinical trial pipeline?",
            ],
        },
        "RetailNext Corp": {
            "financial": [
                "What is RetailNext Corp's revenue?",
                "What is RetailNext Corp's inventory turnover?",
                "What are RetailNext Corp's largest expenses?",
            ],
            "operational": [
                "How many employees does RetailNext Corp have?",
                "What is RetailNext Corp's warehouse capacity?",
                "What is RetailNext Corp's supply chain efficiency?",
            ],
            "strategic": [
                "What is RetailNext Corp's e-commerce market share?",
                "What are RetailNext Corp's logistics partnerships?",
            ],
        },
    }
    
    # Company name mapping (to handle space/no-space mismatches)
    company_map = {
        "TechVenture AI": "Tech Venture AI",
        "GreenEnergy Solutions": "GreenEnergy Solutions",
        "FinanceHub Inc": "FinanceHub Inc",
        "HealthTech Innovations": "HealthTech Innovations",
        "RetailNext Corp": "RetailNext Corp",
    }
    
    for idx, project_data in enumerate(data[:5], 1):  # All 5 projects
        project_name = project_data['project']['name']
        company = project_data['project']['company']
        
        # Map company name if needed
        mapped_company = company_map.get(company, company)
        
        # Get templates for this company
        templates = project_templates.get(mapped_company, {})
        
        # Add questions from templates
        question_num = 1
        for category, questions in templates.items():
            for question in questions:
                additional_tests.append({
                    "id": f"multi_{idx}_{category}_{question_num:02d}",
                    "question": question,
                    "category": category,
                    "project_name": project_name,
                    "difficulty": "medium",
                    "expected_answer_contains": ["revenue", "company", "financial"],  # More flexible terms
                    "expected_sources": ["project_{}_doc".format(idx)],
                    "expected_agents": ["DocumentAgent", "DataExtractionAgent"],
                    "ground_truth": f"{question} - answer should be found in {company}'s documents.",
                    "eval_criteria": {
                        "has_relevant_info": True,
                        "cites_sources": True,
                    }
                })
                question_num += 1
    
    return additional_tests

# Combine all test cases
def get_all_test_cases():
    """Get complete evaluation dataset"""
    return EVAL_DATASET + generate_multi_project_tests()

# Statistics
def get_dataset_stats():
    """Get dataset statistics"""
    all_tests = get_all_test_cases()
    
    by_category = {}
    by_difficulty = {}
    
    for test in all_tests:
        cat = test['category']
        diff = test['difficulty']
        
        by_category[cat] = by_category.get(cat, 0) + 1
        by_difficulty[diff] = by_difficulty.get(diff, 0) + 1
    
    return {
        "total": len(all_tests),
        "by_category": by_category,
        "by_difficulty": by_difficulty,
    }

if __name__ == "__main__":
    stats = get_dataset_stats()
    print(f"📊 Evaluation Dataset Statistics:")
    print(f"   Total test cases: {stats['total']}")
    print(f"\n   By category:")
    for cat, count in stats['by_category'].items():
        print(f"     {cat:15} {count:3} tests")
    print(f"\n   By difficulty:")
    for diff, count in stats['by_difficulty'].items():
        print(f"     {diff:15} {count:3} tests")

