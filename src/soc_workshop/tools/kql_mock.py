"""Mock KQL query executor for workshop demonstrations.

Simulates running KQL queries against a Log Analytics workspace
and returns realistic result sets from canned data.
"""

from __future__ import annotations

import json
from pathlib import Path

_DATA = Path(__file__).resolve().parents[3] / "data"


def run_kql_query(query: str) -> str:
    """Execute a KQL query against the SOC Log Analytics workspace.

    Args:
        query: A KQL query string.  The mock matches on keywords in the
               query (e.g. 'SigninLogs', 'SecurityAlert', 'DeviceProcessEvents')
               and returns pre-built result sets.

    Returns:
        JSON string with a 'columns' and 'rows' structure, or an error.
    """
    q = query.lower()

    if "signinlogs" in q or "signin" in q:
        data = json.loads((_DATA / "signin_logs.json").read_text(encoding="utf-8"))
        return json.dumps({"table": "SigninLogs", "row_count": len(data), "rows": data}, indent=2)

    if "securityalert" in q or "alert" in q:
        data = json.loads((_DATA / "alerts.json").read_text(encoding="utf-8"))
        return json.dumps({"table": "SecurityAlert", "row_count": len(data), "rows": data}, indent=2)

    if "deviceprocessevents" in q or "process" in q:
        data = json.loads((_DATA / "process_events.json").read_text(encoding="utf-8"))
        return json.dumps({"table": "DeviceProcessEvents", "row_count": len(data), "rows": data}, indent=2)

    if "devicenetworkevents" in q or "network" in q:
        data = json.loads((_DATA / "network_events.json").read_text(encoding="utf-8"))
        return json.dumps({"table": "DeviceNetworkEvents", "row_count": len(data), "rows": data}, indent=2)

    return json.dumps({"error": "No matching mock data for this query", "query": query})
