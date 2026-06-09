"""Scoring logic for systems explanation governance."""

from __future__ import annotations

from statistics import mean

from .models import AuditResult, SystemsExplanationItem


def round_score(value: float) -> float:
    return round(value, 3)


def quality_score(item: SystemsExplanationItem) -> float:
    return mean([
        item.boundary_clarity,
        item.actor_coverage,
        item.relationship_clarity,
        item.feedback_visibility,
        item.delay_visibility,
        item.stock_flow_clarity,
        item.stakeholder_visibility,
        item.evidence_strength,
        item.leverage_readiness,
    ])


def systems_ambiguity(item: SystemsExplanationItem) -> float:
    return min(
        1.0,
        (1.0 - item.boundary_clarity) * 0.30
        + (1.0 - item.relationship_clarity) * 0.30
        + (1.0 - item.evidence_strength) * 0.25
        + (1.0 - item.feedback_visibility) * 0.15,
    )


def review_priority_score(item: SystemsExplanationItem) -> float:
    return min(
        1.0,
        systems_ambiguity(item) * 0.40
        + (1.0 - item.leverage_readiness) * 0.25
        + (1.0 - item.stakeholder_visibility) * 0.20
        + (1.0 - item.delay_visibility) * 0.15,
    )


def governance_reasons(item: SystemsExplanationItem, ambiguity: float, priority: float) -> list[str]:
    reasons: list[str] = []

    if item.boundary_clarity < 0.60:
        reasons.append("weak boundary clarity")
    if item.actor_coverage < 0.60:
        reasons.append("weak actor coverage")
    if item.relationship_clarity < 0.60:
        reasons.append("weak relationship clarity")
    if item.feedback_visibility < 0.60:
        reasons.append("weak feedback visibility")
    if item.delay_visibility < 0.60:
        reasons.append("weak delay visibility")
    if item.stock_flow_clarity < 0.60:
        reasons.append("weak stock-flow clarity")
    if item.stakeholder_visibility < 0.60:
        reasons.append("weak stakeholder visibility")
    if item.evidence_strength < 0.60:
        reasons.append("weak evidence strength")
    if item.leverage_readiness < 0.60:
        reasons.append("weak leverage readiness")
    if ambiguity >= 0.45:
        reasons.append("high systems ambiguity")
    if priority >= 0.45:
        reasons.append("review priority threshold reached")
    if item.status in {"review", "revise"}:
        reasons.append(f"status marked {item.status}")
    if len(item.description.split()) < 7:
        reasons.append("description may be too vague")

    return reasons


def recommended_action(item: SystemsExplanationItem, ambiguity: float, priority: float) -> str:
    if item.status == "archive":
        return "Review whether this systems explanation item should be archived or retained for historical context."
    if item.status == "revise" or priority >= 0.45:
        return "Revise this systems explanation before publication and strengthen boundaries actors relationships feedback delays evidence stakeholder visibility and leverage logic."
    if ambiguity >= 0.45 or item.status == "review":
        return "Review boundary clarity relationship logic feedback visibility delay visibility evidence and stakeholder implications during the next governance cycle."
    return "Keep active and review during the next systems explanation governance cycle."


def review_priority(item: SystemsExplanationItem, ambiguity: float, priority: float) -> str:
    if item.status == "archive":
        return "archive review"
    if item.status == "revise" or priority >= 0.45:
        return "high"
    if ambiguity >= 0.45 or item.status == "review":
        return "medium"
    return "standard"


def score_item(item: SystemsExplanationItem) -> AuditResult:
    ambiguity = systems_ambiguity(item)
    priority = review_priority_score(item)
    reasons = governance_reasons(item, ambiguity, priority)

    return AuditResult(
        item=item.item,
        explanation_type=item.explanation_type,
        description=item.description,
        owner=item.owner,
        status=item.status,
        review_date=item.review_date,
        boundary_clarity=round_score(item.boundary_clarity),
        actor_coverage=round_score(item.actor_coverage),
        relationship_clarity=round_score(item.relationship_clarity),
        feedback_visibility=round_score(item.feedback_visibility),
        delay_visibility=round_score(item.delay_visibility),
        stock_flow_clarity=round_score(item.stock_flow_clarity),
        stakeholder_visibility=round_score(item.stakeholder_visibility),
        evidence_strength=round_score(item.evidence_strength),
        leverage_readiness=round_score(item.leverage_readiness),
        quality_score=round_score(quality_score(item)),
        systems_ambiguity=round_score(ambiguity),
        review_priority_score=round_score(priority),
        review_priority=review_priority(item, ambiguity, priority),
        governance_reasons="; ".join(reasons) if reasons else "no immediate governance issue",
        recommended_action=recommended_action(item, ambiguity, priority),
    )
