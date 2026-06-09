"""Data models for the Framework Limits Catalyst Canvas module."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class FrameworkLimitItem:
    item: str
    framework_type: str
    description: str
    clarity: float
    fit: float
    evidence_alignment: float
    assumption_transparency: float
    governance_readiness: float
    oversimplification_risk: float
    false_precision_risk: float
    context_loss: float
    audience_burden: float
    value_opacity: float
    owner: str
    status: str
    review_date: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "FrameworkLimitItem":
        numeric_fields = {
            key: float(row[key])
            for key in [
                "clarity",
                "fit",
                "evidence_alignment",
                "assumption_transparency",
                "governance_readiness",
                "oversimplification_risk",
                "false_precision_risk",
                "context_loss",
                "audience_burden",
                "value_opacity",
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
    clarity: float
    fit: float
    evidence_alignment: float
    assumption_transparency: float
    governance_readiness: float
    oversimplification_risk: float
    false_precision_risk: float
    context_loss: float
    audience_burden: float
    value_opacity: float
    usefulness_score: float
    distortion_risk: float
    review_priority_score: float
    review_priority: str
    governance_reasons: str
    recommended_action: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
