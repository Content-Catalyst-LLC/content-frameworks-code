"""Governance transformations for Message House Catalyst Canvas exports."""

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
        return "Review whether this message pillar should be retired or retained for historical context."
    if result.review_priority == "high":
        return "Revise the message pillar before reuse and strengthen proof or ethical framing."
    if result.review_priority == "medium":
        return "Review evidence strength governance readiness audience relevance or drift risk."
    return "Keep active and review during the next governance cycle."


def queue_item(result: AuditResult) -> dict[str, object]:
    return {
        "queue_id": f"message-house-review-{slugify(result.pillar)}",
        "article_slug": "message-house-and-the-architecture-of-strategic-messaging",
        "pillar": result.pillar,
        "owner": result.owner,
        "status": result.status,
        "review_date": result.review_date,
        "review_priority": result.review_priority,
        "proof_gap": result.proof_gap,
        "message_drift_risk": result.message_drift_risk,
        "ethical_risk": result.ethical_risk,
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
            -float(item["proof_gap"]),
            str(item["pillar"]),
        ),
    )
