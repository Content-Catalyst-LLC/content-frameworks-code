"""Scoring logic for Persona Frameworks Catalyst Canvas diagnostics."""

from __future__ import annotations

from statistics import mean

from .models import AuditResult, PersonaRecord
from .validation import validate_weights


READINESS_WEIGHTS = {
    "evidence_strength": 0.28,
    "specificity": 0.18,
    "content_fit": 0.20,
    "segment_alignment": 0.18,
    "governance_readiness": 0.16,
}

validate_weights(READINESS_WEIGHTS)


def round_score(value: float) -> float:
    return round(value, 3)


def readiness_score(record: PersonaRecord) -> float:
    return mean([
        record.evidence_strength,
        record.specificity,
        record.content_fit,
        record.segment_alignment,
        record.governance_readiness,
    ])


def weighted_readiness(record: PersonaRecord) -> float:
    return sum(getattr(record, key) * weight for key, weight in READINESS_WEIGHTS.items())


def risk_score(record: PersonaRecord) -> float:
    return max([
        record.stereotype_risk,
        record.exclusion_risk,
        record.weak_evidence_risk,
        record.overgeneralization_risk,
    ])


def revision_pressure(record: PersonaRecord) -> float:
    return max(0.0, risk_score(record) - weighted_readiness(record))


def governance_reasons(record: PersonaRecord, risk: float, pressure: float) -> list[str]:
    reasons: list[str] = []

    if record.evidence_strength < 0.60:
        reasons.append("weak evidence strength")
    if record.specificity < 0.60:
        reasons.append("weak persona specificity")
    if record.content_fit < 0.60:
        reasons.append("weak content fit")
    if record.segment_alignment < 0.60:
        reasons.append("weak segment alignment")
    if record.governance_readiness < 0.65:
        reasons.append("weak governance readiness")
    if record.stereotype_risk >= 0.50:
        reasons.append("stereotype risk review")
    if record.exclusion_risk >= 0.50:
        reasons.append("exclusion risk review")
    if record.weak_evidence_risk >= 0.50:
        reasons.append("weak evidence risk review")
    if record.overgeneralization_risk >= 0.50:
        reasons.append("overgeneralization risk review")
    if risk >= 0.70:
        reasons.append("high persona risk")
    if pressure >= 0.15:
        reasons.append("revision pressure")
    if record.status in {"review", "revise"}:
        reasons.append(f"status marked {record.status}")

    return reasons


def review_priority(record: PersonaRecord, risk: float, pressure: float) -> str:
    if record.status == "archive":
        return "archive review"
    if record.status == "revise" or risk >= 0.70:
        return "high"
    if (
        record.status == "review"
        or pressure >= 0.15
        or record.evidence_strength < 0.60
        or record.governance_readiness < 0.65
        or record.exclusion_risk >= 0.50
    ):
        return "medium"
    return "standard"


def score_record(record: PersonaRecord) -> AuditResult:
    risk = risk_score(record)
    pressure = revision_pressure(record)
    reasons = governance_reasons(record, risk, pressure)

    return AuditResult(
        persona=record.persona,
        segment=record.segment,
        description=record.description,
        content_pathway=record.content_pathway,
        owner=record.owner,
        status=record.status,
        review_date=record.review_date,
        evidence_strength=round_score(record.evidence_strength),
        specificity=round_score(record.specificity),
        content_fit=round_score(record.content_fit),
        segment_alignment=round_score(record.segment_alignment),
        governance_readiness=round_score(record.governance_readiness),
        stereotype_risk=round_score(record.stereotype_risk),
        exclusion_risk=round_score(record.exclusion_risk),
        weak_evidence_risk=round_score(record.weak_evidence_risk),
        overgeneralization_risk=round_score(record.overgeneralization_risk),
        risk_score=round_score(risk),
        readiness_score=round_score(readiness_score(record)),
        weighted_readiness=round_score(weighted_readiness(record)),
        revision_pressure=round_score(pressure),
        review_priority=review_priority(record, risk, pressure),
        governance_reasons="; ".join(reasons) if reasons else "no immediate governance issue",
    )
