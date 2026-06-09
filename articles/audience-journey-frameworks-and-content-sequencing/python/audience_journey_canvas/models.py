"""Data models for the Audience Journey Catalyst Canvas module."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class JourneyStage:
    stage: str
    audience_need: str
    journey_type: str
    stage_clarity: float
    content_coverage: float
    transition_quality: float
    evidence_readiness: float
    governance_readiness: float
    required_links: int
    available_links: int
    persona_fit: float
    staleness_risk: float
    owner: str
    status: str
    review_date: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "JourneyStage":
        numeric_fields = {
            key: float(row[key])
            for key in [
                "stage_clarity",
                "content_coverage",
                "transition_quality",
                "evidence_readiness",
                "governance_readiness",
                "persona_fit",
                "staleness_risk",
            ]
        }

        return cls(
            stage=row["stage"],
            audience_need=row["audience_need"],
            journey_type=row["journey_type"],
            required_links=int(row["required_links"]),
            available_links=int(row["available_links"]),
            owner=row["owner"],
            status=row["status"],
            review_date=row["review_date"],
            **numeric_fields,
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class AuditResult:
    stage: str
    audience_need: str
    journey_type: str
    owner: str
    status: str
    review_date: str
    stage_clarity: float
    content_coverage: float
    transition_quality: float
    evidence_readiness: float
    governance_readiness: float
    required_links: int
    available_links: int
    link_gap: int
    persona_fit: float
    persona_mismatch: float
    staleness_risk: float
    journey_risk: float
    readiness_score: float
    weighted_readiness: float
    review_priority: str
    governance_reasons: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
