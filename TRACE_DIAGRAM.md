# Multi-Agent System Trace Diagram

## Complete Trace Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         HTTP POST /api/ask                                   │
│                    [api.ask_question span]                                   │
│                                                                               │
│  Attributes:                                                                  │
│  • question: "What is the AI report about?"                                  │
│  • has_document_ids: false                                                   │
│  • processing.time_ms: 8542.3                                                │
│  • response.confidence: 0.95                                                 │
│  • response.sources_count: 3                                                 │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR AGENT                                        │
│              [orchestrator.orchestrate span]                                 │
│                                                                               │
│  Attributes:                                                                  │
│  • question: "What is the AI report about?"                                  │
│  • context.size: 5                                                           │
│  • orchestrator.model: "gpt-4o-mini"                                         │
│  • question.type: "data"                                                     │
│  • agents.used: "DocumentAgent,DataExtractionAgent,FactCheckAgent"          │
│  • agents.count: 3                                                           │
│  • response.confidence: 0.95                                                 │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┬─────────────────┐
                ▼               ▼               ▼                 ▼
    ┌───────────────────┐ ┌──────────────┐ ┌─────────────┐ ┌──────────────┐
    │ STEP 1: CLASSIFY  │ │  STEP 2:     │ │  STEP 3:    │ │  STEP 4:     │
    │    Question       │ │  Document    │ │  Specialized│ │  Synthesize  │
    │                   │ │  Retrieval   │ │  Agents     │ │  & Verify    │
    └───────────────────┘ └──────┬───────┘ └──────┬──────┘ └──────┬───────┘
                                 │                │                │
                                 ▼                │                │
                    ┌────────────────────────┐   │                │
                    │   DOCUMENT AGENT       │   │                │
                    │ [DocumentAgent.call_llm]│  │                │
                    │                        │   │                │
                    │ Attributes:            │   │                │
                    │ • agent.name: "DocumentAgent"               │
                    │ • agent.model: "gpt-4o-mini"                │
                    │ • agent.temperature: 0.3                    │
                    │ • prompt.system_length: 245                 │
                    │ • prompt.user_length: 1842                  │
                    │ • response.latency_ms: 2341.2               │
                    │ • response.tokens: 1523                     │
                    │ • response.prompt_tokens: 487               │
                    │ • response.completion_tokens: 1036          │
                    │                        │   │                │
                    │ Output:                │   │                │
                    │ • Findings & Citations │   │                │
                    │ • Relevant Sources     │   │                │
                    └────────────────────────┘   │                │
                                                 │                │
                        ┌────────────────────────┼────────────────┘
                        │                        │
                        ▼                        ▼
            ┌───────────────────────┐  ┌───────────────────────┐
            │   ANALYSIS AGENT      │  │  DATA EXTRACTION      │
            │ [AnalysisAgent.call_llm]│ [DataExtractionAgent.call_llm]
            │                       │  │                       │
            │ Called if question    │  │ Called if question    │
            │ type is:              │  │ type is:              │
            │ • analysis            │  │ • data                │
            │ • summary             │  │ • financial           │
            │ • comparison          │  │ • metrics             │
            │ • general             │  │                       │
            │                       │  │                       │
            │ Attributes:           │  │ Attributes:           │
            │ • agent.name          │  │ • agent.name          │
            │ • agent.model         │  │ • agent.model         │
            │ • response.latency_ms │  │ • response.latency_ms │
            │ • response.tokens     │  │ • response.tokens     │
            │                       │  │                       │
            │ Output:               │  │ Output:               │
            │ • Deep Analysis       │  │ • Extracted Data      │
            │ • Key Insights        │  │ • Numbers & Metrics   │
            └───────────────────────┘  └───────────────────────┘
                        │                        │
                        └────────────┬───────────┘
                                     │
                                     ▼
                        ┌────────────────────────┐
                        │   SYNTHESIS STEP       │
                        │ [_synthesize_answer]   │
                        │                        │
                        │ OpenAI Call:           │
                        │ • Combines all agent   │
                        │   outputs              │
                        │ • Creates coherent     │
                        │   final answer         │
                        │                        │
                        │ Attributes:            │
                        │ • model: "gpt-4o-mini" │
                        │ • response.tokens      │
                        │ • response.latency_ms  │
                        └────────────┬───────────┘
                                     │
                                     ▼
                        ┌────────────────────────┐
                        │   FACT-CHECK AGENT     │
                        │ [FactCheckAgent.call_llm]
                        │                        │
                        │ Attributes:            │
                        │ • agent.name           │
                        │ • agent.model          │
                        │ • response.latency_ms  │
                        │ • response.tokens      │
                        │                        │
                        │ Output:                │
                        │ • Verification Result  │
                        │ • Confidence Score     │
                        │   (0.40 - 0.95)        │
                        └────────────┬───────────┘
                                     │
                                     ▼
                        ┌────────────────────────┐
                        │   FINAL RESPONSE       │
                        │                        │
                        │ • Question             │
                        │ • Answer               │
                        │ • Sources              │
                        │ • Confidence           │
                        │ • Agents Used          │
                        │ • Question Type        │
                        │ • Verification Notes   │
                        └────────────────────────┘
