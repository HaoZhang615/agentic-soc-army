"""SOC Workshop mock tools — offline-capable enrichment functions."""

from soc_workshop.tools.sentinel_mock import (
    get_alert_details,
    get_related_alerts,
    get_sign_in_logs,
    get_entity_risk,
)
from soc_workshop.tools.kql_mock import run_kql_query
from soc_workshop.tools.search_mock import search_threat_intel, search_playbooks

__all__ = [
    "get_alert_details",
    "get_related_alerts",
    "get_sign_in_logs",
    "get_entity_risk",
    "run_kql_query",
    "search_threat_intel",
    "search_playbooks",
]
