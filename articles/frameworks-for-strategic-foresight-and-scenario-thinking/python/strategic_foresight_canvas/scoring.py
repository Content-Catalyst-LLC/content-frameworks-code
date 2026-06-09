"""Scoring logic for strategic foresight and scenario thinking governance."""

from __future__ import annotations

from statistics import mean

from .models import AuditResult, ForesightItem


def round_score(value: float) -> float:
    return round(value, 3)


def quality_score(item: ForesightItem) -> float:
    return mean([
        item.driver_clarity,
        item.uncertainty_logic,
        item.scenario_logic,
        item.assumption_transparency,
        item.option_relevance,
        item.indicator_coverage,
        item.evidence_strength,
        item.stakeholder_visibility,
    ])


def assumption_risk(item: ForesightItem) -> float:
    return item.importance * item.uncertainty * (1.0 - item.evidence_strength)


def review_priority_score(item: ForesightItem) -> float:
    return min(
        1.0,
        assumption_risk(item) * 0.35
        + (1.0 - item.indicator_coverage) * 0.25
        + (1.0 - item.option_relevance) * 0.20
        + (1.0 - item.stakeholder_visibility) * 0.20,
    )


def governance_reasons(item: ForesightItem, risk: float, priority: float) -> list[str]:
    reasons: list[str] = []

    if item.driver_clarity < 0.60:
        reasons.append("weak driver clarity")
    if item.uncertainty_logic < 0.60:
        reasons.append("weak uncertainty logic")
    if item.scenario_logic < 0.60:
        reasons.append("weak scenario logic")
    if item.assumption_transparency < 0.60:
        reasons.append("weak assumption transparency")
    if item.option_relevance < 0.60:
        reasons.append("weak option relevance")
    if item.indicator_coverage < 0.60:
        reasons.append("weak indicator coverage")
    if item.evidence_strength < 0.60:
        reasons.append("weak evidence strength")
    if item.stakeholder_visibility < 0.60:
        reasons.append("weak stakeholder visibility")
    if risk >= 0.18:
        reasons.append("high assumption risk")
    if priority >= 0.45:
        reasons.append("review priority threshold reached")
    if item.status in {"review", "revise"}:
        reasons.append(f"status marked {item.status}")
    if len(item.description.split()) < 7:
        reasons.append("description may be too vague")

    return reasons


def recommended_action(item: ForesightItem, risk: float, priority: float) -> str:
    if item.status == "archive":
        return "Review whether this foresight item should be archived or retained for historical context."
    if item.status == "revise" or priority >= 0.45:
        return "Revise this foresight item before publication or strategic use and strengthen scenario logic assumptions indicators options evidence and stakeholder visibility."
    if risk >= 0.18 or item.status == "review":
        return "Review assumption risk indicator coverage option relevance and stakeholder implications during the next foresight governance cycle."
    return "Keep active and monitor during the next foresight review cycle."


def review_priority(item: ForesightItem, risk: float, priority: float) -> str:
    if item.status == "archive":
        return "archive review"
    if item.status == "revise" or priority >= 0.45:
        return "high"
    if risk >= 0.18 or item.status == "review":
        return "medium"
    return "standard"


def score_item(item: ForesightItem) -> AuditResult:
    risk = assumption_risk(item)
    priority = review_priority_score(item)
    reasons = governance_reasons(item, risk, priority)

    return AuditResult(
        item=item.item,
        foresight_type=item.foresight_type,
        description=item.description,
        owner=item.owner,
        status=item.status,
        review_date=item.review_date,
        driver_clarity=round_score(item.driver_clarity),
        uncertainty_logic=round_score(item.uncertainty_logic),
        scenario_logic=round_score(item.scenario_logic),
        assumption_transparency=round_score(item.assumption_transparency),
        option_relevance=round_score(item.option_relevance),
        indicator_coverage=round_score(item.indicator_coverage),
        evidence_strength=round_score(item.evidence_strength),
        stakeholder_visibility=round_score(item.stakeholder_visibility),
        importance=round_score(item.importance),
        uncertainty=round_score(item.uncertainty),
        quality_score=round_score(quality_score(item)),
        assumption_risk=round_score(risk),
        review_priority_score=round_score(priority),
        review_priority=review_priority(item, risk, priority),
        governance_reasons="; ".join(reasons) if reasons else "no immediate governance issue",
        recommended_action=recommended_action(item, risk, priority),
    )
