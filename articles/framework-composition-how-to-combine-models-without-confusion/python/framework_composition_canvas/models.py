"""Data models for the Framework Composition Catalyst Canvas module."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class FrameworkCompositionItem:
    item: str
    composition_type: str
    description: str
    purpose_fit: float
    role_clarity: float
    boundary_clarity: float
    sequence_clarity: float
    translation_quality: float
    evidence_alignment: float
    governance_readiness: float
    audience_burden: float
    conflict_risk: float
    owner: str
    status: str
    review_date: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "FrameworkCompositionItem":
        numeric_fields = {
            key: float(row[key])
            for key in [
                "purpose_fit",
                "role_clarity",
                "boundary_clarity",
                "sequence_clarity",
                "translation_quality",
                "evidence_alignment",
                "governance_readiness",
                "audience_burden",
                "conflict_risk",
            ]
        }

        return cls(
            item=row["item"],
            composition_type=row["composition_type"],
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
    composition_type: str
    description: str
    owner: str
    status: str
    review_date: str
    purpose_fit: float
    role_clarity: float
    boundary_clarity: float
    sequence_clarity: float
    translation_quality: float
    evidence_alignment: float
    governance_readiness: float
    audience_burden: float
    conflict_risk: float
    quality_score: float
    confusion_risk: float
    review_priority_score: float
    review_priority: str
    governance_reasons: str
    recommended_action: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
