"""Governance transformations for Audience Journey Catalyst Canvas exports."""

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
    )


def recommended_action(result: AuditResult) -> str:
    if result.review_priority == "archive review":
        return "Review whether this journey stage should be archived or retained for historical context."
    if result.review_priority == "high":
        return "Revise this journey stage before reuse and repair content coverage links evidence or governance."
    if result.review_priority == "medium":
        return "Review missing links evidence readiness transition quality persona fit or staleness risk."
    return "Keep active and review during the next governance cycle."


def queue_item(result: AuditResult) -> dict[str, object]:
    return {
        "queue_id": f"journey-review-{slugify(result.stage)}",
        "article_slug": "audience-journey-frameworks-and-content-sequencing",
        "stage": result.stage,
        "journey_type": result.journey_type,
        "audience_need": result.audience_need,
        "owner": result.owner,
        "status": result.status,
        "review_date": result.review_date,
        "review_priority": result.review_priority,
        "link_gap": result.link_gap,
        "journey_risk": result.journey_risk,
        "persona_mismatch": result.persona_mismatch,
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
            -int(item["link_gap"]),
            -float(item["journey_risk"]),
            str(item["stage"]),
        ),
    )
