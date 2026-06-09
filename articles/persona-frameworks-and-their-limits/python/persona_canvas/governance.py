"""Governance transformations for Persona Frameworks Catalyst Canvas exports."""

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
        return "Review whether this persona should be archived or retained for historical context."
    if result.review_priority == "high":
        return "Revise persona before reuse and strengthen evidence scope representation or governance."
    if result.review_priority == "medium":
        return "Review evidence strength segment alignment stereotype risk exclusion risk or governance readiness."
    return "Keep active and review during the next governance cycle."


def queue_item(result: AuditResult) -> dict[str, object]:
    return {
        "queue_id": f"persona-review-{slugify(result.persona)}",
        "article_slug": "persona-frameworks-and-their-limits",
        "persona": result.persona,
        "segment": result.segment,
        "content_pathway": result.content_pathway,
        "owner": result.owner,
        "status": result.status,
        "review_date": result.review_date,
        "review_priority": result.review_priority,
        "risk_score": result.risk_score,
        "revision_pressure": result.revision_pressure,
        "evidence_strength": result.evidence_strength,
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
            -float(item["risk_score"]),
            -float(item["revision_pressure"]),
            str(item["persona"]),
        ),
    )
