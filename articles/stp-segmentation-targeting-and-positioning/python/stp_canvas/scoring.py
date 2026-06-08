"""Scoring logic for STP Catalyst Canvas diagnostics."""

from __future__ import annotations

from statistics import mean

from .models import AuditResult, SegmentProfile
from .validation import validate_weights


TARGET_WEIGHTS = {
    "need_intensity": 0.25,
    "strategic_fit": 0.20,
    "reachability": 0.15,
    "evidence_fit": 0.20,
    "ethical_responsibility": 0.20,
}

GOVERNANCE_WEIGHTS = {
    "weighted_target_score": 0.35,
    "positioning_score": 0.35,
    "ethical_responsibility": 0.20,
    "ethical_integrity": 0.10,
}

validate_weights(TARGET_WEIGHTS)
validate_weights(GOVERNANCE_WEIGHTS)


def round_score(value: float) -> float:
    return round(value, 3)


def weighted_sum(profile: SegmentProfile, weights: dict[str, float]) -> float:
    return sum(getattr(profile, key) * weight for key, weight in weights.items())


def target_score(profile: SegmentProfile) -> float:
    return mean([
        profile.need_intensity,
        profile.strategic_fit,
        profile.reachability,
        profile.evidence_fit,
        profile.ethical_responsibility,
    ])


def positioning_score(profile: SegmentProfile) -> float:
    return mean([
        profile.category_clarity,
        profile.audience_relevance,
        profile.differentiation,
        profile.evidence_fit,
        profile.credibility,
    ])


def ethical_risk_score(profile: SegmentProfile) -> float:
    return max(profile.stereotype_risk, profile.exclusion_risk)


def classify_target(score: float) -> str:
    if score >= 0.85:
        return "primary target candidate"
    if score >= 0.70:
        return "strong secondary target"
    if score >= 0.55:
        return "monitor or support with lighter pathway"
    return "low current fit"


def ethical_review_flag(profile: SegmentProfile) -> str:
    if profile.stereotype_risk >= 0.70 or profile.exclusion_risk >= 0.70:
        return "high ethical review"
    if profile.stereotype_risk >= 0.50 or profile.exclusion_risk >= 0.50:
        return "moderate ethical review"
    return "standard review"


def governance_reasons(profile: SegmentProfile, gap: float) -> list[str]:
    reasons: list[str] = []

    if gap >= 0.20:
        reasons.append("major positioning gap")
    elif gap >= 0.10:
        reasons.append("moderate positioning gap")

    if profile.evidence_fit < 0.60:
        reasons.append("weak evidence fit")

    if profile.category_clarity < 0.60:
        reasons.append("weak category clarity")

    if profile.differentiation < 0.60:
        reasons.append("weak differentiation")

    if profile.stereotype_risk >= 0.50:
        reasons.append("stereotype-risk review")

    if profile.exclusion_risk >= 0.50:
        reasons.append("exclusion-risk review")

    if profile.status in {"review", "revise"}:
        reasons.append(f"status marked {profile.status}")

    return reasons


def review_priority(profile: SegmentProfile, gap: float, risk: float) -> str:
    if profile.status == "archive":
        return "archive review"
    if profile.status == "revise" or gap >= 0.20 or risk >= 0.70:
        return "high"
    if profile.status == "review" or gap >= 0.10 or risk >= 0.50 or profile.evidence_fit < 0.60:
        return "medium"
    return "standard"


def score_profile(profile: SegmentProfile) -> AuditResult:
    simple_target = target_score(profile)
    weighted_target = weighted_sum(profile, TARGET_WEIGHTS)
    position = positioning_score(profile)
    gap = max(0.0, profile.need_intensity - position)
    risk = ethical_risk_score(profile)
    ethical_integrity = 1.0 - risk

    governance = (
        weighted_target * GOVERNANCE_WEIGHTS["weighted_target_score"]
        + position * GOVERNANCE_WEIGHTS["positioning_score"]
        + profile.ethical_responsibility * GOVERNANCE_WEIGHTS["ethical_responsibility"]
        + ethical_integrity * GOVERNANCE_WEIGHTS["ethical_integrity"]
    )

    reasons = governance_reasons(profile, gap)

    return AuditResult(
        segment=profile.segment,
        description=profile.description,
        primary_job=profile.primary_job,
        content_pathway=profile.content_pathway,
        owner=profile.owner,
        status=profile.status,
        review_date=profile.review_date,
        target_score=round_score(simple_target),
        weighted_target_score=round_score(weighted_target),
        positioning_score=round_score(position),
        positioning_gap=round_score(gap),
        ethical_risk_score=round_score(risk),
        governance_score=round_score(governance),
        target_classification=classify_target(weighted_target),
        ethical_review_flag=ethical_review_flag(profile),
        review_priority=review_priority(profile, gap, risk),
        governance_reasons="; ".join(reasons) if reasons else "no immediate governance issue",
    )
