"""Scoring logic for Positioning Frameworks Catalyst Canvas diagnostics."""

from __future__ import annotations

from statistics import mean

from .models import AuditResult, PositioningRecord
from .validation import validate_weights


READINESS_WEIGHTS = {
    "category_clarity": 0.18,
    "audience_relevance": 0.20,
    "differentiation": 0.16,
    "evidence_strength": 0.20,
    "governance_readiness": 0.14,
    "boundary_clarity": 0.12,
}

validate_weights(READINESS_WEIGHTS)


def round_score(value: float) -> float:
    return round(value, 3)


def readiness_score(record: PositioningRecord) -> float:
    return mean([
        record.category_clarity,
        record.audience_relevance,
        record.differentiation,
        record.evidence_strength,
        record.governance_readiness,
        record.boundary_clarity,
    ])


def weighted_readiness(record: PositioningRecord) -> float:
    return sum(getattr(record, key) * weight for key, weight in READINESS_WEIGHTS.items())


def evidence_gap(record: PositioningRecord) -> float:
    claim_strength = mean([
        record.category_clarity,
        record.audience_relevance,
        record.differentiation,
    ])
    return max(0.0, claim_strength - record.evidence_strength)


def governance_reasons(record: PositioningRecord, gap: float) -> list[str]:
    reasons: list[str] = []

    if record.category_clarity < 0.65:
        reasons.append("weak category clarity")
    if record.audience_relevance < 0.65:
        reasons.append("weak audience relevance")
    if record.differentiation < 0.65:
        reasons.append("weak differentiation")
    if record.evidence_strength < 0.65:
        reasons.append("weak evidence strength")
    if record.boundary_clarity < 0.65:
        reasons.append("weak boundary clarity")
    if record.governance_readiness < 0.65:
        reasons.append("weak governance readiness")
    if gap >= 0.15:
        reasons.append("evidence gap")
    if record.drift_risk >= 0.60:
        reasons.append("positioning drift risk")
    if record.ethical_risk >= 0.50:
        reasons.append("ethical risk review")
    if record.status in {"review", "revise"}:
        reasons.append(f"status marked {record.status}")

    return reasons


def review_priority(record: PositioningRecord, gap: float) -> str:
    if record.status == "archive":
        return "archive review"
    if record.status == "revise" or record.ethical_risk >= 0.70:
        return "high"
    if (
        record.status == "review"
        or gap >= 0.15
        or record.drift_risk >= 0.60
        or record.boundary_clarity < 0.65
        or record.governance_readiness < 0.65
        or record.evidence_strength < 0.65
    ):
        return "medium"
    return "standard"


def score_record(record: PositioningRecord) -> AuditResult:
    gap = evidence_gap(record)
    reasons = governance_reasons(record, gap)

    return AuditResult(
        idea=record.idea,
        description=record.description,
        category_frame=record.category_frame,
        audience_pathway=record.audience_pathway,
        owner=record.owner,
        status=record.status,
        review_date=record.review_date,
        category_clarity=round_score(record.category_clarity),
        audience_relevance=round_score(record.audience_relevance),
        differentiation=round_score(record.differentiation),
        evidence_strength=round_score(record.evidence_strength),
        governance_readiness=round_score(record.governance_readiness),
        boundary_clarity=round_score(record.boundary_clarity),
        ethical_risk=round_score(record.ethical_risk),
        drift_risk=round_score(record.drift_risk),
        readiness_score=round_score(readiness_score(record)),
        weighted_readiness=round_score(weighted_readiness(record)),
        evidence_gap=round_score(gap),
        review_priority=review_priority(record, gap),
        governance_reasons="; ".join(reasons) if reasons else "no immediate governance issue",
    )
