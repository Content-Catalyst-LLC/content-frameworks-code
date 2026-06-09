"""Governance transformations for SWOT Analysis Catalyst Canvas exports."""

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


def recommended_action(result: AuditResult) -> str:
    if result.review_priority == "archive review":
        return "Review whether this SWOT item should be archived or retained for historical context."
    if result.review_priority == "high":
        return "Revise this SWOT item before reuse and strengthen evidence specificity or action logic."
    if result.review_priority == "medium":
        return "Review evidence support confidence feasibility and strategic action implications."
    return "Keep active and review during the next governance cycle."


def queue_item(result: AuditResult) -> dict[str, object]:
    return {
        "queue_id": f"swot-review-{slugify(result.item)}",
        "article_slug": "swot-analysis-strengths-uses-and-limits",
        "item": result.item,
        "quadrant": result.quadrant,
        "orientation": result.orientation,
        "owner": result.owner,
        "status": result.status,
        "review_date": result.review_date,
        "review_priority": result.review_priority,
        "weighted_priority": result.weighted_priority,
        "evidence_gap": result.evidence_gap,
        "governance_priority": result.governance_priority,
        "governance_reasons": result.governance_reasons,
        "recommended_action": recommended_action(result),
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
            -float(item["governance_priority"]),
            -float(item["evidence_gap"]),
            str(item["item"]),
        ),
    )
