"""Scoring logic for framework drift and conceptual decay."""

from __future__ import annotations

from statistics import mean

from .models import AuditResult, FrameworkDriftItem


def round_score(value: float) -> float:
    return round(value, 3)


def conceptual_integrity(item: FrameworkDriftItem) -> float:
    return mean([
        item.definition_consistency,
        item.boundary_clarity,
        item.evidence_currency,
        item.metadata_consistency,
        item.link_health,
        item.governance_maturity,
    ])


def drift_risk(item: FrameworkDriftItem) -> float:
    integrity = conceptual_integrity(item)

    return min(
        1.0,
        (1.0 - integrity) * 0.32
        + item.reuse_pressure * 0.20
        + item.stale_evidence_risk * 0.18
        + item.dependency_complexity * 0.16
        + (1.0 - item.platform_alignment) * 0.14,
    )


def repair_priority_score(item: FrameworkDriftItem) -> float:
    return min(
        1.0,
        drift_risk(item) * 0.70
        + item.audience_impact * 0.30,
    )


def governance_reasons(item: FrameworkDriftItem, risk: float, priority: float) -> list[str]:
    reasons: list[str] = []

    if item.definition_consistency < 0.60:
        reasons.append("weak definition consistency")
    if item.boundary_clarity < 0.60:
        reasons.append("weak boundary clarity")
    if item.evidence_currency < 0.60:
        reasons.append("weak evidence currency")
    if item.metadata_consistency < 0.60:
        reasons.append("weak metadata consistency")
    if item.link_health < 0.60:
        reasons.append("weak link health")
    if item.governance_maturity < 0.60:
        reasons.append("weak governance maturity")
    if item.reuse_pressure >= 0.70:
        reasons.append("high reuse pressure")
    if item.stale_evidence_risk >= 0.60:
        reasons.append("high stale evidence risk")
    if item.dependency_complexity >= 0.60:
        reasons.append("high dependency complexity")
    if item.platform_alignment < 0.60:
        reasons.append("weak platform alignment")
    if item.audience_impact >= 0.75:
        reasons.append("high audience impact")
    if risk >= 0.40:
        reasons.append("high drift risk")
    if priority >= 0.55:
        reasons.append("repair priority threshold reached")
    if item.status in {"review", "revise"}:
        reasons.append(f"status marked {item.status}")
    if len(item.description.split()) < 7:
        reasons.append("description may be too vague")

    return reasons


def recommended_action(item: FrameworkDriftItem, risk: float, priority: float) -> str:
    if item.status == "archive":
        return "Review whether this framework asset should remain archived be redirected or be retired."
    if item.status == "revise" or priority >= 0.55:
        return "Repair this framework asset by restoring definition consistency boundary clarity evidence currency metadata link health governance maturity and platform alignment."
    if risk >= 0.40 or item.status == "review":
        return "Review drift risk reuse pressure stale evidence dependency complexity platform alignment and audience impact during the next governance cycle."
    return "Keep active and review during the next framework drift governance cycle."


def repair_priority(item: FrameworkDriftItem, risk: float, priority: float) -> str:
    if item.status == "archive":
        return "archive review"
    if item.status == "revise" or priority >= 0.55:
        return "high"
    if risk >= 0.40 or item.status == "review" or priority >= 0.40:
        return "medium"
    return "standard"


def score_item(item: FrameworkDriftItem) -> AuditResult:
    risk = drift_risk(item)
    priority = repair_priority_score(item)
    reasons = governance_reasons(item, risk, priority)

    return AuditResult(
        item=item.item,
        item_type=item.item_type,
        description=item.description,
        owner=item.owner,
        status=item.status,
        review_date=item.review_date,
        definition_consistency=round_score(item.definition_consistency),
        boundary_clarity=round_score(item.boundary_clarity),
        evidence_currency=round_score(item.evidence_currency),
        metadata_consistency=round_score(item.metadata_consistency),
        link_health=round_score(item.link_health),
        governance_maturity=round_score(item.governance_maturity),
        reuse_pressure=round_score(item.reuse_pressure),
        stale_evidence_risk=round_score(item.stale_evidence_risk),
        dependency_complexity=round_score(item.dependency_complexity),
        platform_alignment=round_score(item.platform_alignment),
        audience_impact=round_score(item.audience_impact),
        conceptual_integrity=round_score(conceptual_integrity(item)),
        drift_risk=round_score(risk),
        repair_priority_score=round_score(priority),
        repair_priority=repair_priority(item, risk, priority),
        governance_reasons="; ".join(reasons) if reasons else "no immediate drift issue",
        recommended_action=recommended_action(item, risk, priority),
    )
