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
from opentelemetry.context import attach, detach, get_current


class BaseAgent:
    """Base class for all specialized agents"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """Initialize agent with API key and model"""
        self.client = OpenAI(api_key=api_key, timeout=120.0)  # 2 minute timeout
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
                    max_tokens=800  # Reduced to encourage concise responses
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
                error_msg = str(e)
                if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                    print(f"   [⚠️] {self.name} timed out")
                    return f"{self.name} request timed out. Please try again or check your network connection."
                return f"Error from {self.name}: {error_msg}"


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
        with self.tracer.start_as_current_span(
            "DocumentAgent.search_and_cite",
            attributes={
                "agent.name": self.name,
                "question": question[:100],
                "context.size": len(context)
            }
        ) as span:
            try:
                system = """You are a Document Retrieval Specialist for due diligence.
Your role is to:
1. Identify ONLY the documents that directly contain information needed to answer the question
2. Extract ONLY the key passages relevant to the question
3. Be precise and cite sources
4. Skip documents that are tangentially related but don't help answer the question

Focus on relevance - only cite documents that directly help answer what was asked."""

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

Task: Identify ONLY the documents that contain information directly needed to answer "{question}".
- Skip documents that are only tangentially related
- Extract ONLY passages that directly help answer the question
- List document names and relevant key passages only"""

                result = self.call_llm(system, user)
                
                span.set_attribute("sources.count", len(normalized_sources))
                span.set_status(Status(StatusCode.OK))
                
                return {
                    "agent": "DocumentAgent",
                    "findings": result,
                    "sources_checked": normalized_sources,
                    "relevant_sources": normalized_sources[:3]  # Top 3 candidates max
                }
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, description=str(e)))
                span.set_attribute("error", True)
                span.set_attribute("error.message", str(e))
                raise


class AnalysisAgent(BaseAgent):
    """Specialized agent for deep analysis and insights"""
    
    def analyze(self, question: str, document_findings: str, context: List[Dict]) -> Dict:
        """Provide comprehensive analysis with insights"""
        with self.tracer.start_as_current_span(
            "AnalysisAgent.analyze",
            attributes={
                "agent.name": self.name,
                "question": question[:100],
                "context.size": len(context)
            }
        ) as span:
            try:
                system = """You are a Senior Due Diligence Analyst.
Your role is to provide focused analysis that directly answers the question.

IMPORTANT: 
- Analyze ONLY what is needed to answer the specific question asked
- Do not include general context or background unless directly relevant to the question
- Keep analysis concise and targeted (2-4 sentences typically)
- Focus on insights that directly address what was asked
- Skip tangential information even if it's interesting"""

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

Provide focused analysis that directly answers: "{question}"
- Analyze ONLY what's needed to answer this specific question
- Skip general background or context unless directly relevant
- Keep it concise (2-4 sentences typically)
- Focus on insights that directly address what was asked"""

                result = self.call_llm(system, user, temperature=0.4)
                
                span.set_attribute("response.length", len(result))
                span.set_status(Status(StatusCode.OK))
                
                return {
                    "agent": "AnalysisAgent",
                    "analysis": result,
                    "depth": "comprehensive"
                }
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, description=str(e)))
                span.set_attribute("error", True)
                span.set_attribute("error.message", str(e))
                raise


class DataExtractionAgent(BaseAgent):
    """Specialized agent for extracting numbers, metrics, and structured data"""
    
    def extract(self, question: str, context: List[Dict]) -> Dict:
        """Extract relevant data points, numbers, and metrics"""
        with self.tracer.start_as_current_span(
            "DataExtractionAgent.extract",
            attributes={
                "agent.name": self.name,
                "question": question[:100],
                "context.size": len(context)
            }
        ) as span:
            try:
                system = """You are a Data Extraction Specialist for due diligence.
Your role is to extract ONLY the numbers, percentages, and metrics that directly answer the question asked.

CRITICAL RULES:
1. Extract ONLY data points relevant to the specific question - skip everything else
2. If the question asks about revenue, extract ONLY revenue numbers (not profit, costs, etc.)
3. If the question asks about a specific metric, extract ONLY that metric
4. Never include tangential data even if it's interesting
5. Always use EXACT numbers - never vague terms like "several" or "many"
6. Format concisely: [METRIC]: [NUMBER] [UNIT]

Example for question "What is the revenue?":
❌ Bad: "Revenue: $15.2M. EBITDA margin: 15.2%. Gross margin: 42.3%. Customer count: 2,457..."
✅ Good: "Annual revenue: $15.2 million (as of Q4 2023)"

Focus on answering ONLY what was asked, nothing more."""

                context_text = "\n\n".join([
                    f"[{doc['metadata'].get('filename')}]\n{doc['text'][:1000]}"
                    for doc in context[:5]
                ])
                
                user = f"""Question: {question}

Documents:
{context_text}

Extract ONLY the specific numbers, percentages, counts, or dates that directly answer: "{question}"

REQUIREMENTS:
- Extract ONLY data directly relevant to answering this question
- If question asks about revenue, extract ONLY revenue (not profit, costs, etc.)
- Be specific with exact numbers
- Skip data that doesn't directly answer the question
- Format: [Metric]: [Exact Number] [Unit]

