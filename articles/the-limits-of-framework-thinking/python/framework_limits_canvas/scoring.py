"""Scoring logic for framework limits governance."""

from __future__ import annotations

from statistics import mean

from .models import AuditResult, FrameworkLimitItem


def round_score(value: float) -> float:
    return round(value, 3)


def usefulness_score(item: FrameworkLimitItem) -> float:
    return mean([
        item.clarity,
        item.fit,
        item.evidence_alignment,
        item.assumption_transparency,
        item.governance_readiness,
    ])


def distortion_risk(item: FrameworkLimitItem) -> float:
    return min(
        1.0,
        item.oversimplification_risk * 0.22
        + item.false_precision_risk * 0.22
        + item.context_loss * 0.20
        + item.audience_burden * 0.18
        + item.value_opacity * 0.18,
    )


def review_priority_score(item: FrameworkLimitItem) -> float:
    return min(
        1.0,
        (1.0 - usefulness_score(item)) * 0.50
        + distortion_risk(item) * 0.50,
    )


def governance_reasons(item: FrameworkLimitItem, risk: float, priority: float) -> list[str]:
    reasons: list[str] = []

    if item.clarity < 0.60:
        reasons.append("weak clarity")
    if item.fit < 0.60:
        reasons.append("weak framework fit")
    if item.evidence_alignment < 0.60:
        reasons.append("weak evidence alignment")
    if item.assumption_transparency < 0.60:
        reasons.append("weak assumption transparency")
    if item.governance_readiness < 0.60:
        reasons.append("weak governance readiness")
    if item.oversimplification_risk >= 0.60:
        reasons.append("high oversimplification risk")
    if item.false_precision_risk >= 0.60:
        reasons.append("high false precision risk")
    if item.context_loss >= 0.60:
        reasons.append("high context loss")
    if item.audience_burden >= 0.60:
        reasons.append("high audience burden")
    if item.value_opacity >= 0.60:
        reasons.append("high value opacity")
    if risk >= 0.40:
        reasons.append("high distortion risk")
    if priority >= 0.45:
        reasons.append("review priority threshold reached")
    if item.status in {"review", "revise"}:
        reasons.append(f"status marked {item.status}")
    if len(item.description.split()) < 7:
        reasons.append("description may be too vague")

    return reasons


def recommended_action(item: FrameworkLimitItem, risk: float, priority: float) -> str:
    if item.status == "archive":
        return "Review whether this framework should be archived retained for historical context or redirected."
    if item.status == "revise" or priority >= 0.45:
        return "Revise this framework before reuse and strengthen fit evidence assumptions context notes governance and limits disclosure."
    if risk >= 0.40 or item.status == "review":
        return "Review distortion risk false precision assumptions context loss audience burden and governance readiness during the next review cycle."
    return "Keep active and review during the next framework limits governance cycle."


def review_priority(item: FrameworkLimitItem, risk: float, priority: float) -> str:
    if item.status == "archive":
        return "archive review"
    if item.status == "revise" or priority >= 0.45:
        return "high"
    if risk >= 0.40 or item.status == "review":
        return "medium"
    return "standard"


def score_item(item: FrameworkLimitItem) -> AuditResult:
    risk = distortion_risk(item)
    priority = review_priority_score(item)
    reasons = governance_reasons(item, risk, priority)

    return AuditResult(
        item=item.item,
        framework_type=item.framework_type,
        description=item.description,
        owner=item.owner,
        status=item.status,
        review_date=item.review_date,
        clarity=round_score(item.clarity),
        fit=round_score(item.fit),
        evidence_alignment=round_score(item.evidence_alignment),
        assumption_transparency=round_score(item.assumption_transparency),
        governance_readiness=round_score(item.governance_readiness),
        oversimplification_risk=round_score(item.oversimplification_risk),
        false_precision_risk=round_score(item.false_precision_risk),
        context_loss=round_score(item.context_loss),
        audience_burden=round_score(item.audience_burden),
        value_opacity=round_score(item.value_opacity),
        usefulness_score=round_score(usefulness_score(item)),
        distortion_risk=round_score(risk),
        review_priority_score=round_score(priority),
        review_priority=review_priority(item, risk, priority),
        governance_reasons="; ".join(reasons) if reasons else "no immediate governance issue",
        recommended_action=recommended_action(item, risk, priority),
    )
