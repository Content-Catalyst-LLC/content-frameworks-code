"""Data models for the Strategic Foresight Catalyst Canvas module."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ForesightItem:
    item: str
    foresight_type: str
    description: str
    driver_clarity: float
    uncertainty_logic: float
    scenario_logic: float
    assumption_transparency: float
    option_relevance: float
    indicator_coverage: float
    evidence_strength: float
    stakeholder_visibility: float
    importance: float
    uncertainty: float
    owner: str
    status: str
    review_date: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "ForesightItem":
        numeric_fields = {
            key: float(row[key])
            for key in [
                "driver_clarity",
                "uncertainty_logic",
                "scenario_logic",
                "assumption_transparency",
                "option_relevance",
                "indicator_coverage",
                "evidence_strength",
                "stakeholder_visibility",
                "importance",
                "uncertainty",
            ]
        }

        return cls(
            item=row["item"],
            foresight_type=row["foresight_type"],
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
    foresight_type: str
    description: str
    owner: str
    status: str
    review_date: str
    driver_clarity: float
    uncertainty_logic: float
    scenario_logic: float
    assumption_transparency: float
    option_relevance: float
    indicator_coverage: float
    evidence_strength: float
    stakeholder_visibility: float
    importance: float
    uncertainty: float
    quality_score: float
    assumption_risk: float
    review_priority_score: float
    review_priority: str
    governance_reasons: str
    recommended_action: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
