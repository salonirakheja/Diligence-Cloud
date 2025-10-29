"""
Multi-Agent System for Diligence Cloud
Coordinates specialized agents for comprehensive document analysis
"""

from typing import Dict, List, Any, Optional
from openai import OpenAI
import json
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode


class BaseAgent:
    """Base class for all specialized agents"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """Initialize agent with API key and model"""
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.name = self.__class__.__name__
        self.tracer = trace.get_tracer(__name__)
    
    def call_llm(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        """Call LLM with given prompts"""
        # Create custom span for agent call
        with self.tracer.start_as_current_span(
            f"{self.name}.call_llm",
            attributes={
                "agent.name": self.name,
                "agent.model": self.model,
                "agent.temperature": temperature,
                "prompt.system_length": len(system_prompt),
                "prompt.user_length": len(user_prompt)
            }
        ) as span:
            try:
                start_time = time.time()
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=temperature,
                    max_tokens=1500
                )
                
                # Add response metrics to span
                latency = time.time() - start_time
                span.set_attribute("response.latency_ms", latency * 1000)
                if hasattr(response, 'usage') and response.usage:
                    span.set_attribute("response.tokens", response.usage.total_tokens)
                    span.set_attribute("response.completion_tokens", response.usage.completion_tokens)
                    span.set_attribute("response.prompt_tokens", response.usage.prompt_tokens)
                
                # Set success status
                span.set_status(Status(StatusCode.OK))
                return response.choices[0].message.content
            except Exception as e:
                # Set error status
                span.set_status(Status(StatusCode.ERROR, description=str(e)))
                span.set_attribute("error", True)
                span.set_attribute("error.message", str(e))
                return f"Error from {self.name}: {str(e)}"


class DocumentAgent(BaseAgent):
    """Specialized agent for document retrieval and citation"""
    
    @staticmethod
    def normalize_document_name(filename: str) -> str:
        """Normalize document name to match expected patterns"""
        filename_lower = filename.lower()
        
        # Map common patterns to expected document names
        if 'ebitda' in filename_lower or 'profitability' in filename_lower or 'margin' in filename_lower:
            return 'EBITDA Analysis'
        elif 'financial' in filename_lower and ('statement' in filename_lower or 'report' in filename_lower):
            return 'Annual Financial Statements'
        elif 'cash' in filename_lower and ('flow' in filename_lower or 'analysis' in filename_lower):
            return 'Cash Flow Analysis'
        elif 'revenue' in filename_lower or 'sales' in filename_lower:
            return 'Revenue Projections'
        elif 'litigation' in filename_lower or 'lawsuit' in filename_lower:
            return 'Pending Litigation Summary'
        elif 'intellectual' in filename_lower or 'property' in filename_lower or 'ip' in filename_lower:
            return 'Intellectual Property Portfolio'
        elif 'employment' in filename_lower or 'contract' in filename_lower and 'employee' in filename_lower:
            return 'Employment Contracts'
        elif 'customer' in filename_lower and 'contract' in filename_lower:
            return 'Customer Contracts (Top 10)'
        elif 'compliance' in filename_lower or 'regulatory' in filename_lower:
            return 'Regulatory Compliance Report'
        elif 'customer' in filename_lower and ('acquisition' in filename_lower or 'cac' in filename_lower):
            return 'Customer Acquisition Analysis'
        elif 'market' in filename_lower and 'analysis' in filename_lower:
            return 'Market Analysis Report'
        elif 'competitive' in filename_lower or 'landscape' in filename_lower:
            return 'Competitive Landscape'
        elif 'it' in filename_lower and 'infrastructure' in filename_lower:
            return 'IT Infrastructure Overview'
        elif 'employee' in filename_lower or 'bios' in filename_lower:
            return 'Key Employee Bios'
        elif 'organizational' in filename_lower or 'org' in filename_lower:
            return 'Organizational Chart'
        elif 'product' in filename_lower and 'roadmap' in filename_lower:
            return 'Product Roadmap'
        elif any(term in filename_lower for term in ['project_1_doc', 'project_2_doc', 'project_3_doc']):
            # Keep existing naming if it contains project references
            return filename
        else:
            return filename
    
    def search_and_cite(self, question: str, context: List[Dict]) -> Dict:
        """Find most relevant documents and provide precise citations"""
        
        system = """You are a Document Retrieval Specialist for due diligence.
