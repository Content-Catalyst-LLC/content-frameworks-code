"""Scoring logic for framework composition governance."""

from __future__ import annotations

from statistics import mean

from .models import AuditResult, FrameworkCompositionItem


def round_score(value: float) -> float:
    return round(value, 3)


def quality_score(item: FrameworkCompositionItem) -> float:
    return mean([
        item.purpose_fit,
        item.role_clarity,
        item.boundary_clarity,
        item.sequence_clarity,
        item.translation_quality,
        item.evidence_alignment,
        item.governance_readiness,
    ])


def confusion_risk(item: FrameworkCompositionItem) -> float:
    return min(
        1.0,
        (1.0 - item.role_clarity) * 0.25
        + item.audience_burden * 0.25
        + (1.0 - item.translation_quality) * 0.25
        + item.conflict_risk * 0.25,
    )


def review_priority_score(item: FrameworkCompositionItem) -> float:
    return min(
        1.0,
        (1.0 - quality_score(item)) * 0.50
        + confusion_risk(item) * 0.50,
    )


def governance_reasons(item: FrameworkCompositionItem, risk: float, priority: float) -> list[str]:
    reasons: list[str] = []

    if item.purpose_fit < 0.60:
        reasons.append("weak purpose fit")
    if item.role_clarity < 0.60:
        reasons.append("weak role clarity")
    if item.boundary_clarity < 0.60:
        reasons.append("weak boundary clarity")
    if item.sequence_clarity < 0.60:
        reasons.append("weak sequence clarity")
    if item.translation_quality < 0.60:
        reasons.append("weak translation quality")
    if item.evidence_alignment < 0.60:
        reasons.append("weak evidence alignment")
    if item.governance_readiness < 0.60:
        reasons.append("weak governance readiness")
    if item.audience_burden >= 0.70:
        reasons.append("high audience burden")
    if item.conflict_risk >= 0.60:
        reasons.append("high framework conflict risk")
    if risk >= 0.40:
        reasons.append("high confusion risk")
    if priority >= 0.45:
        reasons.append("review priority threshold reached")
    if item.status in {"review", "revise"}:
        reasons.append(f"status marked {item.status}")
    if len(item.description.split()) < 7:
        reasons.append("description may be too vague")

    return reasons


def recommended_action(item: FrameworkCompositionItem, risk: float, priority: float) -> str:
    if item.status == "archive":
        return "Review whether this framework composition item should be archived or retained for historical context."
    if item.status == "revise" or priority >= 0.45:
        return "Revise this composition before publication and strengthen purpose role boundaries sequence translation evidence governance and audience pathway."
    if risk >= 0.40 or item.status == "review":
        return "Review composition risk translation interfaces model conflicts audience burden and governance dependencies during the next review cycle."
    return "Keep active and review during the next framework composition governance cycle."


def review_priority(item: FrameworkCompositionItem, risk: float, priority: float) -> str:
    if item.status == "archive":
        return "archive review"
    if item.status == "revise" or priority >= 0.45:
        return "high"
    if risk >= 0.40 or item.status == "review":
        return "medium"
    return "standard"


def score_item(item: FrameworkCompositionItem) -> AuditResult:
    risk = confusion_risk(item)
    priority = review_priority_score(item)
    reasons = governance_reasons(item, risk, priority)

    return AuditResult(
        item=item.item,
        composition_type=item.composition_type,
        description=item.description,
        owner=item.owner,
        status=item.status,
        review_date=item.review_date,
        purpose_fit=round_score(item.purpose_fit),
        role_clarity=round_score(item.role_clarity),
        boundary_clarity=round_score(item.boundary_clarity),
        sequence_clarity=round_score(item.sequence_clarity),
        translation_quality=round_score(item.translation_quality),
        evidence_alignment=round_score(item.evidence_alignment),
        governance_readiness=round_score(item.governance_readiness),
        audience_burden=round_score(item.audience_burden),
        conflict_risk=round_score(item.conflict_risk),
        quality_score=round_score(quality_score(item)),
        confusion_risk=round_score(risk),
        review_priority_score=round_score(priority),
        review_priority=review_priority(item, risk, priority),
        governance_reasons="; ".join(reasons) if reasons else "no immediate governance issue",
        recommended_action=recommended_action(item, risk, priority),
    )
