"""Data models for the Persona Frameworks Catalyst Canvas module."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class PersonaRecord:
    persona: str
    segment: str
    description: str
    content_pathway: str
    evidence_strength: float
    specificity: float
    content_fit: float
    segment_alignment: float
    governance_readiness: float
    stereotype_risk: float
    exclusion_risk: float
    weak_evidence_risk: float
    overgeneralization_risk: float
    owner: str
    status: str
    review_date: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "PersonaRecord":
        numeric_fields = {
            key: float(row[key])
            for key in [
                "evidence_strength",
                "specificity",
                "content_fit",
                "segment_alignment",
                "governance_readiness",
                "stereotype_risk",
                "exclusion_risk",
                "weak_evidence_risk",
                "overgeneralization_risk",
            ]
        }

        return cls(
            persona=row["persona"],
            segment=row["segment"],
            description=row["description"],
            content_pathway=row["content_pathway"],
            owner=row["owner"],
            status=row["status"],
            review_date=row["review_date"],
            **numeric_fields,
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class AuditResult:
    persona: str
    segment: str
    description: str
    content_pathway: str
    owner: str
    status: str
    review_date: str
    evidence_strength: float
    specificity: float
    content_fit: float
    segment_alignment: float
    governance_readiness: float
    stereotype_risk: float
    exclusion_risk: float
    weak_evidence_risk: float
    overgeneralization_risk: float
    risk_score: float
    readiness_score: float
    weighted_readiness: float
    revision_pressure: float
    review_priority: str
    governance_reasons: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