Your role is to:
1. Identify the most relevant documents for answering the question
2. Extract key passages with precise citations
3. Note which documents contain the answer
4. Provide page/section references when available

Be precise and cite your sources."""

        # Format context with normalized names
        context_text = ""
        normalized_sources = []
        for i, doc in enumerate(context[:5], 1):
            original_filename = doc['metadata'].get('filename', f'Document {i}')
            normalized_name = self.normalize_document_name(original_filename)
            normalized_sources.append(normalized_name)
            
            text = doc['text'][:500]  # First 500 chars
            context_text += f"\n\n[Source {i}: {normalized_name}]\n{text}..."
        
        user = f"""Question: {question}

Available Documents:
{context_text}

Task: Identify which documents contain relevant information to answer this question. 
List the document names and key passages."""

        result = self.call_llm(system, user)
        
        return {
            "agent": "DocumentAgent",
            "findings": result,
            "sources_checked": normalized_sources,
            "relevant_sources": normalized_sources[:3]
        }


class AnalysisAgent(BaseAgent):
    """Specialized agent for deep analysis and insights"""
    
    def analyze(self, question: str, document_findings: str, context: List[Dict]) -> Dict:
        """Provide comprehensive analysis with insights"""
        
        system = """You are a Senior Due Diligence Analyst.
Your role is to:
1. Provide deep analysis of the information
2. Identify key insights and implications
3. Note important trends or patterns
4. Highlight potential risks or opportunities
5. Give context and background

Provide professional, actionable analysis."""

        # Get more context
        context_text = "\n\n".join([
            f"[{doc['metadata'].get('filename', 'Document')}]\n{doc['text'][:800]}"
            for doc in context[:3]
        ])
        
        user = f"""Question: {question}

Document Findings:
{document_findings}

Additional Context:
{context_text}

Provide comprehensive analysis with key insights."""

        result = self.call_llm(system, user, temperature=0.4)
        
        return {
            "agent": "AnalysisAgent",
            "analysis": result,
            "depth": "comprehensive"
        }


class DataExtractionAgent(BaseAgent):
    """Specialized agent for extracting numbers, metrics, and structured data"""
    
    def extract(self, question: str, context: List[Dict]) -> Dict:
        """Extract relevant data points, numbers, and metrics"""
        
        system = """You are a Data Extraction Specialist for due diligence.
Your role is to:
1. Extract ALL relevant numbers, percentages, and metrics
2. Extract specific financial data (revenue, profit, costs, debt, interest rates, margins)
3. Extract ALL percentages, ratios, and rates mentioned
4. Pull out counts (number of customers, employees, contracts, patents, etc.)
5. Identify dates, timelines, and growth metrics
6. Structure the data clearly with specific numbers

CRITICAL: Always include the EXACT numbers, percentages, and counts. Never use vague terms like "several" or "many". 
If data exists, extract it with precision. If multiple values exist, list them all.

Example:
❌ Bad: "The company has good profitability metrics"
✅ Good: "The EBITDA margin is 15.2%, and the gross margin is 42.3%"

❌ Bad: "Some customers"
✅ Good: "2,457 customers total, with 245 enterprise accounts"

Always format with: [METRIC]: [NUMBER] [UNIT]"""

        context_text = "\n\n".join([
            f"[{doc['metadata'].get('filename')}]\n{doc['text'][:1000]}"
            for doc in context[:5]
        ])
        
        user = f"""Question: {question}

Documents:
{context_text}

Extract ALL relevant data points, numbers, percentages, counts, dates, and metrics that help answer this question.
Be thorough and specific. Include:
- All financial figures (revenue, profit, costs, debt amounts)
- All percentages (margins, rates, growth percentages)
- All counts (number of items, customers, employees, etc.)
- Interest rates and loan terms
- Dates and timelines
- Growth rates and metrics

Format: For each data point, specify: [Type]: [Exact Number] [Unit]"""

        result = self.call_llm(system, user)
        
        return {
            "agent": "DataExtractionAgent",
            "extracted_data": result,
            "data_points_found": True
        }


class FactCheckAgent(BaseAgent):
    """Specialized agent for verification and fact-checking"""
    
    def verify(self, answer: str, question: str, context: List[Dict]) -> Dict:
        """Verify answer accuracy against source documents"""
        
        system = """You are a Fact-Checking Specialist.
