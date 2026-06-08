"""Scoring logic for Message House Catalyst Canvas diagnostics."""

from __future__ import annotations

from statistics import mean

from .models import AuditResult, MessagePillar
from .validation import validate_weights


READINESS_WEIGHTS = {
    "core_alignment": 0.22,
    "audience_relevance": 0.24,
    "evidence_strength": 0.24,
    "differentiation": 0.16,
    "governance_readiness": 0.14,
}

validate_weights(READINESS_WEIGHTS)


def round_score(value: float) -> float:
    return round(value, 3)


def readiness_score(pillar: MessagePillar) -> float:
    return mean([
        pillar.core_alignment,
        pillar.audience_relevance,
        pillar.evidence_strength,
        pillar.differentiation,
        pillar.governance_readiness,
    ])


def weighted_readiness(pillar: MessagePillar) -> float:
    return sum(getattr(pillar, key) * weight for key, weight in READINESS_WEIGHTS.items())


def proof_gap(pillar: MessagePillar) -> float:
    pillar_importance = mean([
        pillar.core_alignment,
        pillar.audience_relevance,
        pillar.differentiation,
    ])
    return max(0.0, pillar_importance - pillar.evidence_strength)


def message_drift_risk(pillar: MessagePillar) -> float:
    structural_gap = max(0.0, pillar.core_alignment - pillar.governance_readiness)
    evidence_gap = proof_gap(pillar)
    return max(structural_gap, evidence_gap, pillar.ethical_risk * 0.6)


def governance_reasons(pillar: MessagePillar, gap: float, drift: float) -> list[str]:
    reasons: list[str] = []

    if gap >= 0.20:
        reasons.append("major proof gap")
    elif gap >= 0.10:
        reasons.append("moderate proof gap")

    if pillar.evidence_strength < 0.65:
        reasons.append("weak evidence strength")

    if pillar.governance_readiness < 0.65:
        reasons.append("weak governance readiness")

    if pillar.core_alignment < 0.65:
        reasons.append("weak core message alignment")

    if pillar.audience_relevance < 0.65:
        reasons.append("weak audience relevance")

    if pillar.differentiation < 0.65:
        reasons.append("weak differentiation")

    if drift >= 0.20:
        reasons.append("message drift risk")

    if pillar.ethical_risk >= 0.50:
        reasons.append("ethical risk review")

    if pillar.status in {"review", "revise"}:
        reasons.append(f"status marked {pillar.status}")

    return reasons


def review_priority(pillar: MessagePillar, gap: float, drift: float) -> str:
    if pillar.status == "archive":
        return "archive review"
    if pillar.status == "revise" or pillar.ethical_risk >= 0.70 or gap >= 0.25:
        return "high"
    if pillar.status == "review" or gap >= 0.10 or drift >= 0.20 or pillar.evidence_strength < 0.65:
        return "medium"
    return "standard"


def score_pillar(pillar: MessagePillar) -> AuditResult:
    gap = proof_gap(pillar)
    drift = message_drift_risk(pillar)
    reasons = governance_reasons(pillar, gap, drift)

    return AuditResult(
        pillar=pillar.pillar,
        description=pillar.description,
        owner=pillar.owner,
        status=pillar.status,
        review_date=pillar.review_date,
        core_alignment=round_score(pillar.core_alignment),
        audience_relevance=round_score(pillar.audience_relevance),
        evidence_strength=round_score(pillar.evidence_strength),
        differentiation=round_score(pillar.differentiation),
        governance_readiness=round_score(pillar.governance_readiness),
        ethical_risk=round_score(pillar.ethical_risk),
        readiness_score=round_score(readiness_score(pillar)),
        weighted_readiness=round_score(weighted_readiness(pillar)),
        proof_gap=round_score(gap),
        message_drift_risk=round_score(drift),
        review_priority=review_priority(pillar, gap, drift),
        governance_reasons="; ".join(reasons) if reasons else "no immediate governance issue",
    )
