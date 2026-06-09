"""Scoring logic for public reasoning and framework design governance."""

from __future__ import annotations

from statistics import mean

from .models import AuditResult, PublicReasoningItem


def round_score(value: float) -> float:
    return round(value, 3)


def quality_score(item: PublicReasoningItem) -> float:
    return mean([
        item.claim_clarity,
        item.evidence_visibility,
        item.value_transparency,
        item.tradeoff_clarity,
        item.stakeholder_inclusion,
        item.uncertainty_disclosure,
        item.participation_fit,
        item.accountability,
        item.transparency,
    ])


def legitimacy_risk(item: PublicReasoningItem) -> float:
    return min(
        1.0,
        (1.0 - item.participation_fit) * 0.25
        + (1.0 - item.stakeholder_inclusion) * 0.25
        + (1.0 - item.transparency) * 0.25
        + (1.0 - item.accountability) * 0.25,
    )


def review_priority_score(item: PublicReasoningItem) -> float:
    return min(
        1.0,
        (1.0 - quality_score(item)) * 0.50
        + legitimacy_risk(item) * 0.50,
    )


def governance_reasons(item: PublicReasoningItem, risk: float, priority: float) -> list[str]:
    reasons: list[str] = []

    if item.claim_clarity < 0.60:
        reasons.append("weak claim clarity")
    if item.evidence_visibility < 0.60:
        reasons.append("weak evidence visibility")
    if item.value_transparency < 0.60:
        reasons.append("weak value transparency")
    if item.tradeoff_clarity < 0.60:
        reasons.append("weak tradeoff clarity")
    if item.stakeholder_inclusion < 0.60:
        reasons.append("weak stakeholder inclusion")
    if item.uncertainty_disclosure < 0.60:
        reasons.append("weak uncertainty disclosure")
    if item.participation_fit < 0.60:
        reasons.append("weak participation fit")
    if item.accountability < 0.60:
        reasons.append("weak accountability")
    if item.transparency < 0.60:
        reasons.append("weak transparency")
    if risk >= 0.40:
        reasons.append("high legitimacy risk")
    if priority >= 0.45:
        reasons.append("review priority threshold reached")
    if item.status in {"review", "revise"}:
        reasons.append(f"status marked {item.status}")
    if len(item.description.split()) < 7:
        reasons.append("description may be too vague")

    return reasons


def recommended_action(item: PublicReasoningItem, risk: float, priority: float) -> str:
    if item.status == "archive":
        return "Review whether this public reasoning item should be archived or retained for historical context."
    if item.status == "revise" or priority >= 0.45:
        return "Revise this public reasoning framework before publication and strengthen evidence visibility values tradeoffs stakeholder inclusion participation fit accountability and transparency."
    if risk >= 0.40 or item.status == "review":
        return "Review legitimacy risk participation promises stakeholder inclusion values tradeoffs and accountability during the next governance cycle."
    return "Keep active and review during the next public reasoning governance cycle."


def review_priority(item: PublicReasoningItem, risk: float, priority: float) -> str:
    if item.status == "archive":
        return "archive review"
    if item.status == "revise" or priority >= 0.45:
        return "high"
    if risk >= 0.40 or item.status == "review":
        return "medium"
    return "standard"


def score_item(item: PublicReasoningItem) -> AuditResult:
    risk = legitimacy_risk(item)
    priority = review_priority_score(item)
    reasons = governance_reasons(item, risk, priority)

    return AuditResult(
        item=item.item,
        reasoning_type=item.reasoning_type,
        description=item.description,
        owner=item.owner,
        status=item.status,
        review_date=item.review_date,
        claim_clarity=round_score(item.claim_clarity),
        evidence_visibility=round_score(item.evidence_visibility),
        value_transparency=round_score(item.value_transparency),
        tradeoff_clarity=round_score(item.tradeoff_clarity),
        stakeholder_inclusion=round_score(item.stakeholder_inclusion),
        uncertainty_disclosure=round_score(item.uncertainty_disclosure),
        participation_fit=round_score(item.participation_fit),
        accountability=round_score(item.accountability),
        transparency=round_score(item.transparency),
        quality_score=round_score(quality_score(item)),
        legitimacy_risk=round_score(risk),
        review_priority_score=round_score(priority),
        review_priority=review_priority(item, risk, priority),
        governance_reasons="; ".join(reasons) if reasons else "no immediate governance issue",
        recommended_action=recommended_action(item, risk, priority),
    )
