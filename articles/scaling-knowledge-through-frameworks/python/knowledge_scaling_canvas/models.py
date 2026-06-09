"""Data models for the Knowledge Scaling Catalyst Canvas module."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class KnowledgeScalingItem:
    item: str
    asset_type: str
    description: str
    modularity: float
    taxonomy_quality: float
    metadata_completeness: float
    link_coverage: float
    evidence_alignment: float
    reuse_readiness: float
    governance_maturity: float
    platform_readiness: float
    audience_pathway_clarity: float
    dependency_complexity: float
    owner: str
    status: str
    review_date: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "KnowledgeScalingItem":
        numeric_fields = {
            key: float(row[key])
            for key in [
                "modularity",
                "taxonomy_quality",
                "metadata_completeness",
                "link_coverage",
                "evidence_alignment",
                "reuse_readiness",
                "governance_maturity",
                "platform_readiness",
                "audience_pathway_clarity",
                "dependency_complexity",
            ]
        }

        return cls(
            item=row["item"],
            asset_type=row["asset_type"],
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
    asset_type: str
    description: str
    owner: str
    status: str
    review_date: str
    modularity: float
    taxonomy_quality: float
    metadata_completeness: float
    link_coverage: float
    evidence_alignment: float
    reuse_readiness: float
    governance_maturity: float
    platform_readiness: float
    audience_pathway_clarity: float
    dependency_complexity: float
    scalability_score: float
    maintenance_risk: float
    review_priority_score: float
    review_priority: str
    governance_reasons: str
    recommended_action: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
