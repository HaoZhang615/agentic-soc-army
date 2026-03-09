"""Centralised settings loader — validates env vars per notebook requirement."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# ── locate .env relative to repo root ──────────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_REPO_ROOT / ".env", override=True)

# Also add src/ to sys.path so notebooks can `import soc_workshop` directly
_SRC = str(_REPO_ROOT / "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)


@dataclass(frozen=True)
class Settings:
    """Typed bag of environment variables used across notebooks."""

    # ── always required ────────────────────────────────────────────────────
    project_endpoint: str = field(default_factory=lambda: os.environ["AZURE_AI_PROJECT_ENDPOINT"])
    model_deployment: str = field(default_factory=lambda: os.environ.get("MODEL_DEPLOYMENT_NAME", "gpt-4.1"))

    # ── optional per-notebook ──────────────────────────────────────────────
    search_connection_name: Optional[str] = field(
        default_factory=lambda: os.environ.get("AZURE_AI_SEARCH_CONNECTION_NAME")
    )
    search_index_name: Optional[str] = field(
        default_factory=lambda: os.environ.get("AZURE_AI_SEARCH_INDEX_NAME")
    )
    mcp_server_url: Optional[str] = field(default_factory=lambda: os.environ.get("MCP_SERVER_URL"))
    mcp_server_label: Optional[str] = field(
        default_factory=lambda: os.environ.get("MCP_SERVER_LABEL", "sentinel-mcp")
    )
    appinsights_conn_str: Optional[str] = field(
        default_factory=lambda: os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    )
    existing_conversation_id: Optional[str] = field(
        default_factory=lambda: os.environ.get("EXISTING_CONVERSATION_ID")
    )

    # ── offline / mock mode ────────────────────────────────────────────────
    offline: bool = field(
        default_factory=lambda: os.environ.get("SOC_WORKSHOP_OFFLINE", "").lower() in ("1", "true", "yes")
    )


def get_settings() -> Settings:
    """Return a frozen Settings instance, or raise with helpful message."""
    try:
        return Settings()
    except KeyError as exc:
        raise EnvironmentError(
            f"Missing required env var {exc}. "
            f"Copy .env.example → .env and fill in values, or run `azd up`."
        ) from exc


def require(settings: Settings, *attrs: str) -> None:
    """Raise early if any of the listed optional settings are None."""
    missing = [a for a in attrs if getattr(settings, a) is None]
    if missing:
        raise EnvironmentError(
            f"This notebook requires the following env vars: {', '.join(missing)}. "
            f"See .env.example for details."
        )
