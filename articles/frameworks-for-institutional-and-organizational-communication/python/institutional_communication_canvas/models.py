"""Data models for the Institutional Communication Catalyst Canvas module."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class CommunicationItem:
    item: str
    communication_type: str
    description: str
    clarity: float
    authority_coverage: float
    evidence_strength: float
    stakeholder_visibility: float
    feedback_quality: float
    channel_fit: float
    cultural_alignment: float
    governance_coverage: float
    ambiguity: float
    claim_strength: float
    owner: str
    status: str
    review_date: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "CommunicationItem":
        numeric_fields = {
            key: float(row[key])
            for key in [
                "clarity",
                "authority_coverage",
                "evidence_strength",
                "stakeholder_visibility",
                "feedback_quality",
                "channel_fit",
                "cultural_alignment",
                "governance_coverage",
                "ambiguity",
                "claim_strength",
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
    clarity: float
    authority_coverage: float
    evidence_strength: float
    stakeholder_visibility: float
    feedback_quality: float
    channel_fit: float
    cultural_alignment: float
    governance_coverage: float
    ambiguity: float
    claim_strength: float
    quality_score: float
    evidence_gap: float
    trust_risk: float
    review_priority_score: float
    review_priority: str
    governance_reasons: str
    recommended_action: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
