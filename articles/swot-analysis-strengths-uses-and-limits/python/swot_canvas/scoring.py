"""Scoring logic for SWOT Analysis Catalyst Canvas diagnostics."""

from __future__ import annotations

from statistics import mean

from .models import AuditResult, SWOTItem
from .validation import validate_weights


PRIORITY_WEIGHTS = {
    "impact": 0.26,
    "confidence": 0.20,
    "urgency": 0.18,
    "feasibility": 0.16,
    "strategic_fit": 0.20,
}

validate_weights(PRIORITY_WEIGHTS)


def round_score(value: float) -> float:
    return round(value, 3)


def priority_score(item: SWOTItem) -> float:
    return mean([
        item.impact,
        item.confidence,
        item.urgency,
        item.feasibility,
        item.strategic_fit,
    ])


def weighted_priority(item: SWOTItem) -> float:
    return sum(getattr(item, key) * weight for key, weight in PRIORITY_WEIGHTS.items())


def evidence_gap(item: SWOTItem) -> float:
    return max(0.0, item.claim_strength - item.evidence_strength)


def governance_priority(item: SWOTItem) -> float:
    return min(1.0, weighted_priority(item) + evidence_gap(item) * 0.50)


def governance_reasons(item: SWOTItem, gap: float, governance_score: float) -> list[str]:
    reasons: list[str] = []

    if item.confidence < 0.60:
        reasons.append("low confidence")
    if item.feasibility < 0.60:
        reasons.append("low feasibility")
    if item.evidence_strength < 0.60:
        reasons.append("weak evidence strength")
    if gap >= 0.15:
        reasons.append("evidence gap")
    if governance_score >= 0.75:
        reasons.append("high governance priority")
    if item.status in {"review", "revise"}:
        reasons.append(f"status marked {item.status}")
    if len(item.description.split()) < 6:
        reasons.append("description may be too vague")

    return reasons


def review_priority(item: SWOTItem, gap: float, governance_score: float) -> str:
    if item.status == "archive":
        return "archive review"
    if item.status == "revise" or gap >= 0.30:
        return "high"
    if governance_score >= 0.75 or gap >= 0.15 or item.status == "review":
        return "medium"
    return "standard"


def score_item(item: SWOTItem) -> AuditResult:
    gap = evidence_gap(item)
    governance_score = governance_priority(item)
    reasons = governance_reasons(item, gap, governance_score)

    return AuditResult(
        item=item.item,
        quadrant=item.quadrant,
        orientation=item.orientation,
        description=item.description,
        owner=item.owner,
        status=item.status,
        review_date=item.review_date,
        impact=round_score(item.impact),
        confidence=round_score(item.confidence),
        urgency=round_score(item.urgency),
        feasibility=round_score(item.feasibility),
        strategic_fit=round_score(item.strategic_fit),
        evidence_strength=round_score(item.evidence_strength),
        claim_strength=round_score(item.claim_strength),
        priority_score=round_score(priority_score(item)),
        weighted_priority=round_score(weighted_priority(item)),
        evidence_gap=round_score(gap),
        governance_priority=round_score(governance_score),
        review_priority=review_priority(item, gap, governance_score),
        governance_reasons="; ".join(reasons) if reasons else "no immediate governance issue",
    )
