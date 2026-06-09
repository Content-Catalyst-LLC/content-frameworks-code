"""Data models for the Technology and Scientific Communication Catalyst Canvas module."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class TechScienceItem:
    item: str
    communication_type: str
    description: str
    claim_clarity: float
    evidence_strength: float
    method_transparency: float
    uncertainty_disclosure: float
    audience_fit: float
    risk_visibility: float
    stakeholder_visibility: float
    promotional_intensity: float
    claim_breadth: float
    owner: str
    status: str
    review_date: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "TechScienceItem":
        numeric_fields = {
            key: float(row[key])
            for key in [
                "claim_clarity",
                "evidence_strength",
                "method_transparency",
                "uncertainty_disclosure",
                "audience_fit",
                "risk_visibility",
                "stakeholder_visibility",
                "promotional_intensity",
                "claim_breadth",
            ]
        }

        return cls(
            item=row["item"],
            communication_type=row["communication_type"],
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
    communication_type: str
    description: str
    owner: str
    status: str
    review_date: str
    claim_clarity: float
    evidence_strength: float
    method_transparency: float
    uncertainty_disclosure: float
    audience_fit: float
    risk_visibility: float
    stakeholder_visibility: float
    promotional_intensity: float
    claim_breadth: float
    quality_score: float
    evidence_gap: float
    hype_risk: float
    review_priority_score: float
    review_priority: str
    governance_reasons: str
    recommended_action: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
