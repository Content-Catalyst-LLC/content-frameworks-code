"""Scoring logic for knowledge scaling governance."""

from __future__ import annotations

from statistics import mean

from .models import AuditResult, KnowledgeScalingItem


def round_score(value: float) -> float:
    return round(value, 3)


def scalability_score(item: KnowledgeScalingItem) -> float:
    return mean([
        item.modularity,
        item.taxonomy_quality,
        item.metadata_completeness,
        item.link_coverage,
        item.evidence_alignment,
        item.reuse_readiness,
        item.governance_maturity,
        item.platform_readiness,
        item.audience_pathway_clarity,
    ])


def maintenance_risk(item: KnowledgeScalingItem) -> float:
    return min(
        1.0,
        (1.0 - item.governance_maturity) * 0.30
        + (1.0 - item.evidence_alignment) * 0.25
        + (1.0 - item.link_coverage) * 0.20
        + item.dependency_complexity * 0.25,
    )


def review_priority_score(item: KnowledgeScalingItem) -> float:
    return min(
        1.0,
        (1.0 - scalability_score(item)) * 0.50
        + maintenance_risk(item) * 0.50,
    )


def governance_reasons(item: KnowledgeScalingItem, risk: float, priority: float) -> list[str]:
    reasons: list[str] = []

    if item.modularity < 0.60:
        reasons.append("weak modularity")
    if item.taxonomy_quality < 0.60:
        reasons.append("weak taxonomy quality")
    if item.metadata_completeness < 0.60:
        reasons.append("weak metadata completeness")
    if item.link_coverage < 0.60:
        reasons.append("weak link coverage")
    if item.evidence_alignment < 0.60:
        reasons.append("weak evidence alignment")
    if item.reuse_readiness < 0.60:
        reasons.append("weak reuse readiness")
    if item.governance_maturity < 0.60:
        reasons.append("weak governance maturity")
    if item.platform_readiness < 0.60:
        reasons.append("weak platform readiness")
    if item.audience_pathway_clarity < 0.60:
        reasons.append("weak audience pathway clarity")
    if item.dependency_complexity >= 0.70:
        reasons.append("high dependency complexity")
    if risk >= 0.40:
        reasons.append("high maintenance risk")
    if priority >= 0.45:
        reasons.append("review priority threshold reached")
    if item.status in {"review", "revise"}:
        reasons.append(f"status marked {item.status}")
    if len(item.description.split()) < 7:
        reasons.append("description may be too vague")

    return reasons


def recommended_action(item: KnowledgeScalingItem, risk: float, priority: float) -> str:
    if item.status == "archive":
        return "Review whether this knowledge asset should be archived retained or redirected."
    if item.status == "revise" or priority >= 0.45:
        return "Revise this knowledge asset before further scaling and strengthen metadata links evidence reuse governance platform readiness and audience pathway clarity."
    if risk >= 0.40 or item.status == "review":
        return "Review maintenance risk evidence alignment link coverage dependency complexity and governance maturity during the next review cycle."
    return "Keep active and review during the next knowledge scaling governance cycle."


def review_priority(item: KnowledgeScalingItem, risk: float, priority: float) -> str:
    if item.status == "archive":
        return "archive review"
    if item.status == "revise" or priority >= 0.45:
        return "high"
    if risk >= 0.40 or item.status == "review":
        return "medium"
    return "standard"


def score_item(item: KnowledgeScalingItem) -> AuditResult:
    risk = maintenance_risk(item)
    priority = review_priority_score(item)
    reasons = governance_reasons(item, risk, priority)

    return AuditResult(
        item=item.item,
        asset_type=item.asset_type,
        description=item.description,
        owner=item.owner,
        status=item.status,
        review_date=item.review_date,
        modularity=round_score(item.modularity),
        taxonomy_quality=round_score(item.taxonomy_quality),
        metadata_completeness=round_score(item.metadata_completeness),
        link_coverage=round_score(item.link_coverage),
        evidence_alignment=round_score(item.evidence_alignment),
        reuse_readiness=round_score(item.reuse_readiness),
        governance_maturity=round_score(item.governance_maturity),
        platform_readiness=round_score(item.platform_readiness),
        audience_pathway_clarity=round_score(item.audience_pathway_clarity),
        dependency_complexity=round_score(item.dependency_complexity),
        scalability_score=round_score(scalability_score(item)),
        maintenance_risk=round_score(risk),
        review_priority_score=round_score(priority),
        review_priority=review_priority(item, risk, priority),
        governance_reasons="; ".join(reasons) if reasons else "no immediate governance issue",
        recommended_action=recommended_action(item, risk, priority),
    )
