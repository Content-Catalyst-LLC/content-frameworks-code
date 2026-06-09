"""Data models for the Framework Governance Catalyst Canvas module."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class FrameworkGovernanceItem:
    item: str
    item_type: str
    description: str
    ownership_clarity: float
    review_cycle_strength: float
    metadata_completeness: float
    evidence_status: float
    link_health: float
    taxonomy_alignment: float
    platform_readiness: float
    stale_evidence_risk: float
    dependency_complexity: float
    audience_impact: float
    owner: str
    status: str
    review_date: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "FrameworkGovernanceItem":
        numeric_fields = {
            key: float(row[key])
            for key in [
                "ownership_clarity",
                "review_cycle_strength",
                "metadata_completeness",
                "evidence_status",
                "link_health",
                "taxonomy_alignment",
                "platform_readiness",
                "stale_evidence_risk",
                "dependency_complexity",
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
    ownership_clarity: float
    review_cycle_strength: float
    metadata_completeness: float
    evidence_status: float
    link_health: float
    taxonomy_alignment: float
    platform_readiness: float
    stale_evidence_risk: float
    dependency_complexity: float
    audience_impact: float
    governance_maturity: float
    maintenance_risk: float
    review_priority_score: float
    review_priority: str
    governance_reasons: str
    recommended_action: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
