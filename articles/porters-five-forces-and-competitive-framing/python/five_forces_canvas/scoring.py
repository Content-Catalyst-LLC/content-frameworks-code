"""Scoring logic for Porter Five Forces Catalyst Canvas diagnostics."""

from __future__ import annotations

from statistics import mean

from .models import AuditResult, ForceRecord
from .validation import validate_weights


PRIORITY_WEIGHTS = {
    "intensity": 0.30,
    "evidence_strength": 0.18,
    "uncertainty": 0.12,
    "strategic_relevance": 0.26,
    "actionability": 0.14,
}

validate_weights(PRIORITY_WEIGHTS)


def round_score(value: float) -> float:
    return round(value, 3)


def readiness_score(record: ForceRecord) -> float:
    return mean([
        record.intensity,
        record.evidence_strength,
        record.strategic_relevance,
        record.actionability,
    ])


def weighted_priority(record: ForceRecord) -> float:
    return sum(getattr(record, key) * weight for key, weight in PRIORITY_WEIGHTS.items())


def evidence_gap(record: ForceRecord) -> float:
    return max(0.0, record.claim_strength - record.evidence_strength)


def governance_priority(record: ForceRecord) -> float:
    return min(1.0, weighted_priority(record) + evidence_gap(record) * 0.45)


def governance_reasons(record: ForceRecord, gap: float, governance_score: float) -> list[str]:
    reasons: list[str] = []

    if record.market_boundary.strip().lower() in {"unclear", "broad", "unknown"}:
        reasons.append("unclear market boundary")
    if record.evidence_strength < 0.60:
        reasons.append("weak evidence strength")
    if record.strategic_relevance < 0.60:
        reasons.append("weak strategic relevance")
    if record.actionability < 0.60:
        reasons.append("low actionability")
    if record.uncertainty >= 0.60:
        reasons.append("high uncertainty")
    if gap >= 0.15:
        reasons.append("evidence gap")
    if governance_score >= 0.75:
        reasons.append("high governance priority")
    if record.status in {"review", "revise"}:
        reasons.append(f"status marked {record.status}")
    if len(record.description.split()) < 7:
        reasons.append("description may be too vague")

    return reasons


def review_priority(record: ForceRecord, gap: float, governance_score: float) -> str:
    if record.status == "archive":
        return "archive review"
    if record.status == "revise" or gap >= 0.30:
        return "high"
    if governance_score >= 0.75 or gap >= 0.15 or record.status == "review":
        return "medium"
    return "standard"


def score_record(record: ForceRecord) -> AuditResult:
    gap = evidence_gap(record)
    governance_score = governance_priority(record)
    reasons = governance_reasons(record, gap, governance_score)

    return AuditResult(
        force=record.force,
        market_boundary=record.market_boundary,
        description=record.description,
        owner=record.owner,
        status=record.status,
        review_date=record.review_date,
        intensity=round_score(record.intensity),
        evidence_strength=round_score(record.evidence_strength),
        uncertainty=round_score(record.uncertainty),
        strategic_relevance=round_score(record.strategic_relevance),
        actionability=round_score(record.actionability),
        claim_strength=round_score(record.claim_strength),
        readiness_score=round_score(readiness_score(record)),
        weighted_priority=round_score(weighted_priority(record)),
        evidence_gap=round_score(gap),
        governance_priority=round_score(governance_score),
        review_priority=review_priority(record, gap, governance_score),
        governance_reasons="; ".join(reasons) if reasons else "no immediate governance issue",
    )
