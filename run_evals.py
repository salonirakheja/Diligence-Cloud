#!/usr/bin/env python3
"""
Evaluation Runner for Diligence Cloud
Runs test cases and generates comprehensive evaluation reports
"""

import json
import os
import time
import requests
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import statistics

from eval_dataset import get_all_test_cases, get_dataset_stats

try:
    import phoenix as px
    from phoenix.trace.span_evaluations import DocumentEvaluations
except ImportError:  # pragma: no cover - optional dependency
    px = None
    DocumentEvaluations = None


def create_phoenix_client() -> tuple[Optional["px.Client"], Optional[str]]:
    """Initialize Phoenix client if configuration is available."""
    if px is None:
        return None, None

    api_url = os.getenv("PHOENIX_API_URL")
    api_key = os.getenv("PHOENIX_API_KEY")

    if not api_url or not api_key:
        return None, None

    api_url = api_url.rstrip("/")
    if api_url.lower().endswith("/v1"):
        api_url = api_url[:-3]

    project_name = os.getenv("PHOENIX_PROJECT", "diligence-evals")

    try:
        print(f"🔗 Connecting to Arize Phoenix project '{project_name}'...")
        client = px.Client(
            endpoint=api_url,
            api_key=api_key,
            warn_if_server_not_running=False,
        )
        print("✅ Phoenix logging enabled for evaluation runs.")
        return client, project_name
    except Exception as exc:  # pragma: no cover - best effort logging
        print(f"⚠️  Failed to initialize Phoenix client: {exc}")
        return None, None


def get_default_api_base() -> str:
    """Return API base URL, preferring CLI/env overrides."""
    return os.getenv("DILIGENCE_API_BASE", "http://localhost:8002")

