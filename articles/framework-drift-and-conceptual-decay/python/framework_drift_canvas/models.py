"""Data models for the Framework Drift Catalyst Canvas module."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class FrameworkDriftItem:
    item: str
    item_type: str
    description: str
    definition_consistency: float
    boundary_clarity: float
    evidence_currency: float
    metadata_consistency: float
    link_health: float
    governance_maturity: float
    reuse_pressure: float
    stale_evidence_risk: float
    dependency_complexity: float
    platform_alignment: float
    audience_impact: float
    owner: str
    status: str
    review_date: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "FrameworkDriftItem":
        numeric_fields = {
            key: float(row[key])
            for key in [
                "definition_consistency",
                "boundary_clarity",
                "evidence_currency",
                "metadata_consistency",
                "link_health",
                "governance_maturity",
                "reuse_pressure",
                "stale_evidence_risk",
                "dependency_complexity",
                "platform_alignment",
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
    definition_consistency: float
    boundary_clarity: float
    evidence_currency: float
    metadata_consistency: float
    link_health: float
    governance_maturity: float
    reuse_pressure: float
    stale_evidence_risk: float
    dependency_complexity: float
    platform_alignment: float
    audience_impact: float
    conceptual_integrity: float
    drift_risk: float
    repair_priority_score: float
    repair_priority: str
    governance_reasons: str
    recommended_action: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
