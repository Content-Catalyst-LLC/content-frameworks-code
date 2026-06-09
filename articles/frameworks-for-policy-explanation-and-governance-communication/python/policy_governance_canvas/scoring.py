"""Scoring logic for policy explanation and governance communication diagnostics."""

from __future__ import annotations

from statistics import mean

from .models import AuditResult, PolicyGovernanceItem


def round_score(value: float) -> float:
    return round(value, 3)


def completeness_score(item: PolicyGovernanceItem) -> float:
    return mean([
        item.problem_clarity,
        item.authority_clarity,
        item.evidence_strength,
        item.stakeholder_visibility,
        item.implementation_detail,
        item.accountability_coverage,
        item.participation_clarity,
    ])


def evidence_gap(item: PolicyGovernanceItem) -> float:
    return max(0.0, item.claim_strength - item.evidence_strength)


def governance_risk(item: PolicyGovernanceItem) -> float:
    return min(
        1.0,
        (1.0 - item.accountability_coverage) * 0.25
        + (1.0 - item.stakeholder_visibility) * 0.20
        + (1.0 - item.evidence_strength) * 0.20
        + item.ambiguity * 0.20
        + (1.0 - item.implementation_detail) * 0.15,
    )


def review_priority_score(item: PolicyGovernanceItem) -> float:
    return min(
        1.0,
        evidence_gap(item) * 0.35
        + governance_risk(item) * 0.40
        + (1.0 - completeness_score(item)) * 0.25,
    )


def governance_reasons(item: PolicyGovernanceItem, gap: float, risk: float, priority: float) -> list[str]:
    reasons: list[str] = []

    if item.problem_clarity < 0.60:
        reasons.append("weak problem clarity")
    if item.authority_clarity < 0.60:
        reasons.append("weak authority clarity")
    if item.evidence_strength < 0.60:
        reasons.append("weak evidence strength")
    if item.stakeholder_visibility < 0.60:
        reasons.append("weak stakeholder visibility")
    if item.implementation_detail < 0.60:
        reasons.append("weak implementation detail")
    if item.accountability_coverage < 0.60:
        reasons.append("weak accountability coverage")
    if item.participation_clarity < 0.60:
        reasons.append("weak participation clarity")
    if item.ambiguity >= 0.60:
        reasons.append("high ambiguity")
    if gap >= 0.15:
        reasons.append("evidence gap")
    if risk >= 0.55:
        reasons.append("high governance communication risk")
    if priority >= 0.45:
        reasons.append("review priority threshold reached")
    if item.status in {"review", "revise"}:
        reasons.append(f"status marked {item.status}")
    if len(item.description.split()) < 7:
        reasons.append("description may be too vague")

    return reasons


def recommended_action(item: PolicyGovernanceItem, gap: float, risk: float, priority: float) -> str:
    if item.status == "archive":
        return "Review whether this policy explanation item should be archived or retained for historical context."
    if item.status == "revise" or gap >= 0.30:
        return "Revise this item before publication and strengthen evidence accountability stakeholder visibility and implementation detail."
    if risk >= 0.55 or priority >= 0.45:
        return "Review authority evidence stakeholder impact participation accountability and ambiguity before publication."
    return "Keep active and review during the next policy communication governance cycle."


def review_priority(item: PolicyGovernanceItem, gap: float, risk: float, priority: float) -> str:
    if item.status == "archive":
        return "archive review"
    if item.status == "revise" or gap >= 0.30:
        return "high"
    if priority >= 0.45 or risk >= 0.55 or gap >= 0.15 or item.status == "review":
        return "medium"
    return "standard"


def score_item(item: PolicyGovernanceItem) -> AuditResult:
    gap = evidence_gap(item)
    risk = governance_risk(item)
    priority = review_priority_score(item)
    reasons = governance_reasons(item, gap, risk, priority)

    return AuditResult(
        item=item.item,
        policy_area=item.policy_area,
        description=item.description,
        owner=item.owner,
        status=item.status,
        review_date=item.review_date,
        problem_clarity=round_score(item.problem_clarity),
        authority_clarity=round_score(item.authority_clarity),
        evidence_strength=round_score(item.evidence_strength),
        stakeholder_visibility=round_score(item.stakeholder_visibility),
        implementation_detail=round_score(item.implementation_detail),
        accountability_coverage=round_score(item.accountability_coverage),
        participation_clarity=round_score(item.participation_clarity),
        ambiguity=round_score(item.ambiguity),
        claim_strength=round_score(item.claim_strength),
        completeness_score=round_score(completeness_score(item)),
        evidence_gap=round_score(gap),
        governance_risk=round_score(risk),
        review_priority_score=round_score(priority),
        review_priority=review_priority(item, gap, risk, priority),
        governance_reasons="; ".join(reasons) if reasons else "no immediate governance issue",
        recommended_action=recommended_action(item, gap, risk, priority),
    )
