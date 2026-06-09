"""Scoring logic for OKRs KPIs Measurement Frameworks Catalyst Canvas diagnostics."""

from __future__ import annotations

from statistics import mean

from .models import AuditResult, MeasurementItem


def round_score(value: float) -> float:
    return round(value, 3)


def quality_score(item: MeasurementItem) -> float:
    return mean([
        item.validity,
        item.reliability,
        item.strategic_relevance,
        item.actionability,
        item.timeliness,
    ])


def measurement_risk(item: MeasurementItem) -> float:
    return min(
        1.0,
        item.gaming_risk * 0.30
        + item.ambiguity * 0.25
        + item.reporting_burden * 0.20
        + (1.0 - item.evidence_strength) * 0.25,
    )


def evidence_gap(item: MeasurementItem) -> float:
    return max(0.0, item.claim_strength - item.evidence_strength)


def governance_priority(item: MeasurementItem) -> float:
    return min(
        1.0,
        measurement_risk(item) * 0.40
        + evidence_gap(item) * 0.30
        + (1.0 - quality_score(item)) * 0.30,
    )


def governance_reasons(item: MeasurementItem, gap: float, risk: float, priority: float) -> list[str]:
    reasons: list[str] = []

    if item.validity < 0.60:
        reasons.append("low validity")
    if item.actionability < 0.60:
        reasons.append("low actionability")
    if item.evidence_strength < 0.60:
        reasons.append("weak evidence strength")
    if item.gaming_risk >= 0.60:
        reasons.append("high gaming risk")
    if item.ambiguity >= 0.55:
        reasons.append("high ambiguity")
    if item.reporting_burden >= 0.55:
        reasons.append("high reporting burden")
    if gap >= 0.15:
        reasons.append("evidence gap")
    if risk >= 0.55:
        reasons.append("high measurement risk")
    if priority >= 0.45:
        reasons.append("governance review needed")
    if item.status in {"review", "revise"}:
        reasons.append(f"status marked {item.status}")
    if len(item.description.split()) < 7:
        reasons.append("description may be too vague")

    return reasons


def recommended_action(item: MeasurementItem, gap: float, risk: float, priority: float) -> str:
    if item.status == "archive":
        return "Review whether this measurement item should be archived or retained for historical context."
    if item.status == "revise" or gap >= 0.30:
        return "Revise this measurement item before reuse and strengthen definition evidence and governance logic."
    if priority >= 0.45 or risk >= 0.55:
        return "Review metric definition evidence source incentive risk owner threshold and action pathway."
    return "Keep active and review during the next measurement governance cycle."


def review_priority(item: MeasurementItem, gap: float, risk: float, priority: float) -> str:
    if item.status == "archive":
        return "archive review"
    if item.status == "revise" or gap >= 0.30:
        return "high"
    if priority >= 0.45 or risk >= 0.55 or gap >= 0.15 or item.status == "review":
        return "medium"
    return "standard"


def score_item(item: MeasurementItem) -> AuditResult:
    gap = evidence_gap(item)
    risk = measurement_risk(item)
    priority = governance_priority(item)
    reasons = governance_reasons(item, gap, risk, priority)

    return AuditResult(
        item=item.item,
        measurement_type=item.measurement_type,
        description=item.description,
        owner=item.owner,
        status=item.status,
        review_date=item.review_date,
        strategic_relevance=round_score(item.strategic_relevance),
        validity=round_score(item.validity),
        reliability=round_score(item.reliability),
        actionability=round_score(item.actionability),
        timeliness=round_score(item.timeliness),
        evidence_strength=round_score(item.evidence_strength),
        gaming_risk=round_score(item.gaming_risk),
        reporting_burden=round_score(item.reporting_burden),
        ambiguity=round_score(item.ambiguity),
        claim_strength=round_score(item.claim_strength),
        quality_score=round_score(quality_score(item)),
        measurement_risk=round_score(risk),
        evidence_gap=round_score(gap),
        governance_priority=round_score(priority),
        review_priority=review_priority(item, gap, risk, priority),
        governance_reasons="; ".join(reasons) if reasons else "no immediate governance issue",
        recommended_action=recommended_action(item, gap, risk, priority),
    )
