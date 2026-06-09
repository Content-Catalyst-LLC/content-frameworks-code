"""Scoring logic for Ansoff Matrix Catalyst Canvas diagnostics."""

from __future__ import annotations

from statistics import mean

from .models import AuditResult, GrowthOption


def round_score(value: float) -> float:
    return round(value, 3)


def readiness_score(option: GrowthOption) -> float:
    return mean([
        option.strategic_fit,
        option.evidence_strength,
        option.feasibility,
        option.capability_readiness,
    ])


def risk_score(option: GrowthOption) -> float:
    return min(
        1.0,
        (
            (1.0 - option.market_familiarity)
            + (1.0 - option.product_familiarity)
            + option.uncertainty
        ) / 3.0
    )


def evidence_gap(option: GrowthOption) -> float:
    return max(0.0, option.claim_strength - option.evidence_strength)


def growth_quality(option: GrowthOption) -> float:
    return max(
        0.0,
        min(
            1.0,
            readiness_score(option) * 0.55
            + option.expected_value * 0.35
            - risk_score(option) * 0.20
        )
    )


def governance_priority(option: GrowthOption) -> float:
    return min(
        1.0,
        risk_score(option) * 0.35
        + evidence_gap(option) * 0.40
        + (1.0 - option.feasibility) * 0.25
    )


def governance_reasons(option: GrowthOption, gap: float, risk: float, governance_score: float) -> list[str]:
    reasons: list[str] = []

    if option.growth_path == "unclear":
        reasons.append("unclear growth path")
    if option.evidence_strength < 0.60:
        reasons.append("weak evidence strength")
    if option.feasibility < 0.60:
        reasons.append("low feasibility")
    if option.capability_readiness < 0.60:
        reasons.append("low capability readiness")
    if option.uncertainty >= 0.65:
        reasons.append("high uncertainty")
    if risk >= 0.55:
        reasons.append("high growth risk")
    if gap >= 0.15:
        reasons.append("evidence gap")
    if governance_score >= 0.50:
        reasons.append("governance review needed")
    if option.status in {"review", "revise"}:
        reasons.append(f"status marked {option.status}")
    if len(option.description.split()) < 8:
        reasons.append("description may be too vague")

    return reasons


def review_priority(option: GrowthOption, gap: float, risk: float, governance_score: float) -> str:
    if option.status == "archive":
        return "archive review"
    if option.status == "revise" or gap >= 0.30:
        return "high"
    if governance_score >= 0.50 or risk >= 0.55 or gap >= 0.15 or option.status == "review":
        return "medium"
    return "standard"


def score_option(option: GrowthOption) -> AuditResult:
    gap = evidence_gap(option)
    risk = risk_score(option)
    governance_score = governance_priority(option)
    reasons = governance_reasons(option, gap, risk, governance_score)

    return AuditResult(
        option=option.option,
        growth_path=option.growth_path,
        market_status=option.market_status,
        product_status=option.product_status,
        description=option.description,
        owner=option.owner,
        status=option.status,
        review_date=option.review_date,
        strategic_fit=round_score(option.strategic_fit),
        evidence_strength=round_score(option.evidence_strength),
        feasibility=round_score(option.feasibility),
        capability_readiness=round_score(option.capability_readiness),
        expected_value=round_score(option.expected_value),
        market_familiarity=round_score(option.market_familiarity),
        product_familiarity=round_score(option.product_familiarity),
        uncertainty=round_score(option.uncertainty),
        claim_strength=round_score(option.claim_strength),
        readiness_score=round_score(readiness_score(option)),
        risk_score=round_score(risk),
        evidence_gap=round_score(gap),
        growth_quality=round_score(growth_quality(option)),
        governance_priority=round_score(governance_score),
        review_priority=review_priority(option, gap, risk, governance_score),
        governance_reasons="; ".join(reasons) if reasons else "no immediate governance issue",
    )