Example: If question is "What is the revenue?", extract ONLY revenue figures."""

                result = self.call_llm(system, user)
                
                span.set_attribute("response.length", len(result))
                span.set_status(Status(StatusCode.OK))
                
                return {
                    "agent": "DataExtractionAgent",
                    "extracted_data": result,
                    "data_points_found": True
                }
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, description=str(e)))
                span.set_attribute("error", True)
                span.set_attribute("error.message", str(e))
                raise


class FactCheckAgent(BaseAgent):
    """Specialized agent for verification and fact-checking"""
    
    def verify(self, answer: str, question: str, context: List[Dict]) -> Dict:
        """Verify answer accuracy against source documents"""
        with self.tracer.start_as_current_span(
            "FactCheckAgent.verify",
            attributes={
                "agent.name": self.name,
                "question": question[:100],
                "answer.length": len(answer),
                "context.size": len(context)
            }
        ) as span:
            try:
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
                
                span.set_attribute("confidence", confidence)
                span.set_status(Status(StatusCode.OK))
                
                return {
                    "agent": "FactCheckAgent",
                    "verification": result,
                    "confidence": confidence,
                    "verified": True
                }
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, description=str(e)))
                span.set_attribute("error", True)
                span.set_attribute("error.message", str(e))
                raise


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
            
            # Capture current OpenTelemetry context for propagation to worker threads
            current_context = get_current()
            
            def wrap_with_context(task_func):
                """Wrap a task function to restore OpenTelemetry context in worker thread"""
                def wrapped():
                    # Restore the context in the worker thread
                    token = attach(current_context)
                    try:
                        return task_func()
                    finally:
                        detach(token)
                return wrapped
            
            if question_type in ["analysis", "summary", "comparison", "general"]:
                print(f"   [ANALYSIS] Calling AnalysisAgent (parallel)...")
                def run_analysis():
                    return self.analysis_agent.analyze(question, doc_result['findings'], context)
                parallel_tasks.append(("AnalysisAgent", "analysis", wrap_with_context(run_analysis)))
            
            if question_type in ["data", "financial", "metrics"]:
                print(f"   [DATA] Calling DataExtractionAgent (parallel)...")
                def run_data_extraction():
                    return self.data_agent.extract(question, context)
                parallel_tasks.append(("DataExtractionAgent", "data", wrap_with_context(run_data_extraction)))
            
            # Execute agents in parallel if there are multiple
            if parallel_tasks:
                print(f"   [PARALLEL] Running {len(parallel_tasks)} agents simultaneously...")
                with ThreadPoolExecutor(max_workers=len(parallel_tasks)) as executor:
                    futures = [(name, key, executor.submit(task)) for name, key, task in parallel_tasks]
                    for agent_name, output_key, future in futures:
                        try:
                            # Add timeout to prevent hanging (3 minutes per agent)
                            result = future.result(timeout=180)
                            agents_used.append(agent_name)
                            agent_outputs[output_key] = result
                            print(f"   [✓] {agent_name} completed")
                        except Exception as e:
                            print(f"   [✗] {agent_name} failed: {str(e)}")
                            # Continue with other agents even if one fails
                            error_result = {
                                "agent": agent_name,
                                "error": str(e),
                                "extracted_data" if "Data" in agent_name else "analysis": f"Error: {str(e)}"
                            }
                            agent_outputs[output_key] = error_result
            
            # Step 4: Filter agent outputs for relevance before synthesis
            print(f"   [FILTER] Filtering agent outputs for question relevance...")
            filtered_outputs = self._filter_relevant_info(question, agent_outputs)
            
            # Step 5: Synthesize final answer
            print(f"   [SYNTHESIS] Synthesizing focused answer from relevant agent outputs...")
            try:
                final_answer = self._synthesize_answer(question, filtered_outputs)
            except Exception as e:
                print(f"   [✗] Synthesis failed: {str(e)}")
                # Fallback: use document agent findings if synthesis fails
                final_answer = doc_result.get('findings', 'Unable to generate answer. Please try again.')
            
            # Step 6: Extract actual sources from ORIGINAL answer (before cleaning)
            # We need the original answer to detect document names
            # Also pass the question to detect multi-document queries (e.g., "first two documents")
            original_answer = final_answer
            print(f"\n   ========== [SOURCE EXTRACTION START] ==========")
            print(f"   [SOURCE] About to extract sources. Answer length: {len(original_answer)}, Context size: {len(context)}")
            print(f"   [SOURCE] Question: {question[:100]}")
            try:
                actual_sources = self._extract_actual_sources(original_answer, context, doc_result.get("relevant_sources", []), question)
                print(f"   [SOURCE] Source extraction completed. Got {len(actual_sources) if actual_sources else 0} sources")
                print(f"   [SOURCE] Sources before safety check: {[s.get('filename') for s in actual_sources] if actual_sources else 'NONE'}")
            except Exception as e:
                print(f"   [SOURCE] ERROR in source extraction: {str(e)}")
                import traceback
                traceback.print_exc()
                actual_sources = []
            
            # Validate sources: Must have at least 1 source, but can have multiple if multiple documents contributed
            if not actual_sources:
                print(f"   [SOURCE] WARNING: No sources returned, using first context document")
                if context:
                    first_doc = context[0]
                    filename = first_doc['metadata'].get('filename', 'Unknown')
                    normalized_name = DocumentAgent.normalize_document_name(filename)
                    actual_sources = [{"filename": normalized_name, "relevance": 0.50}]
            
            print(f"   [SOURCE] Final sources returned: {[s.get('filename') for s in actual_sources]}")
            print(f"   [SOURCE] Final source count: {len(actual_sources)}")
            if len(actual_sources) == 0:
                print(f"   [SOURCE] ⚠️⚠️⚠️ WARNING: NO SOURCES RETURNED ⚠️⚠️⚠️")
            elif len(actual_sources) > 3:
                print(f"   [SOURCE] ⚠️⚠️⚠️ WARNING: More than 3 sources returned ({len(actual_sources)}), this seems excessive")
            else:
                print(f"   [SOURCE] ✅ Returning {len(actual_sources)} source(s) - this is correct if multiple documents contributed")
            print(f"   ========== [SOURCE EXTRACTION END] ==========\n")
            
            # Clean answer text: remove any inline source citations (AFTER source extraction)
            final_answer = self._clean_answer_text(final_answer)
            
            # Step 7: Fact-check the answer
            print(f"   [FACT-CHECK] Calling FactCheckAgent for verification...")
            try:
            verification = self.fact_check_agent.verify(final_answer, question, context)
            except Exception as e:
                print(f"   [⚠️] Fact-check failed: {str(e)}")
                # Use default confidence if fact-check fails
                verification = {"confidence": 0.75, "verified": False, "verification": "Fact-check could not be completed"}
            agents_used.append("FactCheckAgent")
            
            print(f"   [COMPLETE] Used {len(agents_used)} agents, Confidence: {verification['confidence']:.0%}, Sources: {len(actual_sources)}")
            
            # Add final metrics to span
            span.set_attribute("agents.used", ",".join(agents_used))
            span.set_attribute("agents.count", len(agents_used))
            span.set_attribute("response.confidence", verification.get("confidence", 0.75))
            span.set_attribute("response.length", len(final_answer))
            span.set_attribute("response.sources_count", len(actual_sources))
            
            # Set success status for orchestration
            span.set_status(Status(StatusCode.OK))
            
            # Step 8: Return focused result
            return {
                "question": question,
                "answer": final_answer,
                "sources": actual_sources,
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
Your role is to create a focused, direct answer that answers ONLY what was asked.

CRITICAL RULES:
1. Answer the specific question asked - nothing more, nothing less
2. Be concise and direct (aim for 2-4 sentences unless question requires detail)
3. Include ONLY information directly relevant to answering the question
4. Skip background context unless the question specifically asks for it
5. DO NOT include source citations in the answer text - sources are tracked separately
6. If information is tangentially related but doesn't directly answer the question, exclude it

Example:
Question: "What is the revenue?"
Good: "The annual revenue is $15.2 million as of Q4 2023."
Bad: "The annual revenue is $15.2 million as of Q4 2023 [Source: Annual Financial Statements]."
Bad: "The company has strong financial performance. Revenue growth has been impressive, showing 25% YoY increase. The revenue of $15.2 million represents a milestone... [long context]"

Focus on answering the question directly without citations - sources are tracked separately."""

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

