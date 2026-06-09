"""Scoring logic for AI-assisted framework design governance."""

from __future__ import annotations

from statistics import mean

from .models import AIAssistedFrameworkItem, AuditResult


def round_score(value: float) -> float:
    return round(value, 3)


def readiness_score(item: AIAssistedFrameworkItem) -> float:
    return mean([
        item.conceptual_clarity,
        item.evidence_grounding,
        item.metadata_consistency,
        item.human_review_strength,
        item.bias_review,
        item.governance_maturity,
        item.platform_readiness,
        item.drift_control,
    ])


def ai_framework_risk(item: AIAssistedFrameworkItem) -> float:
    readiness = readiness_score(item)

    return min(
        1.0,
        (1.0 - readiness) * 0.32
        + item.unsupported_claim_risk * 0.24
        + item.generic_structure_risk * 0.18
        + (1.0 - item.bias_review) * 0.14
        + (1.0 - item.output_validation) * 0.12,
    )


def governance_priority_score(item: AIAssistedFrameworkItem) -> float:
    return min(
        1.0,
        ai_framework_risk(item) * 0.70
        + item.audience_impact * 0.30,
    )


def governance_reasons(item: AIAssistedFrameworkItem, risk: float, priority: float) -> list[str]:
    reasons: list[str] = []

    if item.conceptual_clarity < 0.60:
        reasons.append("weak conceptual clarity")
    if item.evidence_grounding < 0.60:
        reasons.append("weak evidence grounding")
    if item.metadata_consistency < 0.60:
        reasons.append("weak metadata consistency")
    if item.human_review_strength < 0.60:
        reasons.append("weak human review strength")
    if item.bias_review < 0.60:
        reasons.append("weak bias review")
    if item.governance_maturity < 0.60:
        reasons.append("weak governance maturity")
    if item.platform_readiness < 0.60:
        reasons.append("weak platform readiness")
    if item.drift_control < 0.60:
        reasons.append("weak drift control")
    if item.unsupported_claim_risk >= 0.60:
        reasons.append("high unsupported-claim risk")
    if item.generic_structure_risk >= 0.60:
        reasons.append("high generic-structure risk")
    if item.output_validation < 0.60:
        reasons.append("weak output validation")
    if item.audience_impact >= 0.75:
        reasons.append("high audience impact")
    if risk >= 0.40:
        reasons.append("high AI framework risk")
    if priority >= 0.55:
        reasons.append("governance priority threshold reached")
    if item.status in {"review", "revise"}:
        reasons.append(f"status marked {item.status}")
    if len(item.description.split()) < 7:
        reasons.append("description may be too vague")

    return reasons


def recommended_action(item: AIAssistedFrameworkItem, risk: float, priority: float) -> str:
    if item.status == "archive":
        return "Review whether this AI-assisted framework asset should remain archived be redirected or be retired."
    if item.status == "revise" or priority >= 0.55:
        return "Do not publish this asset without revision. Strengthen source grounding human review bias review governance metadata drift control and output validation."
    if risk >= 0.40 or item.status == "review":
        return "Review AI-assisted framework risk unsupported claims generic structure bias review output validation and audience impact during the next governance cycle."
    return "Keep active and review during the next AI-assisted framework governance cycle."


def governance_priority(item: AIAssistedFrameworkItem, risk: float, priority: float) -> str:
    if item.status == "archive":
        return "archive review"
    if item.status == "revise" or priority >= 0.55:
        return "high"
    if risk >= 0.40 or item.status == "review" or priority >= 0.40:
        return "medium"
    return "standard"


def score_item(item: AIAssistedFrameworkItem) -> AuditResult:
    risk = ai_framework_risk(item)
    priority = governance_priority_score(item)
    reasons = governance_reasons(item, risk, priority)

    return AuditResult(
        item=item.item,
        item_type=item.item_type,
        description=item.description,
        owner=item.owner,
        status=item.status,
        review_date=item.review_date,
        conceptual_clarity=round_score(item.conceptual_clarity),
        evidence_grounding=round_score(item.evidence_grounding),
        metadata_consistency=round_score(item.metadata_consistency),
        human_review_strength=round_score(item.human_review_strength),
        bias_review=round_score(item.bias_review),
        governance_maturity=round_score(item.governance_maturity),
        platform_readiness=round_score(item.platform_readiness),
        drift_control=round_score(item.drift_control),
        unsupported_claim_risk=round_score(item.unsupported_claim_risk),
        generic_structure_risk=round_score(item.generic_structure_risk),
        output_validation=round_score(item.output_validation),
        audience_impact=round_score(item.audience_impact),
        readiness_score=round_score(readiness_score(item)),
        ai_framework_risk=round_score(risk),
        governance_priority_score=round_score(priority),
        governance_priority=governance_priority(item, risk, priority),
        governance_reasons="; ".join(reasons) if reasons else "no immediate AI-assisted framework governance issue",
        recommended_action=recommended_action(item, risk, priority),
    )
