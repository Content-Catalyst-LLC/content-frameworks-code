"""Data models for the Content Framework Value Catalyst Canvas module."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ContentFrameworkValueItem:
    item: str
    framework_type: str
    description: str
    coherence: float
    reuse_readiness: float
    evidence_visibility: float
    audience_pathway_clarity: float
    governance_maturity: float
    platform_readiness: float
    learning_support: float
    ai_readiness: float
    fragmentation_risk: float
    context_preservation: float
    maintenance_burden: float
    owner: str
    status: str
    review_date: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "ContentFrameworkValueItem":
        numeric_fields = {
            key: float(row[key])
            for key in [
                "coherence",
                "reuse_readiness",
                "evidence_visibility",
                "audience_pathway_clarity",
                "governance_maturity",
                "platform_readiness",
                "learning_support",
                "ai_readiness",
                "fragmentation_risk",
                "context_preservation",
                "maintenance_burden",
            ]
        }

        return cls(
            item=row["item"],
            framework_type=row["framework_type"],
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
    framework_type: str
    description: str
    owner: str
    status: str
    review_date: str
    coherence: float
    reuse_readiness: float
    evidence_visibility: float
    audience_pathway_clarity: float
    governance_maturity: float
    platform_readiness: float
    learning_support: float
    ai_readiness: float
    fragmentation_risk: float
    context_preservation: float
    maintenance_burden: float
    value_score: float
    framework_risk: float
    review_priority_score: float
    review_priority: str
    governance_reasons: str
    recommended_action: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
