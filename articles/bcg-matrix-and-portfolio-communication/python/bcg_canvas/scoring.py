"""Scoring logic for BCG Matrix Catalyst Canvas diagnostics."""

from __future__ import annotations

from .models import AuditResult, PortfolioItem


GROWTH_THRESHOLD = 0.60
SHARE_THRESHOLD = 0.60


def round_score(value: float) -> float:
    return round(value, 3)


def quadrant(item: PortfolioItem) -> str:
    if item.growth_score >= GROWTH_THRESHOLD and item.relative_share_score >= SHARE_THRESHOLD:
        return "star"
    if item.growth_score < GROWTH_THRESHOLD and item.relative_share_score >= SHARE_THRESHOLD:
        return "cash_cow"
    if item.growth_score >= GROWTH_THRESHOLD and item.relative_share_score < SHARE_THRESHOLD:
        return "question_mark"
    return "review_quadrant"


def evidence_gap(item: PortfolioItem) -> float:
    return max(0.0, item.claim_strength - item.evidence_strength)


def quadrant_weight(value: str) -> float:
    return {
        "star": 0.85,
        "cash_cow": 0.60,
        "question_mark": 0.78,
        "review_quadrant": 0.70,
    }[value]


def portfolio_priority(item: PortfolioItem) -> float:
    q = quadrant(item)
    return min(
        1.0,
        quadrant_weight(q) * 0.35
        + item.strategic_fit * 0.30
        + item.maintenance_burden * 0.15
        + evidence_gap(item) * 0.20,
    )


def recommended_action(item: PortfolioItem) -> str:
    q = quadrant(item)
    if q == "star":
        return "invest and defend position with evidence updates and governance support"
    if q == "cash_cow":
        return "maintain stable value with scheduled review and selective refresh"
    if q == "question_mark":
        return "test with explicit evidence thresholds before major investment"
    return "review for consolidation repositioning preservation or retirement"


def governance_reasons(item: PortfolioItem, gap: float, priority: float) -> list[str]:
    reasons: list[str] = []
    q = quadrant(item)

    if q == "review_quadrant":
        reasons.append("review quadrant")
    if item.evidence_strength < 0.60:
        reasons.append("weak evidence strength")
    if item.strategic_fit < 0.60:
        reasons.append("low strategic fit")
    if item.maintenance_burden >= 0.65:
        reasons.append("high maintenance burden")
    if gap >= 0.15:
        reasons.append("evidence gap")
    if priority >= 0.70:
        reasons.append("high portfolio communication priority")
    if item.status in {"review", "revise"}:
        reasons.append(f"status marked {item.status}")
    if len(item.description.split()) < 7:
        reasons.append("description may be too vague")

    return reasons


def review_priority(item: PortfolioItem, gap: float, priority: float) -> str:
    if item.status == "archive":
        return "archive review"
    if item.status == "revise" or gap >= 0.30:
        return "high"
    if priority >= 0.70 or gap >= 0.15 or item.status == "review":
        return "medium"
    return "standard"


def score_item(item: PortfolioItem) -> AuditResult:
    gap = evidence_gap(item)
    priority = portfolio_priority(item)
    reasons = governance_reasons(item, gap, priority)

    return AuditResult(
        item=item.item,
        portfolio_area=item.portfolio_area,
        description=item.description,
        owner=item.owner,
        status=item.status,
        review_date=item.review_date,
        growth_score=round_score(item.growth_score),
        relative_share_score=round_score(item.relative_share_score),
        evidence_strength=round_score(item.evidence_strength),
        strategic_fit=round_score(item.strategic_fit),
        maintenance_burden=round_score(item.maintenance_burden),
        claim_strength=round_score(item.claim_strength),
        quadrant=quadrant(item),
        evidence_gap=round_score(gap),
        portfolio_priority=round_score(priority),
        review_priority=review_priority(item, gap, priority),
        recommended_action=recommended_action(item),
        governance_reasons="; ".join(reasons) if reasons else "no immediate governance issue",
    )
