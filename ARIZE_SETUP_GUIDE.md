# Arize Phoenix Observability Setup Guide

## ✅ Setup Complete!

Arize Phoenix observability has been successfully integrated into your Autonomous Diligence Cloud application.

## 🎯 What Was Implemented

### 1. Dependencies Installed
- `arize-phoenix>=4.0.0` - Phoenix observability platform
- `openinference-instrumentation-openai>=0.1.0` - OpenAI instrumentation
- `opentelemetry-sdk>=1.20.0` - OpenTelemetry SDK
- `opentelemetry-exporter-otlp>=1.20.0` - OTLP exporter

### 2. Telemetry Bootstrap

#### `backend/telemetry.py`
- Centralizes Phoenix/OpenTelemetry wiring
- Configures the OTLP/HTTP exporter with Phoenix workspace credentials
- Registers `openinference` instrumentation so OpenAI calls appear as child spans

#### `backend/main.py`
- Loads environment variables and calls `init_tracing()` on startup
- Creates request spans for `/api/ask`, attaches question metadata, and returns span identifiers to clients for evaluation logging

### 3. Required Environment Variables

Configure the following variables wherever the FastAPI service runs (Render, local `.env`, GitHub Actions, etc.):

```env
# Phoenix workspace REST base (usually https://app.phoenix.arize.com/s/<workspace>/v1)
PHOENIX_API_URL=https://app.phoenix.arize.com/s/<workspace>/v1

# User API key generated under Settings → API Keys → User Keys
PHOENIX_API_KEY=your_user_key_here

# Logical project name used to group traces/datasets inside Phoenix
PHOENIX_PROJECT=Diligence-Cloud

# Optional: override service name in span resources
# PHOENIX_SERVICE_NAME=diligence-cloud-backend

# Optional: override traces endpoint directly (defaults to `${PHOENIX_API_URL}/traces`)
# PHOENIX_TRACES_ENDPOINT=https://app.phoenix.arize.com/s/<workspace>/v1/traces
```

> **Heads up:** The instrumentation automatically sends OTLP traces over HTTPS with the proper `Authorization: Bearer <PHOENIX_API_KEY>` header. No local Phoenix instance is required—the backend now streams spans directly to the hosted workspace.

## 🚀 End-to-End Workflow

1. **Deploy / run the FastAPI backend** with the environment variables above. The service emits:
   - A root span for each `/api/ask` request (`api.ask_question`)
   - Child spans for every agent (`DocumentAgent.call_llm`, etc.)
   - OpenAI SDK spans via OpenInference instrumentation

2. **Capture span identifiers**: Every `/api/ask` response includes a `telemetry` payload:
   ```json
   {
     "trace_id": "35f8…",
     "span_id": "7c2a…"
   }
   ```
   These IDs are used by the evaluation runner so Phoenix can stitch pass/fail annotations directly onto the spans.

3. **Run evaluations** (see below) to push DocumentEvaluations that align with the captured spans.

## 🧪 Streaming Evaluation Runs to Phoenix

Use the updated `run_evals.py` script to send automated evaluation results directly to Phoenix:

1. **Install dependencies** (already included in `requirements.txt`):
   ```bash
   pip install arize-phoenix
   ```

2. **Export credentials** (local example):
   ```bash
   export PHOENIX_API_URL=https://api.phoenix.arize.com/v1
   export PHOENIX_API_KEY=your_workspace_api_key
   export PHOENIX_PROJECT=diligence-evals
   ```

3. **Run evaluations**:
   ```bash
   python run_evals.py --base-url https://diligence-cloud.onrender.com
   ```

Each evaluation logs:
- question, project, category, difficulty
- latency, pass/fail status, errors
- term/source/criteria scores and missing items
- agents used and number of sources

You can filter or trend these records in Phoenix to monitor quality regressions over time.

## 📊 What You Can Monitor

