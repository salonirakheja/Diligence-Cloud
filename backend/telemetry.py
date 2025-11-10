"""
Telemetry initialization for Diligence Cloud backend.

Sets up OpenTelemetry exporters that forward spans to Arize Phoenix using the
OTLP/HTTP exporter and instruments the OpenAI SDK via OpenInference so that
LLM calls show up in the Phoenix trace view.
"""

from __future__ import annotations

import os
from typing import Optional

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

try:
    from openinference.instrumentation.openai import OpenAIInstrumentor
except ImportError:  # pragma: no cover - optional dependency
    OpenAIInstrumentor = None  # type: ignore


_TRACER_PROVIDER: Optional[TracerProvider] = None


def _resolve_traces_endpoint() -> Optional[str]:
    """Determine the OTLP endpoint Phoenix expects traces on."""
    explicit = os.getenv("PHOENIX_TRACES_ENDPOINT")
    if explicit:
        return explicit.rstrip("/")

    # Hosted Phoenix exposes a REST base at .../v1 and traces at .../v1/traces
    api_url = os.getenv("PHOENIX_API_URL")
    if api_url:
        api_url = api_url.rstrip("/")
        if api_url.endswith("/traces"):
            return api_url
        if api_url.endswith("/v1"):
            return f"{api_url}/traces"
        return f"{api_url}/v1/traces"

    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if otlp_endpoint:
        return otlp_endpoint.rstrip("/")

    return None


def init_tracing() -> Optional[TracerProvider]:
    """
    Configure OpenTelemetry to emit traces to Phoenix.

    Returns the configured tracer provider if telemetry is enabled, otherwise None.
    """
    global _TRACER_PROVIDER

    if _TRACER_PROVIDER is not None:
        return _TRACER_PROVIDER

    api_key = os.getenv("PHOENIX_API_KEY")
    endpoint = _resolve_traces_endpoint()

    if not api_key or not endpoint:
        print(
            "[telemetry] Phoenix tracing disabled (missing PHOENIX_API_KEY or endpoint)."
        )
        return None

    project_name = os.getenv("PHOENIX_PROJECT", "diligence-cloud")
    service_name = os.getenv("PHOENIX_SERVICE_NAME", "diligence-cloud-backend")

    try:
        resource = Resource.create(
            {
                "service.name": service_name,
                "phoenix.project_name": project_name,
            }
        )

        tracer_provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(
            endpoint=endpoint,
            headers={"Authorization": f"Bearer {api_key}"},
        )
        tracer_provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(tracer_provider)

        if OpenAIInstrumentor:
            OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)
        else:
            print(
                "[telemetry] openinference-instrumentation-openai not installed; "
                "LLM spans will not be captured."
            )

        _TRACER_PROVIDER = tracer_provider
        print("[telemetry] Phoenix tracing initialized.")
        return tracer_provider
    except Exception as exc:  # pragma: no cover - best-effort telemetry init
        print(f"[telemetry] Failed to initialize Phoenix tracing: {exc}")
        return None


