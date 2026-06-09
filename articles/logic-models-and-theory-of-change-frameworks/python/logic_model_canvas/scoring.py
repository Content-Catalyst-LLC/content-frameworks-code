# Scoring logic for logic-model and Theory of Change diagnostics.

from __future__ import annotations

from statistics import mean

from .models import AuditResult, LogicModelElement


def round_score(value: float) -> float:
    return round(value, 3)


def assumption_risk(element: LogicModelElement) -> float:
    return element.assumption_importance * (1.0 - element.assumption_evidence)


def evidence_gap(element: LogicModelElement) -> float:
    return max(0.0, element.claim_strength - element.evidence_strength)


def pathway_quality(element: LogicModelElement) -> float:
    return mean([
        element.evidence_strength,
        element.assumption_evidence,
        element.measurement_coverage,
        element.outcome_clarity,
    ])


def governance_priority(element: LogicModelElement) -> float:
    return min(
        1.0,
        evidence_gap(element) * 0.35
        + assumption_risk(element) * 0.35
        + (1.0 - element.measurement_coverage) * 0.20
        + (1.0 - element.outcome_clarity) * 0.10,
    )


def governance_reasons(element: LogicModelElement, gap: float, risk: float, priority: float) -> list[str]:
    reasons: list[str] = []
    if element.evidence_strength < 0.60:
        reasons.append("weak evidence strength")
    if element.assumption_evidence < 0.60:
        reasons.append("weak assumption evidence")
    if element.measurement_coverage < 0.60:
        reasons.append("weak measurement coverage")
    if element.outcome_clarity < 0.60:
        reasons.append("unclear outcome or impact claim")
    if risk >= 0.40:
        reasons.append("high assumption risk")
    if gap >= 0.15:
        reasons.append("evidence gap")
    if element.model_layer == "impact" and element.evidence_strength < 0.60:
        reasons.append("unsupported impact claim")
    if priority >= 0.45:
        reasons.append("governance review needed")
    if element.status in {"review", "revise"}:
        reasons.append(f"status marked {element.status}")
    if len(element.description.split()) < 7:
        reasons.append("description may be too vague")
    return reasons


def recommended_action(element: LogicModelElement, gap: float, risk: float, priority: float) -> str:
    if element.status == "archive":
        return "Review whether this logic-model element should be archived or retained for historical context."
    if element.status == "revise" or gap >= 0.30:
        return "Revise this causal claim before reuse and strengthen evidence assumptions measurement coverage and outcome clarity."
    if risk >= 0.40 or priority >= 0.45:
        return "Review assumptions evidence indicators stakeholders and failure points before using this pathway in communication."
    return "Keep active and review during the next causal-framework governance cycle."


def review_priority(element: LogicModelElement, gap: float, risk: float, priority: float) -> str:
    if element.status == "archive":
        return "archive review"
    if element.status == "revise" or gap >= 0.30:
        return "high"
    if priority >= 0.45 or risk >= 0.40 or gap >= 0.15 or element.status == "review":
        return "medium"
    return "standard"


def score_element(element: LogicModelElement) -> AuditResult:
    gap = evidence_gap(element)
    risk = assumption_risk(element)
    priority = governance_priority(element)
    reasons = governance_reasons(element, gap, risk, priority)
    return AuditResult(
        element=element.element,
        model_layer=element.model_layer,
        description=element.description,
        owner=element.owner,
        status=element.status,
        review_date=element.review_date,
        evidence_strength=round_score(element.evidence_strength),
        assumption_importance=round_score(element.assumption_importance),
        assumption_evidence=round_score(element.assumption_evidence),
        measurement_coverage=round_score(element.measurement_coverage),
        outcome_clarity=round_score(element.outcome_clarity),
        claim_strength=round_score(element.claim_strength),
        assumption_risk=round_score(risk),
        evidence_gap=round_score(gap),
        pathway_quality=round_score(pathway_quality(element)),
        governance_priority=round_score(priority),
        review_priority=review_priority(element, gap, risk, priority),
        governance_reasons="; ".join(reasons) if reasons else "no immediate governance issue",
        recommended_action=recommended_action(element, gap, risk, priority),
    )
