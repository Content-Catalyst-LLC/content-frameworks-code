"""Data models for the PESTLE Analysis Catalyst Canvas module."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class PESTLEFactor:
    factor: str
    category: str
    signal_type: str
    description: str
    impact: float
    urgency: float
    evidence_strength: float
    uncertainty: float
    strategic_relevance: float
    actionability: float
    claim_strength: float
    owner: str
    status: str
    review_date: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "PESTLEFactor":
        numeric_fields = {
            key: float(row[key])
            for key in [
                "impact",
                "urgency",
                "evidence_strength",
                "uncertainty",
                "strategic_relevance",
                "actionability",
                "claim_strength",
            ]
        }

        return cls(
            factor=row["factor"],
            category=row["category"],
            signal_type=row["signal_type"],
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
    factor: str
    category: str
    signal_type: str
    description: str
    owner: str
    status: str
    review_date: str
    impact: float
    urgency: float
    evidence_strength: float
    uncertainty: float
    strategic_relevance: float
    actionability: float
    claim_strength: float
    readiness_score: float
    weighted_priority: float
    evidence_gap: float
    monitoring_priority: float
    governance_priority: float
    review_priority: str
    governance_reasons: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
