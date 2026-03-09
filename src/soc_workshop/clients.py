"""Shared client construction — single source of truth for auth & project wiring."""

from __future__ import annotations

import logging
import os
from functools import lru_cache

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

from soc_workshop.settings import Settings, get_settings


@lru_cache(maxsize=1)
def _credential() -> DefaultAzureCredential:
    return DefaultAzureCredential()


def get_project_client(settings: Settings | None = None) -> AIProjectClient:
    """Build an AIProjectClient from settings (defaults to env)."""
    s = settings or get_settings()
    return AIProjectClient(
        endpoint=s.project_endpoint,
        credential=_credential(),
    )


def get_agents_client(settings: Settings | None = None):
    """Convenience — returns project_client.agents (AgentsOperations)."""
    return get_project_client(settings).agents


def get_openai_client(settings: Settings | None = None):
    """Convenience — returns project_client.get_openai_client() for Responses API."""
    return get_project_client(settings).get_openai_client()


_tracing_configured = False


def configure_tracing(settings: Settings | None = None) -> bool:
    """Wire up OpenTelemetry → Azure Monitor for agent trace export.

    Call once at process/notebook startup, *before* any agent runs.
    Returns True if tracing was enabled, False if skipped (no connection string).

    Three things are required for full Foundry portal tracing:
      1. AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING env var — feature gate
      2. configure_azure_monitor()  — sets up the OTel exporter to App Insights
      3. AIProjectInstrumentor().instrument() — instruments the SDK to emit spans
    """
    global _tracing_configured  # noqa: PLW0603
    if _tracing_configured:
        return True

    s = settings or get_settings()
    log = logging.getLogger(__name__)

    # ── Step 1: Resolve Application Insights connection string ────────────
    # Prefer the explicit env-var; fall back to auto-discovery from project.
    conn_str = s.appinsights_conn_str
    if not conn_str:
        try:
            client = get_project_client(s)
            conn_str = client.telemetry.get_application_insights_connection_string()
        except Exception:
            log.debug(
                "Could not retrieve App Insights connection string from project; tracing disabled."
            )
            return False

    if not conn_str:
        return False

    # ── Step 2: Set feature-gate env vars BEFORE instrumenting ───────────
    # azure-ai-projects v2.0.0b4 AIProjectInstrumentor.instrument() silently
    # exits unless this env var is set to "true".
    os.environ["AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING"] = "true"

    # Enable content recording so prompt/response text appears in traces.
    os.environ.setdefault("AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED", "true")
    os.environ.setdefault("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "true")

    # Tell azure-core to bridge its internal tracing to OpenTelemetry.
    from azure.core.settings import settings as core_settings
    core_settings.tracing_implementation = "opentelemetry"

    # ── Step 3: Configure Azure Monitor exporter ─────────────────────────
    from azure.monitor.opentelemetry import configure_azure_monitor

    configure_azure_monitor(connection_string=conn_str)

    # ── Step 4: Instrument the AI SDK to emit OpenTelemetry spans ────────
    # AIProjectInstrumentor instruments both the Agents API and the Responses
    # API (via _ResponsesInstrumentorPreview internally).  This is what makes
    # Conversation ID, Trace ID, Duration, Tokens (In/Out) show up in the
    # Foundry portal Traces tab.
    from azure.ai.projects.telemetry import AIProjectInstrumentor

    AIProjectInstrumentor().instrument(
        enable_content_recording=True,
    )

    _tracing_configured = True
    log.info("Azure Monitor tracing enabled (exporter + SDK instrumentation).")
    return True
