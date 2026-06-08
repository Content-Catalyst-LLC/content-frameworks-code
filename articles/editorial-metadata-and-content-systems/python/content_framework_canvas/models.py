"""Data models for generic Content Frameworks Canvas readiness audits."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class CanvasRecord:
    record_id: str
    article_slug: str
    article_title: str
    module_kind: str
    canvas_dimension: str
    description: str
    content_value: float
    audience_value: float
    evidence_strength: float
    repository_support: float
    governance_need: float
    ethical_risk: float
    owner: str
    status: str
    review_date: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "CanvasRecord":
        numeric = {
            key: float(row[key])
            for key in [
                "content_value",
                "audience_value",
                "evidence_strength",
                "repository_support",
                "governance_need",
                "ethical_risk",
            ]
        }
        return cls(
            record_id=row["record_id"],
            article_slug=row["article_slug"],
            article_title=row["article_title"],
            module_kind=row["module_kind"],
            canvas_dimension=row["canvas_dimension"],
            description=row["description"],
            owner=row["owner"],
            status=row["status"],
            review_date=row["review_date"],
            **numeric,
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class AuditResult:
    record_id: str
    article_slug: str
    article_title: str
    module_kind: str
    canvas_dimension: str
    description: str
    owner: str
    status: str
    review_date: str
    content_score: float
    audience_score: float
    evidence_score: float
    repository_score: float
    governance_pressure: float
    ethical_risk: float
    readiness_score: float
    review_priority: str
    governance_reasons: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
