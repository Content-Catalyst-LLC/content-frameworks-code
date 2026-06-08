"""Governance transformations for Catalyst Canvas exports."""

from __future__ import annotations

from .models import AuditResult


def queue_item(result: AuditResult) -> dict[str, object]:
    return {
        "queue_id": f"stp-review-{slugify(result.segment)}",
        "article_slug": "stp-segmentation-targeting-and-positioning",
        "segment": result.segment,
        "owner": result.owner,
        "status": result.status,
        "review_date": result.review_date,
        "review_priority": result.review_priority,
        "ethical_review_flag": result.ethical_review_flag,
        "positioning_gap": result.positioning_gap,
        "governance_score": result.governance_score,
        "governance_reasons": result.governance_reasons,
        "recommended_action": recommended_action(result),
    }


def recommended_action(result: AuditResult) -> str:
    if result.review_priority == "archive review":
        return "Review whether this segment should be retired or retained for historical context."
    if result.review_priority == "high":
        return "Revise positioning, evidence support, and ethical framing before reuse."
    if result.review_priority == "medium":
        return "Add evidence, clarify positioning, or review exclusion/stereotype risk."
    return "Keep active and review during the next governance cycle."


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
            -float(item["positioning_gap"]),
            str(item["segment"]),
        ),
    )


def slugify(value: str) -> str:
    return (
        value.strip()
        .lower()
        .replace("&", "and")
        .replace("/", "-")
        .replace(" ", "-")
        .replace("_", "-")
    )
