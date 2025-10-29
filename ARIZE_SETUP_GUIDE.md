# Arize Phoenix Observability Setup Guide

## ✅ Setup Complete!

Arize Phoenix observability has been successfully integrated into your Autonomous Diligence Cloud application.

## 🎯 What Was Implemented

### 1. Dependencies Installed
- `arize-phoenix>=4.0.0` - Phoenix observability platform
- `openinference-instrumentation-openai>=0.1.0` - OpenAI instrumentation
- `opentelemetry-sdk>=1.20.0` - OpenTelemetry SDK
- `opentelemetry-exporter-otlp>=1.20.0` - OTLP exporter

### 2. Configuration Files Created

#### `backend/arize_config.py`
- Centralized observability configuration
- Supports both local Phoenix and Arize Cloud
- Automatic OpenAI instrumentation
- Custom span creation utilities

#### `.env` Configuration
Added Phoenix configuration options:
```env
# Run Phoenix locally (enabled by default for development)
PHOENIX_LOCAL=true
PHOENIX_PORT=6006

# For production, use Arize Cloud (commented out)
# PHOENIX_LOCAL=false
# ARIZE_API_KEY=your_arize_api_key_here
# ARIZE_SPACE_ID=your_space_id_here
# PHOENIX_COLLECTOR_ENDPOINT=https://app.phoenix.arize.com
```

### 3. Instrumentation Added

#### `backend/main.py`
- Arize initialization on startup
- Request-level tracing for `/api/ask` endpoint
- Automatic metrics collection:
  - Processing time
  - Response confidence
  - Source count
  - Error tracking

#### `backend/multi_agent_system.py`
- **BaseAgent**: Instrumented all LLM calls with:
  - Agent name and model
  - Prompt lengths
  - Response latency
  - Token usage (prompt, completion, total)
  - Error tracking

- **OrchestratorAgent**: Added orchestration tracing with:
  - Question classification
  - Agent coordination
  - Multi-agent workflow tracking
  - Final confidence scores

## 🚀 How to Use

### Option 1: Local Phoenix (Development - Currently Active)

Phoenix is running locally and accessible at:
**http://localhost:6006**

This is the default mode and requires no additional setup. Just start your server:

```bash
python3 backend/main.py
```

Phoenix will automatically launch and you'll see:
```
🔍 Starting Phoenix locally...
✅ Phoenix UI available at: http://localhost:6006
✅ Arize Phoenix observability initialized successfully!
```

### Option 2: Arize Cloud (Production)

For production deployment:

1. **Sign up for Arize Phoenix**: https://phoenix.arize.com/

2. **Get your credentials**:
   - API Key: Settings → API Keys
   - Space ID: Workspace settings

3. **Update `.env`**:
```env
PHOENIX_LOCAL=false
ARIZE_API_KEY=your_actual_api_key
ARIZE_SPACE_ID=your_space_id
PHOENIX_COLLECTOR_ENDPOINT=https://app.phoenix.arize.com
```

4. **Restart server**:
```bash
python3 backend/main.py
```

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