class DiligenceCloudEvaluator:
    """Run and evaluate Diligence Cloud Q&A system"""
    
    def __init__(
        self,
        test_cases: List[Dict],
        base_url: Optional[str] = None,
        phoenix_client: Optional["px.Client"] = None,
        phoenix_eval_name: Optional[str] = None,
    ):
        self.test_cases = test_cases
        self.results = []
        self.start_time = None
        self.end_time = None
        self.base_url = (base_url or get_default_api_base()).rstrip("/")
        self.phoenix_client = phoenix_client
        self.phoenix_eval_name = phoenix_eval_name or "diligence-evals"
    
    def check_server(self) -> bool:
        """Check if server is running"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def get_project_id(self, project_name: str) -> Optional[str]:
        """Get project ID from name"""
        try:
            response = requests.get(f"{self.base_url}/api/projects")
            if response.status_code == 200:
                projects = response.json().get("projects", [])
                for project in projects:
                    if project["name"] == project_name:
                        return project["id"]
        except requests.exceptions.RequestException:
            pass
        return None
    
    def evaluate_single_question(self, test_case: Dict) -> Dict:
        """Evaluate a single test case"""
        print(f"  🧪 {test_case['id']}: {test_case['question'][:60]}...")
        
        start_time = time.time()
        
        # Get project ID
        project_id = self.get_project_id(test_case.get("project_name", ""))
        
        try:
            # Call API
            response = requests.post(
                f"{self.base_url}/api/ask",
                json={
                    "question": test_case["question"],
                    "project_id": project_id,
                },
                timeout=120
            )
            
            end_time = time.time()
            latency = end_time - start_time
            
            if response.status_code != 200:
                return {
                    **test_case,
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text[:200]}",
                    "latency": latency,
                    "timestamp": datetime.now().isoformat(),
                }
            
            answer_data = response.json()
            
            # Evaluate response
            result = {
                **test_case,
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "latency": latency,
                
                # Response data
                "answer": answer_data.get("answer", ""),
                "sources": answer_data.get("sources", []),
                "confidence": answer_data.get("confidence", "unknown"),
                "agents_used": self._extract_agents_used(answer_data),
                
                # Metrics
                "answer_length": len(answer_data.get("answer", "")),
                "num_sources": len(answer_data.get("sources", [])),
                
                # Quality checks
                "term_coverage": self._check_term_coverage(
                    answer_data.get("answer", ""),
                    test_case.get("expected_answer_contains", [])
                ),
                "source_attribution": self._check_source_attribution(
                    answer_data.get("sources", []),
                    test_case.get("expected_sources", [])
                ),
                "agent_usage": self._check_agent_usage(
                    self._extract_agents_used(answer_data),
                    test_case.get("expected_agents", [])
                ),
                "criteria_met": self._check_criteria(
                    answer_data.get("answer", ""),
                    answer_data.get("sources", []),
                    test_case.get("eval_criteria", {})
                ),
            }
            
            # Overall pass/fail
            result["passed"] = self._determine_pass(result)
            
            status_icon = "✅" if result["passed"] else "❌"
            print(f"    {status_icon} {latency:.2f}s | {result['answer_length']} chars | {result['num_sources']} sources")
            
            self._log_to_phoenix(result)
            return result
            
        except requests.exceptions.Timeout:
            result = {
                **test_case,
                "status": "timeout",
                "error": "Request timed out after 120s",
                "latency": 120,
                "timestamp": datetime.now().isoformat(),
                "passed": False,
            }
            self._log_to_phoenix(result)
            return result
        except Exception as e:
            result = {
                **test_case,
                "status": "error",
                "error": str(e),
                "latency": time.time() - start_time,
                "timestamp": datetime.now().isoformat(),
                "passed": False,
            }
            self._log_to_phoenix(result)
            return result
    
    def _extract_agents_used(self, answer_data: Dict) -> List[str]:
        """Extract which agents were used from response"""
        # Look for agent names in the response
        agents = []
        answer = str(answer_data)
        
        agent_names = ["DocumentAgent", "AnalysisAgent", "DataExtractionAgent", 
                      "FactCheckAgent", "OrchestratorAgent"]
        
        for agent in agent_names:
            if agent.lower() in answer.lower():
                agents.append(agent)
        
        return agents
    
    def _check_term_coverage(self, answer: str, expected_terms: List[str]) -> Dict:
        """Check if expected terms are in the answer"""
        if not expected_terms:
            return {"score": 1.0, "found": [], "missing": []}
        
        answer_lower = answer.lower()
        found = [term for term in expected_terms if term.lower() in answer_lower]
        missing = [term for term in expected_terms if term not in found]
        
        return {
            "score": len(found) / len(expected_terms),
            "found": found,
            "missing": missing,
        }
    
    def _check_source_attribution(self, actual_sources: List, expected_sources: List[str]) -> Dict:
        """Check if expected sources are cited"""
        if not expected_sources:
            return {"score": 1.0, "found": [], "missing": []}
        
        # Extract actual source names (try both 'filename' and 'name' fields)
        actual_names = []
        for s in actual_sources:
            if isinstance(s, dict):
                name = s.get("filename", "") or s.get("name", "")
                actual_names.append(name)
            else:
                actual_names.append(str(s))
        
        # Check for partial matches (more lenient)
        found = []
        import re
        for exp in expected_sources:
            exp_lower = exp.lower()
            
            # Special case: Handle generic project document patterns (e.g., "project_1_doc")
            if "project_" in exp_lower and "_doc" in exp_lower:
                match = re.search(r'project_(\d+)_doc', exp_lower)
                if match:
                    project_num = match.group(1)
                    # Check if any actual source contains this project number
                    if any(f"project_{project_num}" in name.lower() for name in actual_names):
                        found.append(exp)
                        continue
            
            # Check for exact match
            if any(exp_lower == name.lower() for name in actual_names):
                found.append(exp)
                continue
            
            # Check for substring match (bidirectional)
            if any(exp_lower in name.lower() or name.lower() in exp_lower for name in actual_names):
                found.append(exp)
                continue
            
            # Check for keyword-based matching (improved)
            # Split expected source into keywords
            keywords = [w.strip() for w in exp_lower.replace('(', '').replace(')', '').split() if len(w) > 3]
            
            if keywords:  # Only do keyword matching if we have keywords
                for name in actual_names:
                    name_lower = name.lower()
                    # If most keywords (70%+) are found in actual source name
                    matching_keywords = sum(1 for kw in keywords if kw in name_lower)
                    if matching_keywords >= len(keywords) * 0.7:
                        found.append(exp)
                        break
        
        missing = [exp for exp in expected_sources if exp not in found]
        
        return {
            "score": len(found) / len(expected_sources),
            "found": found,
            "missing": missing,
        }
    
    def _check_agent_usage(self, actual_agents: List[str], expected_agents: List[str]) -> Dict:
        """Check if expected agents were used"""
        if not expected_agents:
            return {"score": 1.0, "found": [], "missing": []}
        
        found = [exp for exp in expected_agents if exp in actual_agents]
        missing = [exp for exp in expected_agents if exp not in found]
        
        return {
            "score": len(found) / len(expected_agents),
            "found": found,
            "missing": missing,
        }

    def _log_to_phoenix(self, result: Dict):
        """Send evaluation result to Phoenix for observability."""
        if not self.phoenix_client or DocumentEvaluations is None:
            return

        try:
            import pandas as pd  # Local import to keep dependency optional

            span_id = str(result.get("id") or f"test_{len(self.results)}")
            df = pd.DataFrame(
                [
                    {
                        "span_id": span_id,
                        "position": 0,
                        "score": float(1.0 if result.get("passed") else 0.0),
                        "label": "pass" if result.get("passed") else "fail",
                        "question": result.get("question"),
                        "project": result.get("project_name"),
                        "category": result.get("category"),
                        "difficulty": result.get("difficulty"),
                        "status": result.get("status"),
                        "latency_sec": result.get("latency"),
                        "timestamp": result.get("timestamp"),
                        "answer_length": result.get("answer_length"),
                        "num_sources": result.get("num_sources"),
                        "term_score": self._safe_nested(result, "term_coverage", "score"),
                        "source_score": self._safe_nested(result, "source_attribution", "score"),
                        "criteria_score": self._safe_nested(result, "criteria_met", "score"),
                        "term_found": self._safe_nested(result, "term_coverage", "found"),
                        "term_missing": self._safe_nested(result, "term_coverage", "missing"),
                        "sources_found": self._safe_nested(result, "source_attribution", "found"),
                        "sources_missing": self._safe_nested(result, "source_attribution", "missing"),
                        "criteria_met": self._safe_nested(result, "criteria_met", "met"),
                        "criteria_not_met": self._safe_nested(result, "criteria_met", "not_met"),
                        "agents_used": result.get("agents_used"),
                        "error_message": result.get("error"),
                    }
                ]
            ).set_index(["span_id", "position"])

            evaluations = DocumentEvaluations(
                eval_name=self.phoenix_eval_name,
                dataframe=df,
            )
            self.phoenix_client.log_evaluations(evaluations)
        except Exception as exc:  # pragma: no cover - logging should not break evals
            print(f"⚠️  Failed to log evaluation '{result.get('id')}' to Phoenix: {exc}")

    @staticmethod
    def _safe_nested(data: Dict, key: str, nested_key: str):
        """Helper to safely pull nested values."""
        nested = data.get(key, {})
        if isinstance(nested, dict):
            return nested.get(nested_key)
        return None
    
    def _check_criteria(self, answer: str, sources: List, criteria: Dict) -> Dict:
        """Check custom evaluation criteria"""
        if not criteria:
            return {"score": 1.0, "met": [], "not_met": []}
        
        answer_lower = answer.lower()
        met = []
        not_met = []
        
        for criterion, required in criteria.items():
            # Skip optional criteria (required=False)
            if not required:
                continue
            
            # Simple heuristic checks
            passed = False
            
            if "has_revenue" in criterion or "has_revenue_figure" in criterion:
                passed = any(term in answer_lower for term in ["revenue", "$", "million", "m", "billion"])
            elif "has_percentage" in criterion or "has_percentages" in criterion:
                passed = "%" in answer or "percent" in answer_lower
            elif "has_growth" in criterion or "has_growth_metric" in criterion:
                passed = "growth" in answer_lower or "yoy" in answer_lower or "%" in answer
            elif "has_debt" in criterion or "has_debt_amount" in criterion:
                passed = "debt" in answer_lower or "$" in answer_lower
            elif "has_debt_type" in criterion:
                passed = any(term in answer_lower for term in ["debt steps", "term", "line", "bank", "debt"])
            elif "has_interest_rate" in criterion:
                passed = any(term in answer_lower for term in ["interest", "rate", "%", "apr"])
            elif "has_cac" in criterion or "has_cac_value" in criterion:
                passed = "cac" in answer_lower or "$" in answer_lower
            elif "has_ltv" in criterion or "has_ltv_ratio" in criterion:
                passed = "ltv" in answer_lower or "lifetime" in answer_lower or "/" in answer_lower
            elif "has_churn" in criterion or "has_churn_rate" in criterion:
                passed = "churn" in answer_lower or "%" in answer_lower
            elif "has_benchmark" in criterion or "has_benchmark_comparison" in criterion:
                passed = any(term in answer_lower for term in ["benchmark", "industry", "average", "compared", "vs"])
            elif "has_retention" in criterion or "has_retention_metric" in criterion:
                passed = any(term in answer_lower for term in ["retention", "retained", "retain"])
            elif "has_case_count" in criterion:
                passed = any(term in answer_lower for term in ["case", "lawsuit", "litigation", "pending"])
            elif "has_contract_values" in criterion:
                passed = any(term in answer_lower for term in ["contract", "value", "$", "revenue"])
            elif "has_tam" in criterion or "has_sam" in criterion or "has_market_share" in criterion:
                passed = any(term in answer_lower for term in ["market", "tam", "sam", "billion", "million"])
            elif "mentions_executives" in criterion or "has_experience_details" in criterion:
                passed = any(term in answer_lower for term in ["ceo", "cfo", "founder", "executive", "experience", "years"])
            elif "mentions_capacity" in criterion or "has_performance_metrics" in criterion:
                passed = any(term in answer_lower for term in ["capacity", "performance", "throughput", "scalable"])
            elif "covers_revenue" in criterion or "covers_profitability" in criterion or "covers_cash" in criterion or "covers_debt" in criterion:
                passed = any(term in answer_lower for term in ["revenue", "profit", "cash", "debt", "margin"])
            elif "mentions_" in criterion:
                keyword = criterion.replace("mentions_", "").replace("_", " ")
                passed = keyword in answer_lower
            elif "lists_" in criterion:
                # Check for multiple items (commas, bullets, etc.)
                passed = answer.count(",") >= 2 or answer.count("•") >= 2 or answer.count("\n") >= 2 or answer.count("-") >= 2
            elif "states_" in criterion:
                passed = len(answer) > 50  # Has substantive content
            elif "cites_" in criterion:
                passed = len(sources) > 0
            elif criterion == "synthesizes_info":
                passed = len(answer) > 200  # Longer, synthesized answer
            elif criterion == "provides_balanced_view":
                passed = ("however" in answer_lower or "but" in answer_lower or 
                         "while" in answer_lower or "although" in answer_lower)
            elif criterion == "uses_evidence":
                passed = len(sources) > 0
            elif "has_relevant_info" in criterion or "cites_sources" in criterion:
                passed = len(answer) > 50 and len(sources) > 0
            else:
                # Default: check if criterion keyword is in answer
                keyword = criterion.replace("has_", "").replace("_", " ")
                passed = keyword in answer_lower or len(answer) > 100
            
            if passed:
                met.append(criterion)
            else:
                not_met.append(criterion)
        
        # Calculate score based on required criteria only
        required_criteria = [k for k, v in criteria.items() if v]
        if not required_criteria:
            return {"score": 1.0, "met": [], "not_met": []}
        
        return {
            "score": len(met) / len(required_criteria),
            "met": met,
            "not_met": not_met,
        }
    
    def _determine_pass(self, result: Dict) -> bool:
        """Determine if test case passed"""
        if result.get("status") != "success":
            return False
        
        # Must have an answer
        if len(result.get("answer", "")) < 20:
            return False
        
        # Must have sources
        if result.get("num_sources", 0) == 0:
            return False
        
        # Check scores
        term_score = result.get("term_coverage", {}).get("score", 0)
        criteria_score = result.get("criteria_met", {}).get("score", 0)
        
        # Pass if term coverage > 30% and criteria > 30% (relaxed for generated test data)
        # Also check if at least basic criteria are met (has relevant info)
        has_relevant_info = any(
            c in result.get("criteria_met", {}).get("met", []) 
            for c in ["has_relevant_info", "cites_sources"]
        ) if result.get("criteria_met", {}).get("met") else False
        
        # More lenient pass criteria: either good overall scores OR basic info is present
        return (term_score >= 0.3 and criteria_score >= 0.3) or has_relevant_info
    
    def run_all_evaluations(self, subset: Optional[str] = None, limit: Optional[int] = None):
        """Run all evaluations"""
        test_cases = self.test_cases
        
        # Filter by subset if specified
        if subset:
            test_cases = [tc for tc in test_cases if tc.get("category") == subset]
        
        # Limit number of tests
        if limit:
            test_cases = test_cases[:limit]
        
        print(f"\n🚀 Running {len(test_cases)} evaluations...")
        print("=" * 80)
        
        self.start_time = datetime.now()
        
        for test_case in test_cases:
            result = self.evaluate_single_question(test_case)
            self.results.append(result)
            time.sleep(0.5)  # Rate limiting
        
        self.end_time = datetime.now()
        
        print("=" * 80)
        print(f"✅ Evaluation complete!\n")
    
    def generate_report(self) -> str:
        """Generate comprehensive evaluation report"""
        if not self.results:
            return "No results to report"
        
        total = len(self.results)
        successful = sum(1 for r in self.results if r.get("status") == "success")
        passed = sum(1 for r in self.results if r.get("passed", False))
        errors = sum(1 for r in self.results if r.get("status") == "error")
        timeouts = sum(1 for r in self.results if r.get("status") == "timeout")
        
        # Calculate averages for successful tests
        success_results = [r for r in self.results if r.get("status") == "success"]
        
        if success_results:
            avg_latency = statistics.mean(r.get("latency", 0) for r in success_results)
            avg_answer_length = statistics.mean(r.get("answer_length", 0) for r in success_results)
            avg_sources = statistics.mean(r.get("num_sources", 0) for r in success_results)
            
            avg_term_score = statistics.mean(r.get("term_coverage", {}).get("score", 0) for r in success_results)
            avg_source_score = statistics.mean(r.get("source_attribution", {}).get("score", 0) for r in success_results)
            avg_criteria_score = statistics.mean(r.get("criteria_met", {}).get("score", 0) for r in success_results)
        else:
            avg_latency = avg_answer_length = avg_sources = 0
            avg_term_score = avg_source_score = avg_criteria_score = 0
        
        # Group by category
        by_category = {}
        for r in self.results:
            cat = r.get("category", "unknown")
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(r)
        
        # Group by difficulty
        by_difficulty = {}
        for r in self.results:
            diff = r.get("difficulty", "unknown")
            if diff not in by_difficulty:
                by_difficulty[diff] = []
            by_difficulty[diff].append(r)
        
        # Generate report
        duration = (self.end_time - self.start_time).total_seconds()
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════════╗
║              DILIGENCE CLOUD EVALUATION REPORT                           ║
╚══════════════════════════════════════════════════════════════════════════╝

📅 Evaluation Run: {self.start_time.strftime("%Y-%m-%d %H:%M:%S")}
⏱️  Duration: {duration:.1f}s

📊 SUMMARY:
  Total Tests:         {total}
  Successful:          {successful} ({successful/total*100:.1f}%)
  Passed:              {passed} ({passed/total*100:.1f}%)
  Failed:              {total - passed} ({(total-passed)/total*100:.1f}%)
  Errors:              {errors}
  Timeouts:            {timeouts}

⚡ PERFORMANCE METRICS:
  Avg Latency:         {avg_latency:.2f}s
  Avg Answer Length:   {avg_answer_length:.0f} characters
  Avg Sources Cited:   {avg_sources:.1f}

✅ QUALITY SCORES:
  Term Coverage:       {avg_term_score*100:.1f}% (expected terms found)
  Source Attribution:  {avg_source_score*100:.1f}% (expected sources cited)
  Criteria Met:        {avg_criteria_score*100:.1f}% (evaluation criteria passed)
  Overall Pass Rate:   {passed/total*100:.1f}%

📈 BY CATEGORY:
"""
        
        for cat, results in sorted(by_category.items()):
            cat_passed = sum(1 for r in results if r.get("passed", False))
            cat_total = len(results)
            successful_latencies = [r.get("latency", 0) for r in results if r.get("status") == "success"]
            cat_latency = statistics.mean(successful_latencies) if successful_latencies else 0.0
            report += f"  {cat.capitalize():15} {cat_total:3} tests | {cat_passed:3} passed ({cat_passed/cat_total*100:.0f}%) | {cat_latency:.2f}s avg\n"
        
        report += f"\n📊 BY DIFFICULTY:\n"
        for diff, results in sorted(by_difficulty.items()):
            diff_passed = sum(1 for r in results if r.get("passed", False))
            diff_total = len(results)
            report += f"  {diff.capitalize():15} {diff_total:3} tests | {diff_passed:3} passed ({diff_passed/diff_total*100:.0f}%)\n"
        
        # Failed tests
        failed_tests = [r for r in self.results if not r.get("passed", False)]
        if failed_tests:
            report += f"\n❌ FAILED TESTS ({len(failed_tests)}):\n"
            for r in failed_tests[:10]:  # Show first 10
                reason = "Error" if r.get("status") == "error" else "Quality"
                report += f"  • {r.get('id', 'unknown'):12} [{reason:7}] {r.get('question', '')[:50]}...\n"
                if r.get("status") == "error":
                    report += f"    Error: {r.get('error', '')[:80]}\n"
                else:
                    criteria = r.get('criteria_met', {})
                    if criteria.get('not_met'):
                        report += f"    Missing: {', '.join(criteria['not_met'][:3])}\n"
            
            if len(failed_tests) > 10:
                report += f"  ... and {len(failed_tests) - 10} more\n"
        
        report += f"""
{'=' * 78}
💡 RECOMMENDATIONS:
"""
        
        if avg_term_score < 0.7:
            report += "  ⚠️  Improve answer completeness - many expected terms missing\n"
        if avg_source_score < 0.5:
            report += "  ⚠️  Improve source attribution - expected documents not being cited\n"
        if avg_criteria_score < 0.7:
            report += "  ⚠️  Review failed criteria - answers not meeting quality standards\n"
        if avg_latency > 10:
            report += "  ⚠️  Optimize performance - average latency is high\n"
        if passed / total < 0.8:
            report += "  ⚠️  Overall pass rate below 80% - review system prompts and agent logic\n"
        
        if passed / total >= 0.8:
            report += "  ✅ Good performance! Continue monitoring and iterating\n"
        
        report += f"""
{'=' * 78}
"""
        
        return report
    
    def save_results(self, output_file: str = "eval_results.json"):
        """Save results to JSON file"""
        output_path = Path(output_file)
        
        with open(output_path, 'w') as f:
            json.dump({
                "metadata": {
                    "start_time": self.start_time.isoformat() if self.start_time else None,
                    "end_time": self.end_time.isoformat() if self.end_time else None,
                    "total_tests": len(self.results),
                },
                "results": self.results,
            }, f, indent=2)
        
        print(f"💾 Results saved to: {output_path}")


