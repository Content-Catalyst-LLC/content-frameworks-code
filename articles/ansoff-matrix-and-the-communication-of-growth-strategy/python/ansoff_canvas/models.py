"""Data models for the Ansoff Matrix Catalyst Canvas module."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class GrowthOption:
    option: str
    growth_path: str
    market_status: str
    product_status: str
    description: str
    strategic_fit: float
    evidence_strength: float
    feasibility: float
    capability_readiness: float
    expected_value: float
    market_familiarity: float
    product_familiarity: float
    uncertainty: float
    claim_strength: float
    owner: str
    status: str
    review_date: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "GrowthOption":
        numeric_fields = {
            key: float(row[key])
            for key in [
                "strategic_fit",
                "evidence_strength",
                "feasibility",
                "capability_readiness",
                "expected_value",
                "market_familiarity",
                "product_familiarity",
                "uncertainty",
                "claim_strength",
            ]
        }

        return cls(
            option=row["option"],
            growth_path=row["growth_path"],
            market_status=row["market_status"],
            product_status=row["product_status"],
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
    option: str
    growth_path: str
    market_status: str
    product_status: str
    description: str
    owner: str
    status: str
    review_date: str
    strategic_fit: float
    evidence_strength: float
    feasibility: float
    capability_readiness: float
    expected_value: float
    market_familiarity: float
    product_familiarity: float
    uncertainty: float
    claim_strength: float
    readiness_score: float
    risk_score: float
    evidence_gap: float
    growth_quality: float
    governance_priority: float
    review_priority: str
    governance_reasons: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
