"""Scoring logic for PESTLE Analysis Catalyst Canvas diagnostics."""

from __future__ import annotations

from statistics import mean

from .models import AuditResult, PESTLEFactor
from .validation import validate_weights


PRIORITY_WEIGHTS = {
    "impact": 0.24,
    "urgency": 0.18,
    "evidence_strength": 0.16,
    "uncertainty": 0.12,
    "strategic_relevance": 0.20,
    "actionability": 0.10,
}

validate_weights(PRIORITY_WEIGHTS)


def round_score(value: float) -> float:
    return round(value, 3)


def readiness_score(factor: PESTLEFactor) -> float:
    return mean([
        factor.impact,
        factor.urgency,
        factor.evidence_strength,
        factor.strategic_relevance,
        factor.actionability,
    ])


def weighted_priority(factor: PESTLEFactor) -> float:
    return sum(getattr(factor, key) * weight for key, weight in PRIORITY_WEIGHTS.items())


def evidence_gap(factor: PESTLEFactor) -> float:
    return max(0.0, factor.claim_strength - factor.evidence_strength)


def monitoring_priority(factor: PESTLEFactor) -> float:
    return factor.impact * factor.uncertainty


def governance_priority(factor: PESTLEFactor) -> float:
    return min(1.0, weighted_priority(factor) + evidence_gap(factor) * 0.40)


def governance_reasons(factor: PESTLEFactor, gap: float, monitor: float, governance_score: float) -> list[str]:
    reasons: list[str] = []

    if factor.evidence_strength < 0.60:
        reasons.append("weak evidence strength")
    if factor.strategic_relevance < 0.60:
        reasons.append("weak strategic relevance")
    if factor.actionability < 0.60:
        reasons.append("low actionability")
    if factor.uncertainty >= 0.60:
        reasons.append("high uncertainty")
    if gap >= 0.15:
        reasons.append("evidence gap")
    if monitor >= 0.50:
        reasons.append("monitoring needed")
    if governance_score >= 0.75:
        reasons.append("high governance priority")
    if factor.status in {"review", "revise"}:
        reasons.append(f"status marked {factor.status}")
    if len(factor.description.split()) < 7:
        reasons.append("description may be too vague")

    return reasons


def review_priority(factor: PESTLEFactor, gap: float, monitor: float, governance_score: float) -> str:
    if factor.status == "archive":
        return "archive review"
    if factor.status == "revise" or gap >= 0.30:
        return "high"
    if governance_score >= 0.75 or monitor >= 0.50 or gap >= 0.15 or factor.status == "review":
        return "medium"
    return "standard"


def score_factor(factor: PESTLEFactor) -> AuditResult:
    gap = evidence_gap(factor)
    monitor = monitoring_priority(factor)
    governance_score = governance_priority(factor)
    reasons = governance_reasons(factor, gap, monitor, governance_score)

    return AuditResult(
        factor=factor.factor,
        category=factor.category,
        signal_type=factor.signal_type,
        description=factor.description,
        owner=factor.owner,
        status=factor.status,
        review_date=factor.review_date,
        impact=round_score(factor.impact),
        urgency=round_score(factor.urgency),
        evidence_strength=round_score(factor.evidence_strength),
        uncertainty=round_score(factor.uncertainty),
        strategic_relevance=round_score(factor.strategic_relevance),
        actionability=round_score(factor.actionability),
        claim_strength=round_score(factor.claim_strength),
        readiness_score=round_score(readiness_score(factor)),
        weighted_priority=round_score(weighted_priority(factor)),
        evidence_gap=round_score(gap),
        monitoring_priority=round_score(monitor),
        governance_priority=round_score(governance_score),
        review_priority=review_priority(factor, gap, monitor, governance_score),
        governance_reasons="; ".join(reasons) if reasons else "no immediate governance issue",
    )
