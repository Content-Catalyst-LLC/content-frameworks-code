"""Scoring logic for sustainability communication claim governance."""

from __future__ import annotations

from statistics import mean

from .models import AuditResult, SustainabilityClaim


def round_score(value: float) -> float:
    return round(value, 3)


def quality_score(claim: SustainabilityClaim) -> float:
    return mean([
        claim.claim_specificity,
        claim.boundary_clarity,
        claim.evidence_strength,
        claim.materiality_relevance,
        claim.stakeholder_visibility,
        claim.accountability_coverage,
    ])


def evidence_gap(claim: SustainabilityClaim) -> float:
    return max(0.0, claim.claim_strength - claim.evidence_strength)


def greenwashing_risk(claim: SustainabilityClaim) -> float:
    vagueness = 1.0 - claim.claim_specificity
    return min(
        1.0,
        vagueness * 0.25
        + (1.0 - claim.evidence_strength) * 0.25
        + (1.0 - claim.boundary_clarity) * 0.20
        + (1.0 - claim.accountability_coverage) * 0.15
        + claim.promotional_intensity * 0.15,
    )


def review_priority_score(claim: SustainabilityClaim) -> float:
    return min(
        1.0,
        evidence_gap(claim) * 0.35
        + greenwashing_risk(claim) * 0.40
        + (1.0 - claim.stakeholder_visibility) * 0.15
        + (1.0 - claim.uncertainty_disclosure) * 0.10,
    )


def governance_reasons(claim: SustainabilityClaim, gap: float, risk: float, priority: float) -> list[str]:
    reasons: list[str] = []

    if claim.claim_specificity < 0.60:
        reasons.append("vague claim")
    if claim.boundary_clarity < 0.60:
        reasons.append("weak boundary clarity")
    if claim.evidence_strength < 0.60:
        reasons.append("weak evidence strength")
    if claim.materiality_relevance < 0.60:
        reasons.append("weak materiality relevance")
    if claim.stakeholder_visibility < 0.60:
        reasons.append("weak stakeholder visibility")
    if claim.accountability_coverage < 0.60:
        reasons.append("weak accountability coverage")
    if claim.uncertainty_disclosure < 0.60:
        reasons.append("weak uncertainty disclosure")
    if claim.promotional_intensity >= 0.65:
        reasons.append("high promotional intensity")
    if gap >= 0.15:
        reasons.append("evidence gap")
    if risk >= 0.55:
        reasons.append("greenwashing risk")
    if priority >= 0.45:
        reasons.append("review priority threshold reached")
    if claim.status in {"review", "revise"}:
        reasons.append(f"status marked {claim.status}")
    if len(claim.description.split()) < 7:
        reasons.append("description may be too vague")

    return reasons


def recommended_action(claim: SustainabilityClaim, gap: float, risk: float, priority: float) -> str:
    if claim.status == "archive":
        return "Review whether this sustainability claim should be archived or retained for historical context."
    if claim.status == "revise" or gap >= 0.30:
        return "Revise this claim before publication and strengthen boundary evidence stakeholder visibility accountability and uncertainty disclosure."
    if risk >= 0.55 or priority >= 0.45:
        return "Review claim wording evidence boundary materiality stakeholder impacts and greenwashing risk before publication."
    return "Keep active and review during the next sustainability communication governance cycle."


def review_priority(claim: SustainabilityClaim, gap: float, risk: float, priority: float) -> str:
    if claim.status == "archive":
        return "archive review"
    if claim.status == "revise" or gap >= 0.30:
        return "high"
    if priority >= 0.45 or risk >= 0.55 or gap >= 0.15 or claim.status == "review":
        return "medium"
    return "standard"


def score_claim(claim: SustainabilityClaim) -> AuditResult:
    gap = evidence_gap(claim)
    risk = greenwashing_risk(claim)
    priority = review_priority_score(claim)
    reasons = governance_reasons(claim, gap, risk, priority)

    return AuditResult(
        claim=claim.claim,
        claim_type=claim.claim_type,
        description=claim.description,
        owner=claim.owner,
        status=claim.status,
        review_date=claim.review_date,
        claim_specificity=round_score(claim.claim_specificity),
        boundary_clarity=round_score(claim.boundary_clarity),
        evidence_strength=round_score(claim.evidence_strength),
        materiality_relevance=round_score(claim.materiality_relevance),
        stakeholder_visibility=round_score(claim.stakeholder_visibility),
        accountability_coverage=round_score(claim.accountability_coverage),
        uncertainty_disclosure=round_score(claim.uncertainty_disclosure),
        promotional_intensity=round_score(claim.promotional_intensity),
        claim_strength=round_score(claim.claim_strength),
        quality_score=round_score(quality_score(claim)),
        evidence_gap=round_score(gap),
        greenwashing_risk=round_score(risk),
        review_priority_score=round_score(priority),
        review_priority=review_priority(claim, gap, risk, priority),
        governance_reasons="; ".join(reasons) if reasons else "no immediate governance issue",
        recommended_action=recommended_action(claim, gap, risk, priority),
    )
