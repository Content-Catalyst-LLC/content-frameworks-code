"""Data models for the STP Catalyst Canvas module."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class SegmentProfile:
    segment: str
    description: str
    primary_job: str
    content_pathway: str
    need_intensity: float
    strategic_fit: float
    reachability: float
    evidence_fit: float
    ethical_responsibility: float
    category_clarity: float
    audience_relevance: float
    differentiation: float
    credibility: float
    stereotype_risk: float
    exclusion_risk: float
    owner: str
    status: str
    review_date: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "SegmentProfile":
        numeric_fields = {
            key: float(row[key])
            for key in [
                "need_intensity",
                "strategic_fit",
                "reachability",
                "evidence_fit",
                "ethical_responsibility",
                "category_clarity",
                "audience_relevance",
                "differentiation",
                "credibility",
                "stereotype_risk",
                "exclusion_risk",
            ]
        }

        return cls(
            segment=row["segment"],
            description=row["description"],
            primary_job=row["primary_job"],
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
    segment: str
    description: str
    primary_job: str
    content_pathway: str
    owner: str
    status: str
    review_date: str
    target_score: float
    weighted_target_score: float
    positioning_score: float
    positioning_gap: float
    ethical_risk_score: float
    governance_score: float
    target_classification: str
    ethical_review_flag: str
    review_priority: str
    governance_reasons: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