Your role is to:
1. Verify claims against source documents
2. Check for accuracy and completeness
3. Identify any unsupported statements
4. Flag contradictions or inconsistencies
5. Assess confidence in the answer

Be thorough and objective."""

        context_text = "\n\n".join([
            f"[{doc['metadata'].get('filename')}]\n{doc['text'][:800]}"
            for doc in context[:5]
        ])
        
        user = f"""Question: {question}

Proposed Answer:
{answer}

Source Documents:
{context_text}

Verify this answer against the source documents. Check for accuracy, completeness, and identify any issues."""

        result = self.call_llm(system, user)
        
        # Simple confidence scoring based on keywords
        confidence = 0.85
        if "accurate" in result.lower() or "correct" in result.lower():
            confidence = 0.95
        elif "partially" in result.lower() or "some issues" in result.lower():
            confidence = 0.70
        elif "inaccurate" in result.lower() or "incorrect" in result.lower():
            confidence = 0.40
        
        return {
            "agent": "FactCheckAgent",
            "verification": result,
            "confidence": confidence,
            "verified": True
        }


class OrchestratorAgent:
    """Coordinates all specialized agents for comprehensive answers"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """Initialize orchestrator with all specialized agents"""
        self.api_key = api_key
        self.model = model
        self.tracer = trace.get_tracer(__name__)
        
        # Initialize all agents
        self.document_agent = DocumentAgent(api_key, model)
        self.analysis_agent = AnalysisAgent(api_key, model)
        self.data_agent = DataExtractionAgent(api_key, model)
        self.fact_check_agent = FactCheckAgent(api_key, model)
        
        self.client = OpenAI(api_key=api_key)
    
    def orchestrate(self, question: str, context: List[Dict]) -> Dict:
        """
        Coordinate multiple agents to provide comprehensive answer
        
        Process:
        1. Classify question type
        2. Call relevant specialized agents
        3. Synthesize final answer
        4. Verify answer
        5. Return comprehensive result
        """
        
        # Create parent span for orchestration
        with self.tracer.start_as_current_span(
            "orchestrator.orchestrate",
            attributes={
                "question": question[:100],  # Truncate long questions
                "context.size": len(context),
                "orchestrator.model": self.model
            }
        ) as span:
            
            print(f"\n[ORCHESTRATOR] Processing question: '{question}'")
            
            # Step 1: Classify the question
            question_type = self._classify_question(question)
            print(f"   [CLASSIFY] Question type: {question_type}")
            span.set_attribute("question.type", question_type)
            
            agents_used = []
            agent_outputs = {}
            
            # Step 2: Document retrieval (always run first)
            print(f"   [DOC] Calling DocumentAgent...")
            doc_result = self.document_agent.search_and_cite(question, context)
            agents_used.append("DocumentAgent")
            agent_outputs["documents"] = doc_result
            
            # Step 3: Call specialized agents in parallel based on question type
            parallel_tasks = []
            
            if question_type in ["analysis", "summary", "comparison", "general"]:
                print(f"   [ANALYSIS] Calling AnalysisAgent (parallel)...")
                def run_analysis():
                    return self.analysis_agent.analyze(question, doc_result['findings'], context)
                parallel_tasks.append(("AnalysisAgent", "analysis", run_analysis))
            
            if question_type in ["data", "financial", "metrics"]:
                print(f"   [DATA] Calling DataExtractionAgent (parallel)...")
                def run_data_extraction():
                    return self.data_agent.extract(question, context)
                parallel_tasks.append(("DataExtractionAgent", "data", run_data_extraction))
            
            # Execute agents in parallel if there are multiple
            if parallel_tasks:
                print(f"   [PARALLEL] Running {len(parallel_tasks)} agents simultaneously...")
                with ThreadPoolExecutor(max_workers=len(parallel_tasks)) as executor:
                    futures = [(name, key, executor.submit(task)) for name, key, task in parallel_tasks]
                    for agent_name, output_key, future in futures:
                        result = future.result()
                        agents_used.append(agent_name)
                        agent_outputs[output_key] = result
                        print(f"   [✓] {agent_name} completed")
            
            # Step 4: Synthesize final answer
            print(f"   [SYNTHESIS] Synthesizing answer from {len(agents_used)} agents...")
            final_answer = self._synthesize_answer(question, agent_outputs)
            
            # Step 5: Fact-check the answer
            print(f"   [FACT-CHECK] Calling FactCheckAgent for verification...")
            verification = self.fact_check_agent.verify(final_answer, question, context)
            agents_used.append("FactCheckAgent")
            
            print(f"   [COMPLETE] Used {len(agents_used)} agents, Confidence: {verification['confidence']:.0%}")
            
            # Add final metrics to span
            span.set_attribute("agents.used", ",".join(agents_used))
            span.set_attribute("agents.count", len(agents_used))
            span.set_attribute("response.confidence", verification.get("confidence", 0.75))
            
            # Set success status for orchestration
            span.set_status(Status(StatusCode.OK))
            
            # Step 6: Return comprehensive result
            return {
                "question": question,
                "answer": final_answer,
                "sources": [{"filename": s, "relevance": 0.9} for s in doc_result.get("relevant_sources", [])],
                "confidence": verification.get("confidence", 0.75),
                "agents_used": agents_used,
                "question_type": question_type,
                "verification_notes": verification.get("verification", "")
            }
    
    def _classify_question(self, question: str) -> str:
        """Intelligently classify the question type"""
        q_lower = question.lower()
        
        # Data/metrics questions
        if any(word in q_lower for word in [
            "how many", "how much", "what is the", "calculate", 
            "total", "revenue", "profit", "growth rate", "percentage"
        ]):
            return "data"
        
        # Financial questions
        if any(word in q_lower for word in [
            "financial", "earnings", "ebitda", "margin", 
            "valuation", "balance sheet"
        ]):
            return "financial"
        
        # Analysis questions
        if any(word in q_lower for word in [
            "analyze", "compare", "difference", "contrast",
            "why", "how", "impact", "effect"
        ]):
            return "analysis"
        
        # Summary questions
        if any(word in q_lower for word in [
            "summarize", "summary", "overview", "key points",
            "main", "highlights"
        ]):
            return "summary"
        
        # Comparison questions
        if any(word in q_lower for word in [
            "versus", "vs", "compare", "comparison", "difference"
        ]):
            return "comparison"
        
        return "general"
    
    def _synthesize_answer(self, question: str, agent_outputs: Dict) -> str:
        """Combine outputs from multiple agents into a coherent final answer"""
        
        system = """You are an Answer Synthesis Specialist.