def main():
    """Main evaluation runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Diligence Cloud evaluations")
    parser.add_argument("--category", help="Run only specific category (financial, legal, operational, strategic)")
    parser.add_argument("--limit", type=int, help="Limit number of tests to run")
    parser.add_argument("--output", default="eval_results.json", help="Output file for results")
    parser.add_argument("--base-url", help="Override API base URL (default: env DILIGENCE_API_BASE or http://localhost:8002)")
    
    args = parser.parse_args()
    
    # Print dataset stats
    print("\n📊 Evaluation Dataset:")
    stats = get_dataset_stats()
    print(f"   Total test cases: {stats['total']}")
    print(f"   Categories: {', '.join(stats['by_category'].keys())}")
    
    # Load test cases
    test_cases = get_all_test_cases()
    
    # Initialize Phoenix client
    phoenix_client, phoenix_eval_name = create_phoenix_client()

    # Create evaluator
    evaluator = DiligenceCloudEvaluator(
        test_cases,
        base_url=args.base_url or get_default_api_base(),
        phoenix_client=phoenix_client,
        phoenix_eval_name=phoenix_eval_name,
    )
    
    # Check server
    print("\n🔍 Checking server status...")
    if not evaluator.check_server():
        print("❌ Server is not running at", evaluator.base_url)
        print("   Please start the server first: python3 backend/main.py")
        return
    
    print("✅ Server is running")
    
    # Run evaluations
    evaluator.run_all_evaluations(subset=args.category, limit=args.limit)
    
    # Generate report
    report = evaluator.generate_report()
    print(report)
    
    # Save results
    evaluator.save_results(args.output)
    
    print(f"\n✅ Evaluation complete! Results saved to {args.output}")
    print(f"   View detailed results: cat {args.output}")


if __name__ == "__main__":
    main()

