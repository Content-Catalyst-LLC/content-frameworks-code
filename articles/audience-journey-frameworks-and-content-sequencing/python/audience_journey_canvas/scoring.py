"""Scoring logic for Audience Journey Catalyst Canvas diagnostics."""

from __future__ import annotations

from statistics import mean

from .models import AuditResult, JourneyStage
from .validation import validate_weights


READINESS_WEIGHTS = {
    "stage_clarity": 0.18,
    "content_coverage": 0.22,
    "transition_quality": 0.20,
    "evidence_readiness": 0.22,
    "governance_readiness": 0.18,
}

validate_weights(READINESS_WEIGHTS)


def round_score(value: float) -> float:
    return round(value, 3)


def readiness_score(stage: JourneyStage) -> float:
    return mean([
        stage.stage_clarity,
        stage.content_coverage,
        stage.transition_quality,
        stage.evidence_readiness,
        stage.governance_readiness,
    ])


def weighted_readiness(stage: JourneyStage) -> float:
    return sum(getattr(stage, key) * weight for key, weight in READINESS_WEIGHTS.items())


def link_gap(stage: JourneyStage) -> int:
    return max(0, stage.required_links - stage.available_links)


def persona_mismatch(stage: JourneyStage) -> float:
    return max(0.0, 1.0 - stage.persona_fit)


def normalized_link_gap(stage: JourneyStage) -> float:
    denominator = max(1, stage.required_links)
    return min(1.0, link_gap(stage) / denominator)


def evidence_gap(stage: JourneyStage) -> float:
    return max(0.0, 0.70 - stage.evidence_readiness)


def journey_risk(stage: JourneyStage) -> float:
    return max([
        normalized_link_gap(stage),
        persona_mismatch(stage),
        stage.staleness_risk,
        evidence_gap(stage),
        max(0.0, 0.65 - stage.transition_quality),
        max(0.0, 0.65 - stage.governance_readiness),
    ])


def governance_reasons(stage: JourneyStage, gap: int, risk: float) -> list[str]:
    reasons: list[str] = []

    if stage.stage_clarity < 0.65:
        reasons.append("weak stage clarity")
    if stage.content_coverage < 0.65:
        reasons.append("weak content coverage")
    if stage.transition_quality < 0.65:
        reasons.append("weak transition quality")
    if stage.evidence_readiness < 0.70:
        reasons.append("weak evidence readiness")
    if stage.governance_readiness < 0.65:
        reasons.append("weak governance readiness")
    if gap > 0:
        reasons.append("missing journey links")
    if persona_mismatch(stage) >= 0.35:
        reasons.append("persona mismatch risk")
    if stage.staleness_risk >= 0.50:
        reasons.append("stale pathway risk")
    if risk >= 0.70:
        reasons.append("high journey risk")
    if stage.status in {"review", "revise"}:
        reasons.append(f"status marked {stage.status}")

    return reasons


def review_priority(stage: JourneyStage, gap: int, risk: float) -> str:
    if stage.status == "archive":
        return "archive review"
    if stage.status == "revise" or risk >= 0.70:
        return "high"
    if (
        stage.status == "review"
        or gap > 0
        or risk >= 0.45
        or stage.governance_readiness < 0.65
        or stage.evidence_readiness < 0.70
    ):
        return "medium"
    return "standard"


def score_stage(stage: JourneyStage) -> AuditResult:
    gap = link_gap(stage)
    risk = journey_risk(stage)
    reasons = governance_reasons(stage, gap, risk)

    return AuditResult(
        stage=stage.stage,
        audience_need=stage.audience_need,
        journey_type=stage.journey_type,
        owner=stage.owner,
        status=stage.status,
        review_date=stage.review_date,
        stage_clarity=round_score(stage.stage_clarity),
        content_coverage=round_score(stage.content_coverage),
        transition_quality=round_score(stage.transition_quality),
        evidence_readiness=round_score(stage.evidence_readiness),
        governance_readiness=round_score(stage.governance_readiness),
        required_links=stage.required_links,
        available_links=stage.available_links,
        link_gap=gap,
        persona_fit=round_score(stage.persona_fit),
        persona_mismatch=round_score(persona_mismatch(stage)),
        staleness_risk=round_score(stage.staleness_risk),
        journey_risk=round_score(risk),
        readiness_score=round_score(readiness_score(stage)),
        weighted_readiness=round_score(weighted_readiness(stage)),
        review_priority=review_priority(stage, gap, risk),
        governance_reasons="; ".join(reasons) if reasons else "no immediate governance issue",
    )
