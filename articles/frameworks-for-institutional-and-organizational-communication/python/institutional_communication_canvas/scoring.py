"""Scoring logic for institutional and organizational communication governance."""

from __future__ import annotations

from statistics import mean

from .models import AuditResult, CommunicationItem


def round_score(value: float) -> float:
    return round(value, 3)


def quality_score(item: CommunicationItem) -> float:
    return mean([
        item.clarity,
        item.authority_coverage,
        item.evidence_strength,
        item.stakeholder_visibility,
        item.feedback_quality,
        item.channel_fit,
        item.cultural_alignment,
        item.governance_coverage,
    ])


def evidence_gap(item: CommunicationItem) -> float:
    return max(0.0, item.claim_strength - item.evidence_strength)


def trust_risk(item: CommunicationItem) -> float:
    return min(
        1.0,
        item.ambiguity * 0.25
        + (1.0 - item.governance_coverage) * 0.25
        + (1.0 - item.evidence_strength) * 0.20
        + (1.0 - item.stakeholder_visibility) * 0.15
        + (1.0 - item.feedback_quality) * 0.15,
    )


def review_priority_score(item: CommunicationItem) -> float:
    return min(
        1.0,
        trust_risk(item) * 0.40
        + (1.0 - item.authority_coverage) * 0.25
        + evidence_gap(item) * 0.20
        + (1.0 - item.feedback_quality) * 0.15,
    )


def governance_reasons(item: CommunicationItem, gap: float, risk: float, priority: float) -> list[str]:
    reasons: list[str] = []

    if item.clarity < 0.60:
        reasons.append("weak clarity")
    if item.authority_coverage < 0.60:
        reasons.append("weak authority coverage")
    if item.evidence_strength < 0.60:
        reasons.append("weak evidence strength")
    if item.stakeholder_visibility < 0.60:
        reasons.append("weak stakeholder visibility")
    if item.feedback_quality < 0.60:
        reasons.append("weak feedback quality")
    if item.channel_fit < 0.60:
        reasons.append("weak channel fit")
    if item.cultural_alignment < 0.60:
        reasons.append("weak cultural alignment")
    if item.governance_coverage < 0.60:
        reasons.append("weak governance coverage")
    if item.ambiguity >= 0.60:
        reasons.append("high ambiguity")
    if gap >= 0.15:
        reasons.append("evidence gap")
    if risk >= 0.55:
        reasons.append("trust risk")
    if priority >= 0.45:
        reasons.append("review priority threshold reached")
    if item.status in {"review", "revise"}:
        reasons.append(f"status marked {item.status}")
    if len(item.description.split()) < 7:
        reasons.append("description may be too vague")

    return reasons


def recommended_action(item: CommunicationItem, gap: float, risk: float, priority: float) -> str:
    if item.status == "archive":
        return "Review whether this institutional communication item should be archived or retained for historical context."
    if item.status == "revise" or gap >= 0.30:
        return "Revise this communication before publication or rollout and strengthen ownership evidence feedback routes governance coverage and stakeholder visibility."
    if risk >= 0.55 or priority >= 0.45:
        return "Review authority evidence stakeholder impacts feedback quality channel fit and trust risk before publication."
    return "Keep active and review during the next institutional communication governance cycle."


def review_priority(item: CommunicationItem, gap: float, risk: float, priority: float) -> str:
    if item.status == "archive":
        return "archive review"
    if item.status == "revise" or gap >= 0.30:
        return "high"
    if priority >= 0.45 or risk >= 0.55 or gap >= 0.15 or item.status == "review":
        return "medium"
    return "standard"


def score_item(item: CommunicationItem) -> AuditResult:
    gap = evidence_gap(item)
    risk = trust_risk(item)
    priority = review_priority_score(item)
    reasons = governance_reasons(item, gap, risk, priority)

    return AuditResult(
        item=item.item,
        communication_type=item.communication_type,
        description=item.description,
        owner=item.owner,
        status=item.status,
        review_date=item.review_date,
        clarity=round_score(item.clarity),
        authority_coverage=round_score(item.authority_coverage),
        evidence_strength=round_score(item.evidence_strength),
        stakeholder_visibility=round_score(item.stakeholder_visibility),
        feedback_quality=round_score(item.feedback_quality),
        channel_fit=round_score(item.channel_fit),
        cultural_alignment=round_score(item.cultural_alignment),
        governance_coverage=round_score(item.governance_coverage),
        ambiguity=round_score(item.ambiguity),
        claim_strength=round_score(item.claim_strength),
        quality_score=round_score(quality_score(item)),
        evidence_gap=round_score(gap),
        trust_risk=round_score(risk),
        review_priority_score=round_score(priority),
        review_priority=review_priority(item, gap, risk, priority),
        governance_reasons="; ".join(reasons) if reasons else "no immediate governance issue",
        recommended_action=recommended_action(item, gap, risk, priority),
    )
