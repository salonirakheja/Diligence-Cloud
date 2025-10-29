"""
Arize Phoenix Observability Configuration
Instruments OpenAI calls for monitoring and debugging
"""

import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from openinference.instrumentation.openai import OpenAIInstrumentor
import phoenix as px

def initialize_arize_observability():
    """Initialize Arize Phoenix for LLM observability"""
    
    # Check if Arize is enabled
    arize_enabled = os.getenv("ARIZE_API_KEY") is not None
    phoenix_local = os.getenv("PHOENIX_LOCAL", "false").lower() == "true"
    
    if not arize_enabled and not phoenix_local:
        print("⚠️  Arize observability not configured. Set ARIZE_API_KEY or PHOENIX_LOCAL=true")
        return None
    
    try:
        if phoenix_local:
            # Run Phoenix locally
            print("🔍 Starting Phoenix locally...")
            phoenix_port = int(os.getenv("PHOENIX_PORT", 6006))
            session = px.launch_app(port=phoenix_port)
            print(f"✅ Phoenix UI available at: http://localhost:{phoenix_port}")
            endpoint = f"http://localhost:{phoenix_port}/v1/traces"
        else:
            # Use Arize Cloud
            print("🔍 Connecting to Arize Phoenix Cloud...")
            arize_api_key = os.getenv("ARIZE_API_KEY")
            space_id = os.getenv("ARIZE_SPACE_ID", "default")
            endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "https://app.phoenix.arize.com")
            
            # Set up authentication headers
            headers = {
                "api_key": arize_api_key,
                "space_id": space_id
            }
        
        # Configure OpenTelemetry
        tracer_provider = TracerProvider()
        trace.set_tracer_provider(tracer_provider)
        
        # Set up OTLP exporter
        if phoenix_local:
            span_exporter = OTLPSpanExporter(endpoint=endpoint)
        else:
            span_exporter = OTLPSpanExporter(
                endpoint=f"{endpoint}/v1/traces",
                headers=headers
            )
        
        span_processor = BatchSpanProcessor(span_exporter)
        tracer_provider.add_span_processor(span_processor)
        
        # Instrument OpenAI
        OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)
        
        print("✅ Arize Phoenix observability initialized successfully!")
        
        return {
            "enabled": True,
            "local": phoenix_local,
            "endpoint": endpoint
        }
        
    except Exception as e:
        print(f"❌ Failed to initialize Arize observability: {str(e)}")
        return None


def add_trace_attributes(attributes: dict):
    """Add custom attributes to the current trace"""
    try:
        span = trace.get_current_span()
        if span:
            for key, value in attributes.items():
                span.set_attribute(key, str(value))
    except Exception as e:
        print(f"Warning: Could not add trace attributes: {e}")


def create_span(name: str, attributes: dict = None):
    """Create a custom span for tracking operations"""
    try:
        tracer = trace.get_tracer(__name__)
        span = tracer.start_span(name)
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, str(value))
        return span
    except Exception as e:
        print(f"Warning: Could not create span: {e}")
        return None


