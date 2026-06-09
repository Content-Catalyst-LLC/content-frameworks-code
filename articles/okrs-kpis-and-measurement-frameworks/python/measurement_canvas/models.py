"""Data models for the Measurement Frameworks Catalyst Canvas module."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class MeasurementItem:
    item: str
    measurement_type: str
    description: str
    strategic_relevance: float
    validity: float
    reliability: float
    actionability: float
    timeliness: float
    evidence_strength: float
    gaming_risk: float
    reporting_burden: float
    ambiguity: float
    claim_strength: float
    owner: str
    status: str
    review_date: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "MeasurementItem":
        numeric_fields = {
            key: float(row[key])
            for key in [
                "strategic_relevance",
                "validity",
                "reliability",
                "actionability",
                "timeliness",
                "evidence_strength",
                "gaming_risk",
                "reporting_burden",
                "ambiguity",
                "claim_strength",
            ]
        }

        return cls(
            item=row["item"],
            measurement_type=row["measurement_type"],
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
    measurement_type: str
    description: str
    owner: str
    status: str
    review_date: str
    strategic_relevance: float
    validity: float
    reliability: float
    actionability: float
    timeliness: float
    evidence_strength: float
    gaming_risk: float
    reporting_burden: float
    ambiguity: float
    claim_strength: float
    quality_score: float
    measurement_risk: float
    evidence_gap: float
    governance_priority: float
    review_priority: str
    governance_reasons: str
    recommended_action: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
