"""Governance transformations for Positioning Frameworks Catalyst Canvas exports."""

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
        return "Review whether this positioning record should be archived or retained for historical context."
    if result.review_priority == "high":
        return "Revise positioning before reuse and strengthen category frame evidence boundaries or ethics."
    if result.review_priority == "medium":
        return "Review category clarity evidence support boundary language drift risk or governance readiness."
    return "Keep active and review during the next governance cycle."


def queue_item(result: AuditResult) -> dict[str, object]:
    return {
        "queue_id": f"positioning-review-{slugify(result.idea)}",
        "article_slug": "positioning-frameworks-for-complex-ideas",
        "idea": result.idea,
        "category_frame": result.category_frame,
        "audience_pathway": result.audience_pathway,
        "owner": result.owner,
        "status": result.status,
        "review_date": result.review_date,
        "review_priority": result.review_priority,
        "evidence_gap": result.evidence_gap,
        "drift_risk": result.drift_risk,
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
            -float(item["evidence_gap"]),
            -float(item["drift_risk"]),
            str(item["idea"]),
        ),
    )
