"""Data models for the Systems Explanation Catalyst Canvas module."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class SystemsExplanationItem:
    item: str
    explanation_type: str
    description: str
    boundary_clarity: float
    actor_coverage: float
    relationship_clarity: float
    feedback_visibility: float
    delay_visibility: float
    stock_flow_clarity: float
    stakeholder_visibility: float
    evidence_strength: float
    leverage_readiness: float
    owner: str
    status: str
    review_date: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "SystemsExplanationItem":
        numeric_fields = {
            key: float(row[key])
            for key in [
                "boundary_clarity",
                "actor_coverage",
                "relationship_clarity",
                "feedback_visibility",
                "delay_visibility",
                "stock_flow_clarity",
                "stakeholder_visibility",
                "evidence_strength",
                "leverage_readiness",
            ]
        }

        return cls(
            item=row["item"],
            explanation_type=row["explanation_type"],
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
    explanation_type: str
    description: str
    owner: str
    status: str
    review_date: str
    boundary_clarity: float
    actor_coverage: float
    relationship_clarity: float
    feedback_visibility: float
    delay_visibility: float
    stock_flow_clarity: float
    stakeholder_visibility: float
    evidence_strength: float
    leverage_readiness: float
    quality_score: float
    systems_ambiguity: float
    review_priority_score: float
    review_priority: str
    governance_reasons: str
    recommended_action: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
