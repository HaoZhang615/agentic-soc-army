"""Mock Azure AI Search tool — returns canned threat intel & playbook chunks.

In live mode these would hit an Azure AI Search index; here we return
pre-built results so the notebook runs without infrastructure.
"""

from __future__ import annotations

import json
from pathlib import Path

_DATA = Path(__file__).resolve().parents[3] / "data"


def search_threat_intel(query: str, top_k: int = 3) -> str:
    """Search the threat intelligence knowledge base.

    Args:
        query: Natural-language search query (e.g. 'cobalt strike beacon indicators').
        top_k: Maximum number of results to return.

    Returns:
        JSON array of matching threat intel documents with title, content, source, and score.
    """
    docs = json.loads((_DATA / "threat_intel_chunks.json").read_text(encoding="utf-8"))
    # Simple keyword overlap scoring
    q_words = set(query.lower().split())
    scored = []
    for doc in docs:
        text_words = set(doc["content"].lower().split())
        overlap = len(q_words & text_words)
        if overlap > 0:
            scored.append({**doc, "relevance_score": round(overlap / max(len(q_words), 1), 2)})
    scored.sort(key=lambda d: d["relevance_score"], reverse=True)
    return json.dumps(scored[:top_k], indent=2)


def search_playbooks(query: str, top_k: int = 2) -> str:
    """Search SOC response playbooks.

    Args:
        query: Description of the incident type (e.g. 'phishing email with credential harvest').
        top_k: Maximum number of playbook matches to return.

    Returns:
        JSON array of matching playbook excerpts with title, steps, and severity guidance.
    """
    docs = json.loads((_DATA / "playbook_chunks.json").read_text(encoding="utf-8"))
    q_words = set(query.lower().split())
    scored = []
    for doc in docs:
        text_words = set(doc["content"].lower().split())
        overlap = len(q_words & text_words)
        if overlap > 0:
            scored.append({**doc, "relevance_score": round(overlap / max(len(q_words), 1), 2)})
    scored.sort(key=lambda d: d["relevance_score"], reverse=True)
    return json.dumps(scored[:top_k], indent=2)
