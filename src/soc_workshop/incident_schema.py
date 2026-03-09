"""Dataclasses for SOC incident artefacts used across all notebooks."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Entity:
    """Observable entity extracted from an alert (IP, user, host, hash, URL, …)."""

    entity_type: str          # e.g. "ip", "user", "host", "filehash", "url", "domain"
    value: str
    risk_score: Optional[int] = None  # 0-100
    tags: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        return f"{self.entity_type}={self.value}"


@dataclass
class Alert:
    """A single security alert as it arrives from Sentinel / Defender / SIEM."""

    alert_id: str
    title: str
    severity: str             # "High", "Medium", "Low", "Informational"
    description: str
    timestamp: str            # ISO-8601
    source: str               # "Microsoft Sentinel", "Defender for Endpoint", etc.
    tactics: list[str] = field(default_factory=list)       # MITRE ATT&CK tactics
    techniques: list[str] = field(default_factory=list)    # MITRE ATT&CK technique IDs
    entities: list[Entity] = field(default_factory=list)
    raw_json: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict) -> "Alert":
        entities = [Entity(**e) for e in d.pop("entities", [])]
        return cls(**d, entities=entities)


@dataclass
class EvidenceItem:
    """A single piece of evidence collected during investigation."""

    source: str       # tool / agent that produced it
    category: str     # "network", "identity", "endpoint", "threat_intel"
    summary: str
    raw: dict = field(default_factory=dict, repr=False)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class TimelineEvent:
    """One entry in a chronological incident timeline."""

    timestamp: str
    event: str
    source: str
    severity: str = "info"  # info, warning, critical


@dataclass
class InvestigationRecord:
    """Root container for an entire investigation — passed between notebooks."""

    incident_id: str
    title: str
    alerts: list[Alert] = field(default_factory=list)
    entities: list[Entity] = field(default_factory=list)
    evidence: list[EvidenceItem] = field(default_factory=list)
    timeline: list[TimelineEvent] = field(default_factory=list)
    hypothesis: str = ""
    verdict: str = ""           # "True Positive", "False Positive", "Benign"
    confidence: float = 0.0     # 0.0 – 1.0
    recommended_actions: list[str] = field(default_factory=list)
    thread_id: Optional[str] = None   # Foundry thread id for conversation continuity
    agent_ids: list[str] = field(default_factory=list)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(asdict(self), indent=indent, default=str)

    @classmethod
    def from_json(cls, raw: str) -> "InvestigationRecord":
        d = json.loads(raw)
        d["alerts"] = [Alert.from_dict(a) for a in d.get("alerts", [])]
        d["entities"] = [Entity(**e) for e in d.get("entities", [])]
        d["evidence"] = [EvidenceItem(**e) for e in d.get("evidence", [])]
        d["timeline"] = [TimelineEvent(**t) for t in d.get("timeline", [])]
        return cls(**d)
