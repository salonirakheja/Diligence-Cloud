"""
AI Agents Module
Handles AI-powered question answering and document analysis
"""

import os
from typing import List, Dict, Any
import json

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class DiligenceAgent:
    """AI agent for answering questions about documents"""
    
    def __init__(self, openai_key: str = None, openrouter_key: str = None):
        """
        Initialize the diligence agent
        
        Args:
            openai_key: OpenAI API key
            openrouter_key: OpenRouter API key (alternative to OpenAI)
        """
        self.openai_key = openai_key
        self.openrouter_key = openrouter_key
        
        if not openai_key and not openrouter_key:
            raise ValueError("Either openai_key or openrouter_key must be provided")
        
        # Set default model
        self.model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
        
        # Configure OpenAI if using OpenAI directly
        if openai_key and OPENAI_AVAILABLE:
            openai.api_key = openai_key
    
    def generate_answer(self, question: str, context: List[Dict]) -> Dict:
        """
        Generate an answer to a question based on document context
        
        Args:
            question: User's question
            context: List of relevant document chunks with metadata
            
        Returns:
            Dictionary with answer, sources, and confidence score
        """
        if not context:
            return {
                "question": question,
                "answer": "I don't have enough information to answer this question. Please upload relevant documents.",
                "sources": [],
                "confidence": 0.0
            }
        
        # Prepare context text from chunks
        context_text = self._format_context(context)
        
        # Create prompt
        system_prompt = """You are an expert diligence analyst assistant. Your role is to:
1. Answer questions accurately based on the provided document context
2. Cite specific sources when making statements
3. Be clear when information is not available in the documents
4. Provide concise, professional answers
5. Use data and numbers when available

If you cannot answer the question with the given context, clearly state that."""

        user_prompt = f"""Based on the following context from uploaded documents, answer the question professionally.

CONTEXT:
{context_text}

QUESTION: {question}

Provide a clear, concise answer. If the information is not in the context, say so."""

        # Generate answer
        try:
            answer_text = self._call_llm(system_prompt, user_prompt)
            
            # Calculate confidence score
            confidence = self._calculate_confidence(answer_text, context)
            
            # Extract sources
            sources = self._extract_sources(context)
            
            return {
                "question": question,
                "answer": answer_text,
                "sources": sources,
                "confidence": confidence
            }
        
        except Exception as e:
            return {
                "question": question,
                "answer": f"Error generating answer: {str(e)}",
                "sources": [],
                "confidence": 0.0
            }
    
    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call the LLM API (OpenAI or OpenRouter)
        
        Args:
            system_prompt: System message
            user_prompt: User message
            
        Returns:
            Generated response text
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Use OpenRouter if available
        if self.openrouter_key and REQUESTS_AVAILABLE:
            return self._call_openrouter(messages)
        
        # Otherwise use OpenAI
        elif self.openai_key and OPENAI_AVAILABLE:
            return self._call_openai(messages)
        
        else:
            raise Exception("No valid API configuration found")
    
    def _call_openai(self, messages: List[Dict]) -> str:
        """Call OpenAI API using v1.0+ syntax"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_key)
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.3,
                max_tokens=1000
            )
            return response.choices[0].message.content
        
        except Exception as e:
            # Fallback to GPT-3.5 if GPT-4 fails
            try:
                from openai import OpenAI
                client = OpenAI(api_key=self.openai_key)
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.3,
                    max_tokens=1000
                )
                return response.choices[0].message.content
            except Exception as e2:
                raise Exception(f"OpenAI API error: {str(e2)}")
    
    def _call_openrouter(self, messages: List[Dict]) -> str:
        """Call OpenRouter API"""
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openrouter_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/diligence-cloud",
                    "X-Title": "Autonomous Diligence Cloud"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.3,
                    "max_tokens": 1000
                },
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            return result["choices"][0]["message"]["content"]
        
        except Exception as e:
            raise Exception(f"OpenRouter API error: {str(e)}")
    
    def _format_context(self, context: List[Dict]) -> str:
        """Format context chunks for the prompt"""
        formatted = []
        
        for i, chunk in enumerate(context, 1):
            metadata = chunk['metadata']
            text = chunk['text']
            
            source_info = f"[Source {i}: {metadata.get('filename', 'Unknown')}"
            if metadata.get('chunk_index') is not None:
                source_info += f", Section {metadata['chunk_index'] + 1}"
            source_info += "]"
            
            formatted.append(f"{source_info}\n{text}")
        
        return "\n\n".join(formatted)
    
    def _extract_sources(self, context: List[Dict]) -> List[Dict]:
        """Extract source information from context"""
        sources = []
        seen_files = set()
        
        for chunk in context:
            metadata = chunk['metadata']
            filename = metadata.get('filename', 'Unknown')
            
            if filename not in seen_files:
                seen_files.add(filename)
                sources.append({
                    'filename': filename,
                    'file_type': metadata.get('file_type', 'unknown'),
                    'relevance': round(chunk.get('score', 0), 2)
                })
        
        return sources
    
    def _calculate_confidence(self, answer: str, context: List[Dict]) -> float:
        """
        Calculate confidence score for the answer
        
        Simple heuristic based on:
        - Whether answer indicates uncertainty
        - Average relevance score of context
        - Length and completeness of answer
        """
        confidence = 0.7  # Base confidence
        
        # Reduce confidence if answer indicates uncertainty
        uncertainty_phrases = [
            "don't have enough information",
            "not available in",
            "cannot find",
            "not mentioned",
            "unclear from",
            "not specified"
        ]
        
        answer_lower = answer.lower()
        if any(phrase in answer_lower for phrase in uncertainty_phrases):
            confidence = 0.3
        
        # Adjust based on context relevance
        if context:
            avg_score = sum(c.get('score', 0) for c in context) / len(context)
            confidence *= (0.5 + avg_score * 0.5)  # Scale by average relevance
        
        # Boost confidence for longer, detailed answers
        if len(answer) > 200 and confidence > 0.3:
            confidence = min(0.95, confidence + 0.1)
        
        return round(confidence, 2)


class AnalysisAgent:
    """Advanced agent for document analysis and insights"""
    
    def __init__(self, diligence_agent: DiligenceAgent):
        """Initialize with base diligence agent"""
        self.agent = diligence_agent
    
    def summarize_document(self, doc_id: str, context: List[Dict]) -> str:
        """Generate a summary of a document"""
        prompt = "Provide a comprehensive summary of the key information in this document."
        result = self.agent.generate_answer(prompt, context)
        return result['answer']
    
    def extract_key_facts(self, topic: str, context: List[Dict]) -> List[str]:
        """Extract key facts about a specific topic"""
        prompt = f"List the key facts and data points about {topic} found in the documents."
        result = self.agent.generate_answer(prompt, context)
        
        # Parse bullet points from answer
        facts = []
        for line in result['answer'].split('\n'):
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line[0].isdigit()):
                facts.append(line.lstrip('-•0123456789. '))
        
        return facts
    
    def compare_documents(self, question: str, context: List[Dict]) -> str:
        """Compare information across multiple documents"""
        prompt = f"Compare and contrast the information about: {question}"
        result = self.agent.generate_answer(prompt, context)
        return result['answer']

