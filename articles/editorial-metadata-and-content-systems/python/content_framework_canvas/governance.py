"""Governance queue builders for Content Frameworks Catalyst Canvas audits."""

from __future__ import annotations

from .models import AuditResult


def queue_item(result: AuditResult) -> dict[str, object]:
    return {
        "queue_id": f"{result.article_slug}-{result.record_id}",
        "article_slug": result.article_slug,
        "article_title": result.article_title,
        "canvas_dimension": result.canvas_dimension,
        "owner": result.owner,
        "status": result.status,
        "review_date": result.review_date,
        "review_priority": result.review_priority,
        "readiness_score": result.readiness_score,
        "governance_pressure": result.governance_pressure,
        "ethical_risk": result.ethical_risk,
        "governance_reasons": result.governance_reasons,
        "recommended_action": recommended_action(result),
    }


def recommended_action(result: AuditResult) -> str:
    if result.review_priority == "archive review":
        return "Review whether this record should be archived or preserved for history."
    if result.review_priority == "high":
        return "Revise before reuse in Catalyst Canvas."
    if result.review_priority == "medium":
        return "Review evidence, repository support, governance status, or ethical risk."
    return "Keep active and review during the next governance cycle."


def build_governance_queue(results: list[AuditResult]) -> list[dict[str, object]]:
    rank = {"high": 0, "medium": 1, "archive review": 2, "standard": 3}

    queued = [
        queue_item(result)
        for result in results
        if result.review_priority != "standard"
    ]

    return sorted(
        queued,
        key=lambda item: (
            rank.get(str(item["review_priority"]), 99),
            float(item["readiness_score"]),
            str(item["canvas_dimension"]),
        ),
    )
