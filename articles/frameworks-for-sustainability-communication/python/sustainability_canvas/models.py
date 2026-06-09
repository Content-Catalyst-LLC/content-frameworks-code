"""Data models for the Sustainability Communication Catalyst Canvas module."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class SustainabilityClaim:
    claim: str
    claim_type: str
    description: str
    claim_specificity: float
    boundary_clarity: float
    evidence_strength: float
    materiality_relevance: float
    stakeholder_visibility: float
    accountability_coverage: float
    uncertainty_disclosure: float
    promotional_intensity: float
    claim_strength: float
    owner: str
    status: str
    review_date: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "SustainabilityClaim":
        numeric_fields = {
            key: float(row[key])
            for key in [
                "claim_specificity",
                "boundary_clarity",
                "evidence_strength",
                "materiality_relevance",
                "stakeholder_visibility",
                "accountability_coverage",
                "uncertainty_disclosure",
                "promotional_intensity",
                "claim_strength",
            ]
        }

        return cls(
            claim=row["claim"],
            claim_type=row["claim_type"],
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
    claim: str
    claim_type: str
    description: str
    owner: str
    status: str
    review_date: str
    claim_specificity: float
    boundary_clarity: float
    evidence_strength: float
    materiality_relevance: float
    stakeholder_visibility: float
    accountability_coverage: float
    uncertainty_disclosure: float
    promotional_intensity: float
    claim_strength: float
    quality_score: float
    evidence_gap: float
    greenwashing_risk: float
    review_priority_score: float
    review_priority: str
    governance_reasons: str
    recommended_action: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
