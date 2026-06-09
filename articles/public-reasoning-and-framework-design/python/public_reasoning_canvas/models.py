"""Data models for the Public Reasoning Catalyst Canvas module."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class PublicReasoningItem:
    item: str
    reasoning_type: str
    description: str
    claim_clarity: float
    evidence_visibility: float
    value_transparency: float
    tradeoff_clarity: float
    stakeholder_inclusion: float
    uncertainty_disclosure: float
    participation_fit: float
    accountability: float
    transparency: float
    owner: str
    status: str
    review_date: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "PublicReasoningItem":
        numeric_fields = {
            key: float(row[key])
            for key in [
                "claim_clarity",
                "evidence_visibility",
                "value_transparency",
                "tradeoff_clarity",
                "stakeholder_inclusion",
                "uncertainty_disclosure",
                "participation_fit",
                "accountability",
                "transparency",
            ]
        }

        return cls(
            item=row["item"],
            reasoning_type=row["reasoning_type"],
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
    reasoning_type: str
    description: str
    owner: str
    status: str
    review_date: str
    claim_clarity: float
    evidence_visibility: float
    value_transparency: float
    tradeoff_clarity: float
    stakeholder_inclusion: float
    uncertainty_disclosure: float
    participation_fit: float
    accountability: float
    transparency: float
    quality_score: float
    legitimacy_risk: float
    review_priority_score: float
    review_priority: str
    governance_reasons: str
    recommended_action: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