```

## Question Type Routing

```
                    ┌─────────────────────┐
                    │  Question Received  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Classify Question  │
                    └──────────┬──────────┘
                               │
                ┌──────────────┼──────────────┬──────────────┐
                │              │              │              │
                ▼              ▼              ▼              ▼
        ┌──────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐
        │   "data"     │ │"analysis"│ │"summary" │ │ "financial"  │
        │  "metrics"   │ │"general" │ │"comparison"│ "definition" │
        └──────┬───────┘ └─────┬────┘ └─────┬────┘ └──────┬───────┘
               │               │             │             │
               ▼               ▼             ▼             ▼
    ┌──────────────────┐ ┌─────────────────────────────────────┐
    │ DocumentAgent +  │ │    DocumentAgent +                  │
    │ DataExtraction   │ │    AnalysisAgent                    │
    │ Agent            │ │                                     │
    └──────────────────┘ └─────────────────────────────────────┘
```

## Token Usage Tracking

Each LLM call tracks:

```
┌────────────────────────────────────────┐
│         OpenAI API Call                │
├────────────────────────────────────────┤
│ Prompt Tokens:         487             │
│ Completion Tokens:     1036            │
│ Total Tokens:          1523            │
│                                        │
│ Latency:              2341.2 ms        │
│ Model:                gpt-4o-mini      │
│ Temperature:          0.3              │
└────────────────────────────────────────┘
```

## Error Tracking

When errors occur:

```
┌────────────────────────────────────────┐
│         Error Span                     │
├────────────────────────────────────────┤
│ error: true                            │
│ error.message: "API rate limit..."    │
│ agent.name: "DocumentAgent"           │
│ timestamp: 2024-10-27T...             │
└────────────────────────────────────────┘
```

## Span Hierarchy Example

```
Root Span: api.ask_question (8542ms)
│
├─ orchestrator.orchestrate (8234ms)
│  │
│  ├─ DocumentAgent.call_llm (2341ms)
│  │  └─ OpenAI API Call [auto-instrumented]
│  │     • Model: gpt-4o-mini
│  │     • Tokens: 1523
│  │
│  ├─ DataExtractionAgent.call_llm (1876ms)
│  │  └─ OpenAI API Call [auto-instrumented]
│  │     • Model: gpt-4o-mini
│  │     • Tokens: 1342
│  │
│  ├─ _synthesize_answer (2145ms)
│  │  └─ OpenAI API Call [auto-instrumented]
│  │     • Model: gpt-4o-mini
│  │     • Tokens: 1687
│  │
│  └─ FactCheckAgent.call_llm (1872ms)
│     └─ OpenAI API Call [auto-instrumented]
│        • Model: gpt-4o-mini
│        • Tokens: 1456
│
└─ Response Assembly (308ms)
```

## Attributes Captured

### Request Level
- `question` - User's question (truncated to 100 chars)
- `has_document_ids` - Whether specific docs were requested
- `processing.time_ms` - Total processing time
- `response.confidence` - Final confidence score
- `response.sources_count` - Number of sources cited

### Orchestrator Level
- `question.type` - Classification (data, analysis, summary, etc.)
- `context.size` - Number of relevant documents
- `orchestrator.model` - Model being used
- `agents.used` - Comma-separated list of agents
- `agents.count` - Number of agents involved

### Agent Level
- `agent.name` - Name of the agent (DocumentAgent, etc.)
- `agent.model` - Model used by agent
- `agent.temperature` - Temperature setting
- `prompt.system_length` - System prompt length
- `prompt.user_length` - User prompt length
- `response.latency_ms` - Response time
- `response.tokens` - Total tokens
- `response.prompt_tokens` - Input tokens
- `response.completion_tokens` - Output tokens

### Error Level
- `error` - Boolean flag
- `error.message` - Error description

## Phoenix UI Views

### 1. Traces View
Shows all traces with:
- Timestamp
- Duration
- Status (success/error)
- Number of spans
- Root operation name

### 2. Trace Detail View
For each trace:
- Waterfall diagram of all spans
- Timing breakdown
- Token usage per call
- Custom attributes
- Error details (if any)

### 3. Spans View
Individual span details:
- Start/end time
- Duration
- Parent/child relationships
- All attributes
- LLM input/output (if enabled)

## Cost Tracking

Based on token usage:
```
┌────────────────────────────────────────┐
│      Per-Request Cost Estimate         │
├────────────────────────────────────────┤
│ DocumentAgent:        487 → $0.0024    │
│ DataExtraction:       342 → $0.0017    │
│ Synthesis:            687 → $0.0034    │
│ FactCheck:            456 → $0.0023    │
├────────────────────────────────────────┤
│ Total Tokens:        1972              │
│ Estimated Cost:      $0.0098           │
└────────────────────────────────────────┘
```

## How to View in Phoenix

1. **Start your server** (already running)
2. **Open Phoenix UI**: http://localhost:6006
3. **Ask a question** in your app
4. **See the trace** appear in real-time
5. **Click on trace** to see full waterfall diagram
6. **Explore spans** to see individual agent calls
7. **View attributes** to see all metadata

---

**Your multi-agent system is fully instrumented and ready for visualization! 🎉**