### 1. LLM Traces
- Every OpenAI API call is automatically traced
- See prompts, responses, and token usage
- Track latency for each call

### 2. Multi-Agent Workflows
- Visualize the flow through different agents:
  - DocumentAgent
  - AnalysisAgent
  - DataExtractionAgent
  - FactCheckAgent
  - OrchestratorAgent

### 3. Performance Metrics
- **Latency**: Response times for each agent and overall request
- **Token Usage**: Track costs across all LLM calls
- **Confidence Scores**: Monitor answer quality
- **Error Rates**: Identify failing operations

### 4. Custom Attributes
Each trace includes:
- `question`: The user's question
- `question.type`: Classification (analysis, data, summary, etc.)
- `agent.name`: Which agent processed the request
- `agent.model`: Model used (gpt-4o-mini, etc.)
- `agents.used`: List of all agents involved
- `agents.count`: Number of agents used
- `response.confidence`: Final confidence score
- `response.tokens`: Total tokens used
- `processing.time_ms`: Total processing time

## 🔍 Viewing Traces

### In Phoenix UI (http://localhost:6006):

1. **Traces Tab**: See all LLM calls in real-time
2. **Projects**: Organize traces by project
3. **Spans**: Drill down into individual operations
4. **Metrics**: View aggregated statistics

### Example Trace Structure:
```
api.ask_question (FastAPI endpoint)
└── orchestrator.orchestrate
    ├── DocumentAgent.call_llm
    ├── AnalysisAgent.call_llm
    ├── DataExtractionAgent.call_llm (conditional)
    ├── orchestrator._synthesize_answer
    └── FactCheckAgent.call_llm
```

## 💡 Use Cases

### 1. Debug Multi-Agent Behavior
- See which agents are called for different question types
- Understand the decision-making process
- Identify bottlenecks in agent coordination

### 2. Optimize Costs
- Track token usage per agent
- Identify expensive operations
- Optimize prompt engineering

### 3. Improve Quality
- Monitor confidence scores
- Find low-quality responses
- A/B test different prompts

### 4. Performance Tuning
- Identify slow agents
- Optimize response times
- Balance quality vs. speed

## 🛠️ Troubleshooting

### Phoenix UI Not Loading
- Check that port 6006 is not in use
- Verify `PHOENIX_LOCAL=true` in `.env`
- Look for Phoenix startup messages in server logs

### No Traces Appearing
- Ensure OpenAI API key is set correctly
- Check that questions are being processed
- Verify Phoenix is initialized (look for ✅ message)

### Connection Errors (Arize Cloud)
- Verify API key and Space ID are correct
- Check network connectivity
- Ensure endpoint URL is correct

## 📈 Next Steps

1. **Explore Phoenix UI**: Visit http://localhost:6006 and explore your traces
2. **Ask Questions**: Use your application and watch traces appear in real-time
3. **Analyze Patterns**: Look for trends in agent usage and performance
4. **Optimize**: Use insights to improve prompts and agent logic
5. **Production**: When ready, switch to Arize Cloud for persistent storage

## 🔒 Security Notes

- Phoenix local mode stores data in memory only
- Arize Cloud provides secure, persistent storage
- Never commit `.env` file with API keys
- API keys are transmitted securely over HTTPS

## 📚 Resources

- **Phoenix Documentation**: https://arize.com/docs/phoenix
- **OpenTelemetry**: https://opentelemetry.io/
- **Arize Platform**: https://phoenix.arize.com/

## ✨ Features Enabled

- ✅ Automatic OpenAI call tracing
- ✅ Multi-agent workflow visualization
- ✅ Token usage tracking
- ✅ Latency monitoring
- ✅ Error tracking
- ✅ Custom span attributes
- ✅ Real-time trace viewing
- ✅ Local and cloud deployment options

---

**Your application now has enterprise-grade observability! 🎉**

Access Phoenix UI: **http://localhost:6006**

