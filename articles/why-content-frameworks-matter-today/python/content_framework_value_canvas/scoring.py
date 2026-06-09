"""Scoring logic for content framework value governance."""

from __future__ import annotations

from statistics import mean

from .models import AuditResult, ContentFrameworkValueItem


def round_score(value: float) -> float:
    return round(value, 3)


def value_score(item: ContentFrameworkValueItem) -> float:
    return mean([
        item.coherence,
        item.reuse_readiness,
        item.evidence_visibility,
        item.audience_pathway_clarity,
        item.governance_maturity,
        item.platform_readiness,
        item.learning_support,
        item.ai_readiness,
    ])


def framework_risk(item: ContentFrameworkValueItem) -> float:
    return min(
        1.0,
        (1.0 - item.evidence_visibility) * 0.22
        + (1.0 - item.governance_maturity) * 0.22
        + item.fragmentation_risk * 0.22
        + (1.0 - item.context_preservation) * 0.17
        + item.maintenance_burden * 0.17,
    )


def review_priority_score(item: ContentFrameworkValueItem) -> float:
    return min(
        1.0,
        (1.0 - value_score(item)) * 0.50
        + framework_risk(item) * 0.50,
    )


def governance_reasons(item: ContentFrameworkValueItem, risk: float, priority: float) -> list[str]:
    reasons: list[str] = []

    if item.coherence < 0.60:
        reasons.append("weak coherence")
    if item.reuse_readiness < 0.60:
        reasons.append("weak reuse readiness")
    if item.evidence_visibility < 0.60:
        reasons.append("weak evidence visibility")
    if item.audience_pathway_clarity < 0.60:
        reasons.append("weak audience pathway clarity")
    if item.governance_maturity < 0.60:
        reasons.append("weak governance maturity")
    if item.platform_readiness < 0.60:
        reasons.append("weak platform readiness")
    if item.learning_support < 0.60:
        reasons.append("weak learning support")
    if item.ai_readiness < 0.60:
        reasons.append("weak AI-readiness")
    if item.fragmentation_risk >= 0.60:
        reasons.append("high fragmentation risk")
    if item.context_preservation < 0.60:
        reasons.append("weak context preservation")
    if item.maintenance_burden >= 0.60:
        reasons.append("high maintenance burden")
    if risk >= 0.40:
        reasons.append("high framework risk")
    if priority >= 0.45:
        reasons.append("review priority threshold reached")
    if item.status in {"review", "revise"}:
        reasons.append(f"status marked {item.status}")
    if len(item.description.split()) < 7:
        reasons.append("description may be too vague")

    return reasons


def recommended_action(item: ContentFrameworkValueItem, risk: float, priority: float) -> str:
    if item.status == "archive":
        return "Review whether this framework should be archived retained redirected or retired."
    if item.status == "revise" or priority >= 0.45:
        return "Revise this framework before further reuse and strengthen coherence evidence visibility governance metadata platform readiness context preservation and maintenance planning."
    if risk >= 0.40 or item.status == "review":
        return "Review framework risk evidence visibility governance maturity fragmentation context preservation and maintenance burden during the next review cycle."
    return "Keep active and review during the next content framework value governance cycle."


def review_priority(item: ContentFrameworkValueItem, risk: float, priority: float) -> str:
    if item.status == "archive":
        return "archive review"
    if item.status == "revise" or priority >= 0.45:
        return "high"
    if risk >= 0.40 or item.status == "review":
        return "medium"
    return "standard"


def score_item(item: ContentFrameworkValueItem) -> AuditResult:
    risk = framework_risk(item)
    priority = review_priority_score(item)
    reasons = governance_reasons(item, risk, priority)

    return AuditResult(
        item=item.item,
        framework_type=item.framework_type,
        description=item.description,
        owner=item.owner,
        status=item.status,
        review_date=item.review_date,
        coherence=round_score(item.coherence),
        reuse_readiness=round_score(item.reuse_readiness),
        evidence_visibility=round_score(item.evidence_visibility),
        audience_pathway_clarity=round_score(item.audience_pathway_clarity),
        governance_maturity=round_score(item.governance_maturity),
        platform_readiness=round_score(item.platform_readiness),
        learning_support=round_score(item.learning_support),
        ai_readiness=round_score(item.ai_readiness),
        fragmentation_risk=round_score(item.fragmentation_risk),
        context_preservation=round_score(item.context_preservation),
        maintenance_burden=round_score(item.maintenance_burden),
        value_score=round_score(value_score(item)),
        framework_risk=round_score(risk),
        review_priority_score=round_score(priority),
        review_priority=review_priority(item, risk, priority),
        governance_reasons="; ".join(reasons) if reasons else "no immediate governance issue",
        recommended_action=recommended_action(item, risk, priority),
    )
