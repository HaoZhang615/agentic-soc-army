"""Shared client construction — single source of truth for auth & project wiring."""

from __future__ import annotations

import logging
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
    """
    global _tracing_configured  # noqa: PLW0603
    if _tracing_configured:
        return True

    s = settings or get_settings()

    # Prefer the connection string from the Foundry project connection
    # (auto-discovered via the SDK); fall back to the env-var override.
    conn_str = s.appinsights_conn_str
    if not conn_str:
        try:
            client = get_project_client(s)
            conn_str = client.telemetry.get_application_insights_connection_string()
        except Exception:
            logging.getLogger(__name__).debug(
                "Could not retrieve App Insights connection string from project; tracing disabled."
            )
            return False

    if not conn_str:
        return False

    from azure.monitor.opentelemetry import configure_azure_monitor

    configure_azure_monitor(connection_string=conn_str)
    _tracing_configured = True
    logging.getLogger(__name__).info("Azure Monitor tracing enabled.")
    return True