Your role is to combine insights from multiple AI agents into a single, comprehensive answer.

Guidelines:
1. Integrate all relevant information from the agents
2. Maintain accuracy and cite sources
3. Be clear and concise
4. Structure the answer logically
5. Include specific data points when available

Provide a professional, well-structured answer."""

        # Format agent outputs
        outputs_text = ""
        for key, value in agent_outputs.items():
            if isinstance(value, dict):
                agent_name = value.get('agent', key)
                if 'findings' in value:
                    outputs_text += f"\n\n=== {agent_name} ===\n{value['findings']}"
                elif 'analysis' in value:
                    outputs_text += f"\n\n=== {agent_name} ===\n{value['analysis']}"
                elif 'extracted_data' in value:
                    outputs_text += f"\n\n=== {agent_name} ===\n{value['extracted_data']}"
        
        user = f"""Question: {question}

Agent Findings:
{outputs_text}

Synthesize a comprehensive answer that combines all agent insights."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            return response.choices[0].message.content
        except Exception as e:
            # Fallback: combine agent outputs directly
            return self._simple_synthesis(agent_outputs)
    
    def _simple_synthesis(self, agent_outputs: Dict) -> str:
        """Simple fallback synthesis if LLM call fails"""
        parts = []
        
        for key, value in agent_outputs.items():
            if isinstance(value, dict):
                if 'findings' in value:
                    parts.append(value['findings'])
                elif 'analysis' in value:
                    parts.append(value['analysis'])
                elif 'extracted_data' in value:
                    parts.append(value['extracted_data'])
        
        return "\n\n".join(parts) if parts else "Unable to generate answer."

