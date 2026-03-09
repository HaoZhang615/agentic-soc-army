"""Mock Sentinel / Defender enrichment functions.

Each function doubles as an Azure AI Agent *FunctionTool* callable AND
returns realistic canned data when SOC_WORKSHOP_OFFLINE=1.
"""

from __future__ import annotations

import json
from pathlib import Path

_DATA = Path(__file__).resolve().parents[3] / "data"


def _load(name: str) -> dict:
    return json.loads((_DATA / name).read_text(encoding="utf-8"))


# ── Alert details ───────────────────────────────────────────────────────────
def get_alert_details(alert_id: str) -> str:
    """Return full details for a Sentinel alert by ID.

    Args:
        alert_id: The unique alert identifier (e.g. 'ALERT-2025-001').

    Returns:
        JSON string with alert metadata, entities, tactics, and raw log excerpt.
    """
    alerts = _load("alerts.json")
    for a in alerts:
        if a["alert_id"] == alert_id:
            return json.dumps(a, indent=2)
    return json.dumps({"error": f"Alert {alert_id} not found"})


# ── Related alerts ──────────────────────────────────────────────────────────
def get_related_alerts(entity_value: str) -> str:
    """Find alerts that share an entity (IP, user, host, hash) with the given value.

    Args:
        entity_value: The observable value to pivot on (e.g. '10.0.14.88').

    Returns:
        JSON array of matching alerts.
    """
    alerts = _load("alerts.json")
    hits = []
    for a in alerts:
        for e in a.get("entities", []):
            if e["value"] == entity_value:
                hits.append({"alert_id": a["alert_id"], "title": a["title"], "severity": a["severity"]})
                break
    return json.dumps(hits, indent=2)


# ── Sign-in logs ────────────────────────────────────────────────────────────
def get_sign_in_logs(user_principal: str) -> str:
    """Retrieve recent sign-in activity for a user principal name.

    Args:
        user_principal: UPN such as 'jdoe@contoso.com'.

    Returns:
        JSON array of sign-in events with IP, location, device, risk level.
    """
    logs = _load("signin_logs.json")
    hits = [l for l in logs if l["user_principal"] == user_principal]
    return json.dumps(hits, indent=2)


# ── Entity risk score ──────────────────────────────────────────────────────
def get_entity_risk(entity_type: str, entity_value: str) -> str:
    """Look up the risk score for an entity.

    Args:
        entity_type: One of 'ip', 'user', 'host', 'filehash', 'url', 'domain'.
        entity_value: The observable value.

    Returns:
        JSON object with risk_score (0-100), risk_level, and tags.
    """
    risk_db = _load("entity_risk.json")
    key = f"{entity_type}:{entity_value}"
    if key in risk_db:
        return json.dumps(risk_db[key])
    return json.dumps({"entity_type": entity_type, "value": entity_value, "risk_score": 25, "risk_level": "Low", "tags": []})
