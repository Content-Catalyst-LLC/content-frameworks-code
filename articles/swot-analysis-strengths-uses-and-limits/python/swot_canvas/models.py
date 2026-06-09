"""Data models for the SWOT Analysis Catalyst Canvas module."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class SWOTItem:
    item: str
    quadrant: str
    orientation: str
    description: str
    impact: float
    confidence: float
    urgency: float
    feasibility: float
    strategic_fit: float
    evidence_strength: float
    claim_strength: float
    owner: str
    status: str
    review_date: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "SWOTItem":
        numeric_fields = {
            key: float(row[key])
            for key in [
                "impact",
                "confidence",
                "urgency",
                "feasibility",
                "strategic_fit",
                "evidence_strength",
                "claim_strength",
            ]
        }

        return cls(
            item=row["item"],
            quadrant=row["quadrant"],
            orientation=row["orientation"],
            description=row["description"],
            owner=row["owner"],
            status=row["status"],
            review_date=row["review_date"],
            **numeric_fields,
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class AuditResult:
    item: str
    quadrant: str
    orientation: str
    description: str
    owner: str
    status: str
    review_date: str
    impact: float
    confidence: float
    urgency: float
    feasibility: float
    strategic_fit: float
    evidence_strength: float
    claim_strength: float
    priority_score: float
    weighted_priority: float
    evidence_gap: float
    governance_priority: float
    review_priority: str
    governance_reasons: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
