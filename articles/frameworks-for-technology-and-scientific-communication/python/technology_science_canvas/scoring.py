"""Scoring logic for technology and scientific communication governance."""

from __future__ import annotations

from statistics import mean

from .models import AuditResult, TechScienceItem


def round_score(value: float) -> float:
    return round(value, 3)


def quality_score(item: TechScienceItem) -> float:
    return mean([
        item.claim_clarity,
        item.evidence_strength,
        item.method_transparency,
        item.uncertainty_disclosure,
        item.audience_fit,
        item.risk_visibility,
        item.stakeholder_visibility,
    ])


def evidence_gap(item: TechScienceItem) -> float:
    return max(0.0, item.claim_breadth - item.evidence_strength)


def hype_risk(item: TechScienceItem) -> float:
    return min(
        1.0,
        (1.0 - item.evidence_strength) * 0.25
        + (1.0 - item.uncertainty_disclosure) * 0.25
        + item.promotional_intensity * 0.25
        + item.claim_breadth * 0.25,
    )


def review_priority_score(item: TechScienceItem) -> float:
    return min(
        1.0,
        evidence_gap(item) * 0.35
        + hype_risk(item) * 0.40
        + (1.0 - item.audience_fit) * 0.15
        + (1.0 - item.risk_visibility) * 0.10,
    )


def governance_reasons(item: TechScienceItem, gap: float, risk: float, priority: float) -> list[str]:
    reasons: list[str] = []

    if item.claim_clarity < 0.60:
        reasons.append("weak claim clarity")
    if item.evidence_strength < 0.60:
        reasons.append("weak evidence strength")
    if item.method_transparency < 0.60:
        reasons.append("weak method transparency")
    if item.uncertainty_disclosure < 0.60:
        reasons.append("weak uncertainty disclosure")
    if item.audience_fit < 0.60:
        reasons.append("weak audience fit")
    if item.risk_visibility < 0.60:
        reasons.append("weak risk visibility")
    if item.stakeholder_visibility < 0.60:
        reasons.append("weak stakeholder visibility")
    if item.promotional_intensity >= 0.65:
        reasons.append("high promotional intensity")
    if item.claim_breadth >= 0.80:
        reasons.append("broad claim")
    if gap >= 0.15:
        reasons.append("evidence gap")
    if risk >= 0.55:
        reasons.append("hype risk")
    if priority >= 0.45:
        reasons.append("review priority threshold reached")
    if item.status in {"review", "revise"}:
        reasons.append(f"status marked {item.status}")
    if len(item.description.split()) < 7:
        reasons.append("description may be too vague")

    return reasons


def recommended_action(item: TechScienceItem, gap: float, risk: float, priority: float) -> str:
    if item.status == "archive":
        return "Review whether this technical or scientific communication item should be archived or retained for historical context."
    if item.status == "revise" or gap >= 0.30:
        return "Revise this communication before publication and strengthen evidence method transparency uncertainty disclosure risk visibility and claim boundaries."
    if risk >= 0.55 or priority >= 0.45:
        return "Review claim wording evidence method explanation uncertainty risk stakeholder impacts and hype risk before publication."
    return "Keep active and review during the next technology and scientific communication governance cycle."


def review_priority(item: TechScienceItem, gap: float, risk: float, priority: float) -> str:
    if item.status == "archive":
        return "archive review"
    if item.status == "revise" or gap >= 0.30:
        return "high"
    if priority >= 0.45 or risk >= 0.55 or gap >= 0.15 or item.status == "review":
        return "medium"
    return "standard"


def score_item(item: TechScienceItem) -> AuditResult:
    gap = evidence_gap(item)
    risk = hype_risk(item)
    priority = review_priority_score(item)
    reasons = governance_reasons(item, gap, risk, priority)

    return AuditResult(
        item=item.item,
        communication_type=item.communication_type,
        description=item.description,
        owner=item.owner,
        status=item.status,
        review_date=item.review_date,
        claim_clarity=round_score(item.claim_clarity),
        evidence_strength=round_score(item.evidence_strength),
        method_transparency=round_score(item.method_transparency),
        uncertainty_disclosure=round_score(item.uncertainty_disclosure),
        audience_fit=round_score(item.audience_fit),
        risk_visibility=round_score(item.risk_visibility),
        stakeholder_visibility=round_score(item.stakeholder_visibility),
        promotional_intensity=round_score(item.promotional_intensity),
        claim_breadth=round_score(item.claim_breadth),
        quality_score=round_score(quality_score(item)),
        evidence_gap=round_score(gap),
        hype_risk=round_score(risk),
        review_priority_score=round_score(priority),
        review_priority=review_priority(item, gap, risk, priority),
        governance_reasons="; ".join(reasons) if reasons else "no immediate governance issue",
        recommended_action=recommended_action(item, gap, risk, priority),
    )
