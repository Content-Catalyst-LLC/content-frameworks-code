"""Data models for the BCG Matrix Catalyst Canvas module."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class PortfolioItem:
    item: str
    portfolio_area: str
    description: str
    growth_score: float
    relative_share_score: float
    evidence_strength: float
    strategic_fit: float
    maintenance_burden: float
    claim_strength: float
    owner: str
    status: str
    review_date: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "PortfolioItem":
        numeric_fields = {
            key: float(row[key])
            for key in [
                "growth_score",
                "relative_share_score",
                "evidence_strength",
                "strategic_fit",
                "maintenance_burden",
                "claim_strength",
            ]
        }

        return cls(
            item=row["item"],
            portfolio_area=row["portfolio_area"],
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
    portfolio_area: str
    description: str
    owner: str
    status: str
    review_date: str
    growth_score: float
    relative_share_score: float
    evidence_strength: float
    strategic_fit: float
    maintenance_burden: float
    claim_strength: float
    quadrant: str
    evidence_gap: float
    portfolio_priority: float
    review_priority: str
    recommended_action: str
    governance_reasons: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
