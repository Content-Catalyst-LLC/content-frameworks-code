"""Data models for the Message House Catalyst Canvas module."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class MessagePillar:
    pillar: str
    description: str
    core_alignment: float
    audience_relevance: float
    evidence_strength: float
    differentiation: float
    governance_readiness: float
    ethical_risk: float
    owner: str
    status: str
    review_date: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "MessagePillar":
        numeric_fields = {
            key: float(row[key])
            for key in [
                "core_alignment",
                "audience_relevance",
                "evidence_strength",
                "differentiation",
                "governance_readiness",
                "ethical_risk",
            ]
        }

        return cls(
            pillar=row["pillar"],
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
    pillar: str
    description: str
    owner: str
    status: str
    review_date: str
    core_alignment: float
    audience_relevance: float
    evidence_strength: float
    differentiation: float
    governance_readiness: float
    ethical_risk: float
    readiness_score: float
    weighted_readiness: float
    proof_gap: float
    message_drift_risk: float
    review_priority: str
    governance_reasons: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
