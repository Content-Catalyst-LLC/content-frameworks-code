"""Data models for the Positioning Frameworks Catalyst Canvas module."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class PositioningRecord:
    idea: str
    description: str
    category_frame: str
    audience_pathway: str
    category_clarity: float
    audience_relevance: float
    differentiation: float
    evidence_strength: float
    governance_readiness: float
    boundary_clarity: float
    ethical_risk: float
    drift_risk: float
    owner: str
    status: str
    review_date: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "PositioningRecord":
        numeric_fields = {
            key: float(row[key])
            for key in [
                "category_clarity",
                "audience_relevance",
                "differentiation",
                "evidence_strength",
                "governance_readiness",
                "boundary_clarity",
                "ethical_risk",
                "drift_risk",
            ]
        }

        return cls(
            idea=row["idea"],
            description=row["description"],
            category_frame=row["category_frame"],
            audience_pathway=row["audience_pathway"],
            owner=row["owner"],
            status=row["status"],
            review_date=row["review_date"],
            **numeric_fields,
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class AuditResult:
    idea: str
    description: str
    category_frame: str
    audience_pathway: str
    owner: str
    status: str
    review_date: str
    category_clarity: float
    audience_relevance: float
    differentiation: float
    evidence_strength: float
    governance_readiness: float
    boundary_clarity: float
    ethical_risk: float
    drift_risk: float
    readiness_score: float
    weighted_readiness: float
    evidence_gap: float
    review_priority: str
    governance_reasons: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