Synthesize a focused answer that DIRECTLY answers the question "{question}".

REQUIREMENTS:
- Be concise (target: 50-150 words unless question requires detail)
- Include ONLY information that directly answers the question
- Skip tangential or background information
- If multiple agents provided information, prioritize the most relevant to the question
- Start with the direct answer, then add supporting details only if necessary
- If an agent's findings are not directly relevant to answering this specific question, exclude them"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                temperature=0.3,
                max_tokens=600  # Reduced to encourage concise answers
            )
            return response.choices[0].message.content
        except Exception as e:
            # Fallback: combine agent outputs directly
            return self._simple_synthesis(agent_outputs)
    
    def _filter_relevant_info(self, question: str, agent_outputs: Dict) -> Dict:
        """Filter agent outputs to keep only what directly answers the question"""
        filtered = {}
        
        # Extract key terms from question (nouns, verbs, important words)
        question_lower = question.lower()
        # Remove stop words and focus on meaningful terms
        stop_words = {'what', 'is', 'the', 'are', 'a', 'an', 'how', 'many', 'much', 'does', 'do', 'did', 'will', 'can', 'should', 'could'}
        key_terms = [w.strip('?,!') for w in question_lower.split() 
                    if len(w) > 3 and w not in stop_words]
        
        for key, value in agent_outputs.items():
            if isinstance(value, dict):
                content = ""
                if 'findings' in value:
                    content = value['findings']
                elif 'analysis' in value:
                    content = value['analysis']
                elif 'extracted_data' in value:
                    content = value['extracted_data']
                
                if not content:
                    continue
                
                content_lower = content.lower()
                # Calculate relevance: how many key terms appear in content
                relevance = sum(1 for term in key_terms if term in content_lower) / max(len(key_terms), 1)
                
                # Also check if content directly addresses question type indicators
                question_words = {'what', 'who', 'when', 'where', 'why', 'how'}
                question_type = next((w for w in question_words if question_lower.startswith(w)), None)
                
                # For data/metrics questions, prioritize DataExtractionAgent
                if question_type == 'what' and 'data' in key:
                    relevance = max(relevance, 0.8)  # Boost relevance for data questions
                
                # Keep if at least 40% relevance or if it's the document agent (always keep)
                if relevance > 0.4 or key == 'documents':
                    filtered[key] = value
        
        return filtered if filtered else agent_outputs  # Return original if nothing passes filter
    
    def _simple_synthesis(self, agent_outputs: Dict) -> str:
        """Simple fallback synthesis if LLM call fails - returns most relevant info"""
        # Prioritize document findings or extracted data over analysis
        for key in ['documents', 'data', 'analysis']:
            if key in agent_outputs:
                value = agent_outputs[key]
                if isinstance(value, dict):
                    if 'findings' in value:
                        return value['findings'][:500]  # Limit length
                    elif 'extracted_data' in value:
                        return value['extracted_data'][:500]
                    elif 'analysis' in value:
                        return value['analysis'][:500]
        
        # Fallback: combine but keep it short
        parts = []
        for key, value in agent_outputs.items():
            if isinstance(value, dict):
                if 'findings' in value:
                    parts.append(value['findings'][:300])
                elif 'extracted_data' in value:
                    parts.append(value['extracted_data'][:300])
                elif 'analysis' in value:
                    parts.append(value['analysis'][:300])
        
        return ". ".join(parts[:2]) if parts else "Unable to generate answer."  # Limit to 2 parts
    
    def _clean_answer_text(self, answer: str) -> str:
        """Remove inline source citations from answer text"""
        if not answer:
            return answer
        
        # Remove common citation patterns
        import re
        
        # Remove [Source: ...] patterns
        answer = re.sub(r'\[Source:.*?\]', '', answer, flags=re.IGNORECASE)
        # Remove (Source: ...) patterns
        answer = re.sub(r'\(Source:.*?\)', '', answer, flags=re.IGNORECASE)
        # Remove [Document: ...] patterns
        answer = re.sub(r'\[Document:.*?\]', '', answer, flags=re.IGNORECASE)
        # Remove [From: ...] patterns
        answer = re.sub(r'\[From:.*?\]', '', answer, flags=re.IGNORECASE)
        # Remove standalone source mentions at end like "Source: filename"
        answer = re.sub(r'\s*Source:\s*[^\n]+', '', answer, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        answer = re.sub(r'\s+', ' ', answer)
        answer = re.sub(r'\s*\.\s*\.', '.', answer)  # Remove double periods
        
        return answer.strip()
    
    def _extract_actual_sources(self, answer: str, context: List[Dict], candidate_sources: List[str], question: str = "") -> List[Dict]:
        """
        Extract the sources that actually provided information used in the answer.
        
        If question requests multiple documents (e.g., "first two"), returns that many.
        Otherwise, returns all documents that contributed chunks (or single best source if only one contributed).
        """
        if not answer or not context:
            print(f"   [SOURCE-DEBUG] No answer or context - returning empty")
            return []
        
        print(f"   [SOURCE-DEBUG] ====== STARTING SOURCE EXTRACTION ======")
        print(f"   [SOURCE-DEBUG] Answer: {answer[:150]}...")
        print(f"   [SOURCE-DEBUG] Question parameter: {question[:150] if question else 'N/A (None)'}...")
        print(f"   [SOURCE-DEBUG] Question type: {type(question)}, Question is None: {question is None}")
        print(f"   [SOURCE-DEBUG] Context has {len(context)} documents")
        print(f"   [SOURCE-DEBUG] Candidate sources: {candidate_sources}")
        
        answer_lower = answer.lower()
        question_lower = question.lower() if question and isinstance(question, str) else ""
        actual_sources = []
        seen_filenames = set()
        
        # CRITICAL: Detect if question asks for multiple documents (e.g., "first two", "both documents", "all three")
        # This MUST run BEFORE checking answer_doc_names so we can return the requested count
        import re
        requested_doc_count = None
        print(f"   [SOURCE-DEBUG] ========== QUESTION DETECTION ==========")
        print(f"   [SOURCE-DEBUG] question parameter value: '{question}'")
        print(f"   [SOURCE-DEBUG] question_lower value: '{question_lower}'")
        print(f"   [SOURCE-DEBUG] question is None: {question is None}")
        print(f"   [SOURCE-DEBUG] question type: {type(question)}")
        
        if question_lower:
            print(f"   [SOURCE-DEBUG] Analyzing question for multi-doc patterns: '{question_lower}'")
            # Look for patterns like "first two", "two documents", "both documents", "all three", etc.
            # Order matters: more specific patterns first
            patterns = [
                # More flexible patterns that allow optional trailing words
                (r'first\s+two\s+documents?(?:\s+\w+)?', lambda m: 2),  # "first two documents" or "first two documents uploaded/shared/etc"
                (r'first\s+(\d+)\s+documents?(?:\s+\w+)?', lambda m: int(m.group(1))),  # "first N documents" with optional trailing word
                (r'first\s+two\s+documents?', lambda m: 2),  # "first two documents"
                (r'first\s+(\d+)\s+documents?', lambda m: int(m.group(1))),  # "first N documents"
                (r'two\s+documents?', lambda m: 2),  # Just "two documents" (common case)
                (r'both\s+documents?', lambda m: 2),  # "both documents"
                (r'all\s+three\s+documents?', lambda m: 3),  # "all three documents"
                (r'all\s+(\d+)\s+documents?', lambda m: int(m.group(1))),  # "all N documents"
                (r'(\d+)\s+documents?', lambda m: int(m.group(1))),  # Generic "N documents" (last resort, matches numbers only)
            ]
            for pattern, extractor in patterns:
                match = re.search(pattern, question_lower)
                if match:
                    requested_doc_count = extractor(match)
                    print(f"   [SOURCE-DEBUG] ✅ Question requests {requested_doc_count} document(s) (matched pattern: {pattern})")
                    break
            if requested_doc_count is None:
                print(f"   [SOURCE-DEBUG] ❌ No multi-doc pattern found in question")
        else:
            print(f"   [SOURCE-DEBUG] ⚠️⚠️⚠️ No question provided to source extraction! question_lower='{question_lower}' ⚠️⚠️⚠️")
        print(f"   [SOURCE-DEBUG] Final requested_doc_count: {requested_doc_count}")
        print(f"   [SOURCE-DEBUG] ========== END QUESTION DETECTION ==========")
        
        # Track which document's chunks were used by counting chunks per document
        doc_chunk_counts = {}  # filename -> count of chunks from this doc
        doc_highest_scores = {}  # filename -> highest score chunk from this doc
        
        for doc in context:
            filename = doc['metadata'].get('filename', '')
            if not filename:
                continue
            normalized_name = DocumentAgent.normalize_document_name(filename)
            score = doc.get('score', 0)
            
            # Count chunks from each document
            if normalized_name not in doc_chunk_counts:
                doc_chunk_counts[normalized_name] = 0
                doc_highest_scores[normalized_name] = 0
            doc_chunk_counts[normalized_name] += 1
            if score > doc_highest_scores[normalized_name]:
                doc_highest_scores[normalized_name] = score
        
        print(f"   [SOURCE-DEBUG] Document chunk usage: {doc_chunk_counts}")
        print(f"   [SOURCE-DEBUG] Document highest scores: {doc_highest_scores}")
        print(f"   [SOURCE-DEBUG] Answer text (first 200 chars): {answer[:200]}")
        print(f"   [SOURCE-DEBUG] Total context documents: {len(context)}")
        for i, doc in enumerate(context[:5]):  # Show first 5
            fn = doc['metadata'].get('filename', 'UNKNOWN')
            score = doc.get('score', 0)
            print(f"   [SOURCE-DEBUG] Context doc {i+1}: {fn} (score: {score:.3f})")
        
        # Extract unique content terms from answer (numbers, specific terms)
        import re
        
        # Extract numbers (dates, amounts, percentages, counts) - these are strong indicators
        numbers_list = re.findall(r'\d+[\.\,]?\d*', answer)
        numbers = numbers_list if numbers_list else []  # Ensure it's always a list
        
        # Extract meaningful content words from answer (excluding common words)
        # Focus on nouns, proper nouns, and specific terms
        stop_words = {'that', 'this', 'with', 'from', 'have', 'been', 'they', 'what', 'when', 'where', 
                     'were', 'about', 'which', 'there', 'their', 'them', 'then', 'than', 'these', 
                     'those', 'would', 'could', 'should', 'might', 'will', 'shall'}
        answer_words = [w.strip('.,!?;:()[]$%"\'').lower() for w in answer.split() 
                       if len(w.strip('.,!?;:()[]$%"\'')) >= 4 
                       and w.lower() not in stop_words]
        
        # Get unique answer terms (prioritize longer, more specific terms)
        answer_terms_set = set()
        for word in sorted(answer_words, key=len, reverse=True)[:20]:  # Top 20 unique terms by length
            answer_terms_set.add(word)
        answer_terms = answer_terms_set if answer_terms_set else set()  # Ensure it's always a set
        
        # Check if answer mentions specific document names
        # Check ALL documents in context, not just candidates
        answer_doc_names = []
        for doc in context:
            filename = doc['metadata'].get('filename', '')
            if not filename:
                continue
            
            normalized_name = DocumentAgent.normalize_document_name(filename)
            filename_lower = filename.lower()
            normalized_lower = normalized_name.lower()
            
            # Check original filename first (exact match with extension)
            # Use word boundaries but also allow comma/space separated matches
            import re
            
            # Check if filename appears in answer - SIMPLEST CHECK FIRST
            # Direct substring match (most reliable)
            if filename_lower in answer_lower:
                answer_doc_names.append((normalized_name, filename_lower))  # Store tuple with normalized and original
                print(f"   [SOURCE-DETECT] Found exact filename match (substring): {filename_lower}")
                continue
            
            # Also check with regex for better punctuation handling
            filename_pattern = re.escape(filename_lower)
            # Pattern: filename can appear after any punctuation or whitespace
            if re.search(r'[\(\)\[\],\s:\.\-]?' + filename_pattern + r'[\(\)\[\],\s\.\-]?', answer_lower):
                answer_doc_names.append((normalized_name, filename_lower))
                print(f"   [SOURCE-DETECT] Found exact filename match (regex): {filename_lower}")
                continue
            
            # Check normalized name
            normalized_pattern = re.escape(normalized_lower)
            if re.search(r'[\(\)\[\],\s:\.\-]?' + normalized_pattern + r'[\(\)\[\],\s\.\-]?', answer_lower) or normalized_lower in answer_lower:
                answer_doc_names.append((normalized_name, filename_lower))
                print(f"   [SOURCE-DETECT] Found normalized name match: {normalized_lower}")
                continue
            
            # Check filename without extension
            filename_base = filename_lower.rsplit('.', 1)[0]  # Remove extension
            base_pattern = re.escape(filename_base)
            if re.search(r'[\(\)\[\],\s:\.\-]?' + base_pattern + r'[\(\)\[\],\s\.\-]?', answer_lower) or filename_base in answer_lower:
                answer_doc_names.append((normalized_name, filename_lower))
                print(f"   [SOURCE-DETECT] Found filename base match: {filename_base}")
                continue
            
            # Check normalized name without extension
            normalized_base = normalized_lower.rsplit('.', 1)[0]
            normalized_base_pattern = re.escape(normalized_base)
            if re.search(r'[\(\)\[\],\s:\.\-]?' + normalized_base_pattern + r'[\(\)\[\],\s\.\-]?', answer_lower) or normalized_base in answer_lower:
                answer_doc_names.append((normalized_name, filename_lower))
                print(f"   [SOURCE-DETECT] Found normalized base match: {normalized_base}")
                continue
            
            # Check document name parts (for "project_1_doc_25.txt", check for "doc_25", "doc 25", "25", etc.)
            filename_parts = filename_base.split('_')
            if len(filename_parts) >= 2:
                # Check last part (document number)
                last_part = filename_parts[-1]
                if len(last_part) >= 2 and (last_part in answer_lower or f"doc_{last_part}" in answer_lower or f"doc {last_part}" in answer_lower):
                    answer_doc_names.append((normalized_name, filename_lower))
                    continue
                
                # Check combination of last two parts (e.g., "doc_25")
                if len(filename_parts) >= 3:
                    last_two = f"{filename_parts[-2]}_{filename_parts[-1]}"
                    last_two_spaced = f"{filename_parts[-2]} {filename_parts[-1]}"
                    if last_two in answer_lower.replace(' ', '_') or last_two_spaced in answer_lower:
                        answer_doc_names.append((normalized_name, filename_lower))
                        continue
        
        # Also check candidate sources (fallback)
        if not answer_doc_names:
            for candidate in candidate_sources:
                candidate_lower = candidate.lower()
                candidate_base = candidate_lower.rsplit('.', 1)[0]
                
                if candidate_lower in answer_lower or candidate_base in answer_lower:
                    answer_doc_names.append((candidate, candidate))  # Store as tuple for consistency
        
        # Score each document in context
        source_scores = []
        
        for doc in context:
            filename = doc['metadata'].get('filename', '')
            if not filename or filename in seen_filenames:
                continue
            
            # Normalize filename for matching
            normalized_name = DocumentAgent.normalize_document_name(filename)
            filename_lower = filename.lower()  # Define here for use in scoring
            
            # Get full document text for matching
            doc_text = doc.get('text', '').lower()
            if not doc_text:
                continue
            
            score = 0
            
            # Initialize matching variables for this iteration
            # MUST assign both values unconditionally to avoid UnboundLocalError
            # Python treats these as local variables if assigned anywhere in function
            matching_numbers = sum(1 for num in numbers if num in doc_text) if numbers else 0
            matching_terms = sum(1 for term in answer_terms if term in doc_text)
            
            # STRONG INDICATOR: Answer explicitly mentions this document name
            # Check if this document is in answer_doc_names (now tuples)
            is_mentioned = any(norm == normalized_name or orig.lower() == filename_lower 
                              for norm, orig in answer_doc_names)
            if is_mentioned or normalized_name.lower() in answer_lower or filename_lower in answer_lower:
                score += 10  # Very strong signal
            
            # STRONG INDICATOR: Numbers from answer appear in document
            if matching_numbers > 0:
                score += 5 * matching_numbers  # Each matching number is significant
            
            # MEDIUM INDICATOR: Answer terms appear in document
            score += matching_terms
            
            # WEAK INDICATOR: Document was in candidate sources
            if normalized_name in candidate_sources:
                score += 1
            
            # WEAK INDICATOR: Document has high vector search relevance
            doc_score = doc.get('score', 0)
            if doc_score > 0.8:
                score += 2
            elif doc_score > 0.6:
                score += 1
            
            # Collect all documents with any evidence - we'll filter strictly later
            # Use the already-computed matching_numbers and matching_terms
            if score > 0 or matching_terms > 0 or matching_numbers > 0:
                source_scores.append({
                    "filename": normalized_name,
                    "score": score,
                    "original_filename": filename,
                    "matching_numbers": matching_numbers,  # Already computed above
                    "matching_terms": matching_terms      # Already computed above
                })
                seen_filenames.add(filename)
                print(f"   [SOURCE-SCORE] {normalized_name}: score={score}, numbers={matching_numbers}, terms={matching_terms}")
        
        # Sort by score (highest first)
        source_scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Debug: Log what we found
        print(f"   [SOURCE-DEBUG] Answer length: {len(answer)}, answer_doc_names: {answer_doc_names}")
        print(f"   [SOURCE-DEBUG] Requested doc count from question: {requested_doc_count}")
        if answer_doc_names:
            print(f"   [SOURCE-DEBUG] Documents detected in answer: {answer_doc_names}")
        
        # PRIORITY 1: If question asks for multiple documents, use chunk-based logic to return that many
        # This takes precedence over explicit mentions because the question is explicit about wanting multiple
        if requested_doc_count and requested_doc_count > 1:
            print(f"   [SOURCE-DEBUG] Question explicitly requests {requested_doc_count} documents - using chunk-based logic")
            print(f"   [SOURCE-DEBUG] SKIPPING explicit mention check - will use chunk-based logic below")
            # Skip explicit mention check, go directly to chunk-based logic below
            # Force answer_doc_names to empty so we don't process explicit mentions
            answer_doc_names = []
        
        # PRIORITY 2: If answer explicitly mentions a document by name (actual filename), use those
        # BUT: Only if question didn't request a specific count (answer_doc_names will be empty if question requested count)
        if answer_doc_names:
            # Extract unique documents - USE ORIGINAL FILENAME AS KEY to prevent collisions
            # (Normalized names can be identical for different documents, causing loss of data)
            unique_mentioned = {}
            for norm_name, orig_name in answer_doc_names:
                # Use original filename as key to guarantee uniqueness
                if orig_name not in unique_mentioned:
                    unique_mentioned[orig_name] = norm_name
            
            print(f"   [SOURCE] Answer explicitly mentions {len(unique_mentioned)} document(s): {list(unique_mentioned.keys())}")
            print(f"   [SOURCE-DEBUG] requested_doc_count={requested_doc_count}, unique_mentioned count={len(unique_mentioned)}")
            print(f"   [SOURCE-DEBUG] Unique mentioned details: {[(orig, norm) for orig, norm in unique_mentioned.items()]}")
            
            # If multiple documents are mentioned, ALWAYS return all mentioned documents
            # BUT: If question explicitly requests a specific count, limit to that count
            # (e.g., question asks for "first two" but answer mentions 3 - return only the 2 best from mentioned)
            if len(unique_mentioned) > 1:
                # If question asks for specific number, limit results to that number
                if requested_doc_count and requested_doc_count > 1 and requested_doc_count < len(unique_mentioned):
                    print(f"   [SOURCE] Question requests {requested_doc_count} documents, but answer mentions {len(unique_mentioned)}. Limiting to top {requested_doc_count} from mentioned documents.")
                    # Prioritize by chunk usage and score
                    result = []
                    for orig_name, norm_name in unique_mentioned.items():
                        matching_score = 0.90
                        chunks = 0
                        for doc in context:
                            filename = doc['metadata'].get('filename', '')
                            if filename and filename.lower() == orig_name.lower():
                                normalized = DocumentAgent.normalize_document_name(filename)
                                matching_score = min(0.95, 0.7 + (doc.get('score', 0) * 0.2))
                                chunks = doc_chunk_counts.get(normalized, 0)
                                break
                        result.append({
                            "filename": norm_name,
                            "relevance": matching_score,
                            "chunks": chunks
                        })
                    # Sort by chunks (more chunks = more relevant), then by score
                    result.sort(key=lambda x: (x.get('chunks', 0), x.get('relevance', 0)), reverse=True)
                    result = result[:requested_doc_count]
                    # Remove chunks from final result
                    for r in result:
                        r.pop('chunks', None)
                    print(f"   [SOURCE-DEBUG] ====== SOURCE EXTRACTION COMPLETE (Limited Multiple Explicit Mentions) ======")
                    print(f"   [SOURCE-DEBUG] Returning {len(result)} source(s): {[s['filename'] for s in result]}")
                    return result
                # Otherwise, return ALL mentioned documents
                print(f"   [SOURCE] Multiple documents mentioned ({len(unique_mentioned)}), returning ALL: {list(unique_mentioned.keys())}")
                result = []
                for orig_name, norm_name in unique_mentioned.items():
                    # Find matching document in context for relevance score
                    matching_score = 0.90
                    for doc in context:
                        filename = doc['metadata'].get('filename', '')
                        if filename and filename.lower() == orig_name.lower():
                            normalized = DocumentAgent.normalize_document_name(filename)
                            matching_score = min(0.95, 0.7 + (doc.get('score', 0) * 0.2))
                            break
                    result.append({
                        "filename": norm_name,  # Use normalized name for consistency with rest of system
                        "relevance": matching_score
                    })
                print(f"   [SOURCE-DEBUG] ====== SOURCE EXTRACTION COMPLETE (Multiple Explicit Mentions) ======")
                print(f"   [SOURCE-DEBUG] Returning {len(result)} source(s): {[s['filename'] for s in result]}")
                return result
            
            # Single document mentioned - return just that one
            # unique_mentioned is now {orig_name: norm_name}, so check against keys (orig_name)
            for doc in context:
                filename = doc['metadata'].get('filename', '')
                if not filename:
                    continue
                filename_lower_check = filename.lower()
                
                # Check if this document matches any mentioned original filename
                if filename_lower_check in unique_mentioned:
                    result_filename = unique_mentioned[filename_lower_check]  # Get normalized name
                    print(f"   [SOURCE] Returning explicitly mentioned document: {result_filename}")
                    result = [{
                        "filename": result_filename,
                        "relevance": 0.95
                    }]
                    print(f"   [SOURCE-DEBUG] ====== SOURCE EXTRACTION COMPLETE (Single Explicit Match) ======")
                    print(f"   [SOURCE-DEBUG] Returning: {result}")
                    return result
            
            # If not found in context, return the first mentioned normalized name
            first_orig, first_norm = next(iter(unique_mentioned.items()))
            print(f"   [SOURCE] Document name mentioned but not in context, returning: {first_norm}")
            result = [{"filename": first_norm, "relevance": 0.90}]
            print(f"   [SOURCE-DEBUG] ====== SOURCE EXTRACTION COMPLETE (Mentioned Not in Context) ======")
            print(f"   [SOURCE-DEBUG] Returning: {result}")
            return result
        
        # No explicit document name in answer - use documents that provided chunks
        # Return ALL documents that provided chunks (if multiple, return all; if one, return that one)
        # OR if question asks for specific number, return that many top documents
        if doc_chunk_counts:
            # Sort documents by chunk count (descending), then by score
            sorted_docs = sorted(doc_chunk_counts.items(), 
                                key=lambda x: (x[1], doc_highest_scores.get(x[0], 0)), 
                                reverse=True)
            
            print(f"   [SOURCE] All chunk counts: {doc_chunk_counts}")
            print(f"   [SOURCE] Sorted by chunks: {sorted_docs}")
            
            # Filter: Only include documents that provided at least 1 chunk
            contributing_docs = []
            for filename, chunk_count in sorted_docs:
                if chunk_count > 0:  # Only include documents that actually provided chunks
                    highest_score = doc_highest_scores.get(filename, 0)
                    contributing_docs.append({
                        "filename": filename,
                        "relevance": min(0.95, 0.7 + (highest_score * 0.2)),
                        "chunks_used": chunk_count
                    })
            
            if contributing_docs:
                # Debug: Log state before decision
                print(f"   [SOURCE-DEBUG] About to check contributing_docs. requested_doc_count={requested_doc_count}, contributing_count={len(contributing_docs)}")
                
                # If question asks for specific number of documents, limit to that
                if requested_doc_count and requested_doc_count > 1:
                    # Return the top N documents (based on chunks and scores)
                    # Match documents by order in context (first document = first in upload order)
                    # But prioritize by chunk usage and score
                    print(f"   [SOURCE] Question requests {requested_doc_count} documents, selecting top {requested_doc_count}")
                    
                    # Try to match "first N documents" by finding documents in order of context
                    # Context order typically reflects upload order
                    context_order_map = {}
                    for idx, doc in enumerate(context):
                        filename = doc['metadata'].get('filename', '')
                        if filename:
                            normalized = DocumentAgent.normalize_document_name(filename)
                            if normalized not in context_order_map:
                                context_order_map[normalized] = idx
                    
                    # Sort contributing docs: first by context order (for "first N"), then by chunks/score
                    contributing_docs.sort(key=lambda d: (
                        context_order_map.get(d['filename'], 999),  # Lower index = earlier in context
                        -d['chunks_used'],  # More chunks = better
                        -d['relevance']  # Higher relevance = better
                    ))
                    
                    # Take top N
                    result = contributing_docs[:requested_doc_count]
                    print(f"   [SOURCE] Selected {len(result)} document(s) based on question request:")
                    for doc in result:
                        print(f"   [SOURCE]   - {doc['filename']}: {doc['chunks_used']} chunks, relevance: {doc['relevance']:.2f}")
                else:
                    # Normal case: return all documents that contributed chunks
                    print(f"   [SOURCE] Found {len(contributing_docs)} document(s) that provided chunks:")
                    for doc in contributing_docs:
                        print(f"   [SOURCE]   - {doc['filename']}: {doc['chunks_used']} chunks, relevance: {doc['relevance']:.2f}")
                    result = contributing_docs
                
                # Remove chunks_used from final result (internal metadata only)
                for doc in result:
                    doc.pop('chunks_used', None)
                
                print(f"   [SOURCE-DEBUG] ====== SOURCE EXTRACTION COMPLETE (Chunk-Based) ======")
                print(f"   [SOURCE-DEBUG] Returning {len(result)} source(s): {[s['filename'] for s in result]}")
                return result
            else:
                # No documents provided chunks (shouldn't happen, but handle gracefully)
                print(f"   [SOURCE] WARNING: doc_chunk_counts exists but all counts are 0")
        
        # Fallback: use scoring logic if chunk tracking didn't work
        if source_scores:
            # Priority 1: Sources with matching numbers (data extracted from these docs)
            sources_with_numbers = []
            for src in source_scores:
                matching_numbers = src.get('matching_numbers', 0)
                matching_terms = src.get('matching_terms', 0)
                score = src.get('score', 0)
                if matching_numbers > 0:
                    sources_with_numbers.append(src)
                    print(f"   [SOURCE-SELECT] Candidate with numbers: {src['filename']} (score: {score}, numbers: {matching_numbers})")
            
            # If found sources with numbers, return ALL of them (they all contributed data)
            if sources_with_numbers:
                print(f"   [SOURCE] Using {len(sources_with_numbers)} source(s) with matching numbers")
                result = []
                for src in sources_with_numbers:
                    score = src.get('score', 0)
                    result.append({
                        "filename": src['filename'],
                        "relevance": min(0.95, 0.7 + (score / 30))
                    })
                print(f"   [SOURCE-DEBUG] ====== SOURCE EXTRACTION COMPLETE (Matching Numbers) ======")
                print(f"   [SOURCE-DEBUG] Returning {len(result)} source(s): {[s['filename'] for s in result]}")
                return result
            
            # Priority 2: Find sources with good term overlap (5+ terms indicates strong content match)
            sources_with_terms = []
            max_term_count = 0
            
            for src in source_scores:
                matching_terms = src.get('matching_terms', 0)
                if matching_terms >= 5:  # Only include sources with significant term overlap
                    sources_with_terms.append(src)
                    if matching_terms > max_term_count:
                        max_term_count = matching_terms
                    print(f"   [SOURCE-SELECT] Candidate with terms: {src['filename']} (score: {src.get('score', 0)}, terms: {matching_terms})")
            
            # If found sources with good term match, return ALL of them
            if sources_with_terms:
                print(f"   [SOURCE] Using {len(sources_with_terms)} source(s) with good term overlap (max {max_term_count} terms)")
                result = []
                for src in sources_with_terms:
                    score = src.get('score', 0)
                    result.append({
                        "filename": src['filename'],
                        "relevance": min(0.95, 0.7 + (score / 30))
                    })
                print(f"   [SOURCE-DEBUG] ====== SOURCE EXTRACTION COMPLETE (Matching Terms) ======")
                print(f"   [SOURCE-DEBUG] Returning {len(result)} source(s): {[s['filename'] for s in result]}")
                return result
            
            # Priority 3: Use top scored sources (limit to top 2 if multiple have high scores)
            # If there's a clear winner, use just that; if multiple are close, use top 2
            if len(source_scores) >= 2:
                top_score = source_scores[0].get('score', 0)
                second_score = source_scores[1].get('score', 0)
                
                # If top 2 scores are within 30% of each other, include both
                if top_score > 0 and second_score / top_score >= 0.7:
                    print(f"   [SOURCE] Top 2 sources have similar scores ({top_score:.1f} vs {second_score:.1f}), returning both")
                    result = []
                    for src in source_scores[:2]:
                        result.append({
                            "filename": src['filename'],
                            "relevance": 0.75
                        })
                    print(f"   [SOURCE-DEBUG] ====== SOURCE EXTRACTION COMPLETE (Top 2 Scores) ======")
                    print(f"   [SOURCE-DEBUG] Returning {len(result)} source(s): {[s['filename'] for s in result]}")
                    return result
            
            # Clear winner or only one source - return just the top one
            top_source = source_scores[0]
            print(f"   [SOURCE] Using top scored source: {top_source['filename']} (score: {top_source.get('score', 0)})")
            result = [{
                "filename": top_source['filename'],
                "relevance": 0.75
            }]
            print(f"   [SOURCE-DEBUG] ====== SOURCE EXTRACTION COMPLETE (Top Score) ======")
            print(f"   [SOURCE-DEBUG] Returning {len(result)} source(s): {[s['filename'] for s in result]}")
            return result
        
        # Last resort: if no scored sources and we have candidates, take top 1
        if candidate_sources:
            print(f"   [SOURCE] Fallback to candidate sources: {candidate_sources}")
            # Return top 2 candidates if multiple (they were all considered relevant)
            # But limit to max 3 to avoid too many sources
            num_to_return = min(len(candidate_sources), 3)
            result = [{"filename": candidate_sources[i], "relevance": 0.70} for i in range(num_to_return)]
            print(f"   [SOURCE-DEBUG] ====== SOURCE EXTRACTION COMPLETE (Candidates) ======")
            print(f"   [SOURCE-DEBUG] Returning {len(result)} source(s): {[s['filename'] for s in result]}")
            return result
        
        # Absolute last resort: use first document from context
        if context:
            first_doc = context[0]
            filename = first_doc['metadata'].get('filename', 'Unknown')
            normalized_name = DocumentAgent.normalize_document_name(filename)
            print(f"   [SOURCE] Last resort: using first context document: {normalized_name}")
            result = [{"filename": normalized_name, "relevance": 0.50}]
            # ABSOLUTE FINAL CHECK
            if len(result) > 1:
                result = [result[0]]
            return result
        
        # Should never reach here, but return empty list
        print(f"   [SOURCE] ERROR: No sources found - returning empty list")
        print(f"   [SOURCE-DEBUG] ====== SOURCE EXTRACTION COMPLETE (ERROR) ======")
        return []

