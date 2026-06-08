"""Scoring logic for generic Content Frameworks Catalyst Canvas readiness."""

from __future__ import annotations

from .models import AuditResult, CanvasRecord
from .validation import validate_weights


READINESS_WEIGHTS = {
    "content_value": 0.22,
    "audience_value": 0.24,
    "evidence_strength": 0.22,
    "repository_support": 0.16,
    "governance_inverse": 0.10,
    "ethical_inverse": 0.06,
}

validate_weights(READINESS_WEIGHTS)


def round_score(value: float) -> float:
    return round(value, 3)


def readiness_score(record: CanvasRecord) -> float:
    governance_inverse = 1.0 - record.governance_need
    ethical_inverse = 1.0 - record.ethical_risk

    return (
        record.content_value * READINESS_WEIGHTS["content_value"]
        + record.audience_value * READINESS_WEIGHTS["audience_value"]
        + record.evidence_strength * READINESS_WEIGHTS["evidence_strength"]
        + record.repository_support * READINESS_WEIGHTS["repository_support"]
        + governance_inverse * READINESS_WEIGHTS["governance_inverse"]
        + ethical_inverse * READINESS_WEIGHTS["ethical_inverse"]
    )


def governance_reasons(record: CanvasRecord) -> list[str]:
    reasons: list[str] = []

    if record.content_value < 0.65:
        reasons.append("weak content value")

    if record.audience_value < 0.65:
        reasons.append("weak audience value")

    if record.evidence_strength < 0.70:
        reasons.append("evidence needs strengthening")

    if record.repository_support < 0.70:
        reasons.append("repository support needs improvement")

    if record.governance_need >= 0.75:
        reasons.append("high governance need")

    if record.ethical_risk >= 0.50:
        reasons.append("ethical risk review")

    if record.status in {"review", "revise"}:
        reasons.append(f"status marked {record.status}")

    return reasons


def review_priority(record: CanvasRecord, score: float) -> str:
    if record.status == "archive":
        return "archive review"
    if record.status == "revise" or score < 0.62 or record.ethical_risk >= 0.70:
        return "high"
    if record.status == "review" or score < 0.74 or record.governance_need >= 0.75 or record.ethical_risk >= 0.50:
        return "medium"
    return "standard"


def score_record(record: CanvasRecord) -> AuditResult:
    score = readiness_score(record)
    reasons = governance_reasons(record)

    return AuditResult(
        record_id=record.record_id,
        article_slug=record.article_slug,
        article_title=record.article_title,
        module_kind=record.module_kind,
        canvas_dimension=record.canvas_dimension,
        description=record.description,
        owner=record.owner,
        status=record.status,
        review_date=record.review_date,
        content_score=round_score(record.content_value),
        audience_score=round_score(record.audience_value),
        evidence_score=round_score(record.evidence_strength),
        repository_score=round_score(record.repository_support),
        governance_pressure=round_score(record.governance_need),
        ethical_risk=round_score(record.ethical_risk),
        readiness_score=round_score(score),
        review_priority=review_priority(record, score),
        governance_reasons="; ".join(reasons) if reasons else "no immediate governance issue",
    )
