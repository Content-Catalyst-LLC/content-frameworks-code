"""Governance transformations for BCG Matrix Catalyst Canvas exports."""

from __future__ import annotations

from .models import AuditResult


def slugify(value: str) -> str:
    return (
        value.strip()
        .lower()
        .replace("&", "and")
        .replace("/", "-")
        .replace(" ", "-")
        .replace("_", "-")
        .replace(":", "")
    )


def queue_item(result: AuditResult) -> dict[str, object]:
    return {
        "queue_id": f"bcg-review-{slugify(result.item)}",
        "article_slug": "bcg-matrix-and-portfolio-communication",
        "item": result.item,
        "portfolio_area": result.portfolio_area,
        "quadrant": result.quadrant,
        "owner": result.owner,
        "status": result.status,
        "review_date": result.review_date,
        "review_priority": result.review_priority,
        "growth_score": result.growth_score,
        "relative_share_score": result.relative_share_score,
        "evidence_gap": result.evidence_gap,
        "portfolio_priority": result.portfolio_priority,
        "governance_reasons": result.governance_reasons,
        "recommended_action": result.recommended_action,
    }


def build_governance_queue(results: list[AuditResult]) -> list[dict[str, object]]:
    priority_rank = {"high": 0, "medium": 1, "archive review": 2, "standard": 3}

    queued = [
        queue_item(result)
        for result in results
        if result.review_priority != "standard"
    ]

    return sorted(
        queued,
        key=lambda item: (
            priority_rank.get(str(item["review_priority"]), 99),
            -float(item["portfolio_priority"]),
            -float(item["evidence_gap"]),
            str(item["item"]),
        ),
    )
