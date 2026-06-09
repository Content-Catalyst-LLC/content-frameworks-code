# Data models for the Logic Model Catalyst Canvas module.

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class LogicModelElement:
    element: str
    model_layer: str
    description: str
    evidence_strength: float
    assumption_importance: float
    assumption_evidence: float
    measurement_coverage: float
    outcome_clarity: float
    claim_strength: float
    owner: str
    status: str
    review_date: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "LogicModelElement":
        numeric = {
            key: float(row[key])
            for key in [
                "evidence_strength",
                "assumption_importance",
                "assumption_evidence",
                "measurement_coverage",
                "outcome_clarity",
                "claim_strength",
            ]
        }
        return cls(
            element=row["element"],
            model_layer=row["model_layer"],
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
    element: str
    model_layer: str
    description: str
    owner: str
    status: str
    review_date: str
    evidence_strength: float
    assumption_importance: float
    assumption_evidence: float
    measurement_coverage: float
    outcome_clarity: float
    claim_strength: float
    assumption_risk: float
    evidence_gap: float
    pathway_quality: float
    governance_priority: float
    review_priority: str
    governance_reasons: str
    recommended_action: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
