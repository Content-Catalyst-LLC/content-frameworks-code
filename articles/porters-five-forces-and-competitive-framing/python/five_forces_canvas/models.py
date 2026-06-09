"""Data models for the Porter Five Forces Catalyst Canvas module."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ForceRecord:
    force: str
    market_boundary: str
    description: str
    intensity: float
    evidence_strength: float
    uncertainty: float
    strategic_relevance: float
    actionability: float
    claim_strength: float
    owner: str
    status: str
    review_date: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "ForceRecord":
        numeric_fields = {
            key: float(row[key])
            for key in [
                "intensity",
                "evidence_strength",
                "uncertainty",
                "strategic_relevance",
                "actionability",
                "claim_strength",
            ]
        }

        return cls(
            force=row["force"],
            market_boundary=row["market_boundary"],
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
    force: str
    market_boundary: str
    description: str
    owner: str
    status: str
    review_date: str
    intensity: float
    evidence_strength: float
    uncertainty: float
    strategic_relevance: float
    actionability: float
    claim_strength: float
    readiness_score: float
    weighted_priority: float
    evidence_gap: float
    governance_priority: float
    review_priority: str
    governance_reasons: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
