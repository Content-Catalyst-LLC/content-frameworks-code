"""Data models for the AI-Assisted Framework Design Catalyst Canvas module."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class AIAssistedFrameworkItem:
    item: str
    item_type: str
    description: str
    conceptual_clarity: float
    evidence_grounding: float
    metadata_consistency: float
    human_review_strength: float
    bias_review: float
    governance_maturity: float
    platform_readiness: float
    drift_control: float
    unsupported_claim_risk: float
    generic_structure_risk: float
    output_validation: float
    audience_impact: float
    owner: str
    status: str
    review_date: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "AIAssistedFrameworkItem":
        numeric_fields = {
            key: float(row[key])
            for key in [
                "conceptual_clarity",
                "evidence_grounding",
                "metadata_consistency",
                "human_review_strength",
                "bias_review",
                "governance_maturity",
                "platform_readiness",
                "drift_control",
                "unsupported_claim_risk",
                "generic_structure_risk",
                "output_validation",
                "audience_impact",
            ]
        }

        return cls(
            item=row["item"],
            item_type=row["item_type"],
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
    item_type: str
    description: str
    owner: str
    status: str
    review_date: str
    conceptual_clarity: float
    evidence_grounding: float
    metadata_consistency: float
    human_review_strength: float
    bias_review: float
    governance_maturity: float
    platform_readiness: float
    drift_control: float
    unsupported_claim_risk: float
    generic_structure_risk: float
    output_validation: float
    audience_impact: float
    readiness_score: float
    ai_framework_risk: float
    governance_priority_score: float
    governance_priority: str
    governance_reasons: str
    recommended_action: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
