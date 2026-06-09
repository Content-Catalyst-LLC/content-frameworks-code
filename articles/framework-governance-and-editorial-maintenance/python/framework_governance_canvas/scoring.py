"""Scoring logic for framework governance and editorial maintenance."""

from __future__ import annotations

from statistics import mean

from .models import AuditResult, FrameworkGovernanceItem


def round_score(value: float) -> float:
    return round(value, 3)


def governance_maturity(item: FrameworkGovernanceItem) -> float:
    return mean([
        item.ownership_clarity,
        item.review_cycle_strength,
        item.metadata_completeness,
        item.evidence_status,
        item.link_health,
        item.taxonomy_alignment,
        item.platform_readiness,
    ])


def maintenance_risk(item: FrameworkGovernanceItem) -> float:
    maturity = governance_maturity(item)

    return min(
        1.0,
        (1.0 - maturity) * 0.34
        + item.stale_evidence_risk * 0.22
        + (1.0 - item.link_health) * 0.16
        + (1.0 - item.platform_readiness) * 0.12
        + item.dependency_complexity * 0.16,
    )


def review_priority_score(item: FrameworkGovernanceItem) -> float:
    return min(
        1.0,
        maintenance_risk(item) * 0.70
        + item.audience_impact * 0.30,
    )


def governance_reasons(item: FrameworkGovernanceItem, risk: float, priority: float) -> list[str]:
    reasons: list[str] = []

    if item.ownership_clarity < 0.60:
        reasons.append("weak ownership clarity")
    if item.review_cycle_strength < 0.60:
        reasons.append("weak review-cycle strength")
    if item.metadata_completeness < 0.60:
        reasons.append("weak metadata completeness")
    if item.evidence_status < 0.60:
        reasons.append("weak evidence status")
    if item.link_health < 0.60:
        reasons.append("weak link health")
    if item.taxonomy_alignment < 0.60:
        reasons.append("weak taxonomy alignment")
    if item.platform_readiness < 0.60:
        reasons.append("weak platform readiness")
    if item.stale_evidence_risk >= 0.60:
        reasons.append("high stale evidence risk")
    if item.dependency_complexity >= 0.60:
        reasons.append("high dependency complexity")
    if item.audience_impact >= 0.75:
        reasons.append("high audience impact")
    if risk >= 0.40:
        reasons.append("high maintenance risk")
    if priority >= 0.55:
        reasons.append("review priority threshold reached")
    if item.status in {"review", "revise"}:
        reasons.append(f"status marked {item.status}")
    if len(item.description.split()) < 7:
        reasons.append("description may be too vague")

    return reasons


def recommended_action(item: FrameworkGovernanceItem, risk: float, priority: float) -> str:
    if item.status == "archive":
        return "Review whether this framework asset should be archived retained redirected or retired."
    if item.status == "revise" or priority >= 0.55:
        return "Revise this framework asset and strengthen ownership review cadence metadata evidence link health taxonomy alignment repository readiness and decision records."
    if risk >= 0.40 or item.status == "review":
        return "Review maintenance risk evidence status link health platform readiness dependency complexity and audience impact during the next governance cycle."
    return "Keep active and review during the next framework governance cycle."


def review_priority(item: FrameworkGovernanceItem, risk: float, priority: float) -> str:
    if item.status == "archive":
        return "archive review"
    if item.status == "revise" or priority >= 0.55:
        return "high"
    if risk >= 0.40 or item.status == "review" or priority >= 0.40:
        return "medium"
    return "standard"


def score_item(item: FrameworkGovernanceItem) -> AuditResult:
    risk = maintenance_risk(item)
    priority = review_priority_score(item)
    reasons = governance_reasons(item, risk, priority)

    return AuditResult(
        item=item.item,
        item_type=item.item_type,
        description=item.description,
        owner=item.owner,
        status=item.status,
        review_date=item.review_date,
        ownership_clarity=round_score(item.ownership_clarity),
        review_cycle_strength=round_score(item.review_cycle_strength),
        metadata_completeness=round_score(item.metadata_completeness),
        evidence_status=round_score(item.evidence_status),
        link_health=round_score(item.link_health),
        taxonomy_alignment=round_score(item.taxonomy_alignment),
        platform_readiness=round_score(item.platform_readiness),
        stale_evidence_risk=round_score(item.stale_evidence_risk),
        dependency_complexity=round_score(item.dependency_complexity),
        audience_impact=round_score(item.audience_impact),
        governance_maturity=round_score(governance_maturity(item)),
        maintenance_risk=round_score(risk),
        review_priority_score=round_score(priority),
        review_priority=review_priority(item, risk, priority),
        governance_reasons="; ".join(reasons) if reasons else "no immediate governance issue",
        recommended_action=recommended_action(item, risk, priority),
    )
