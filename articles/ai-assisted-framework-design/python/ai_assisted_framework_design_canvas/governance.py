"""Governance transformations for AI-Assisted Framework Design Catalyst Canvas exports."""

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
        "queue_id": f"ai-assisted-framework-governance-{slugify(result.item)}",
        "article_slug": "ai-assisted-framework-design",
        "item": result.item,
        "item_type": result.item_type,
        "owner": result.owner,
        "status": result.status,
        "review_date": result.review_date,
        "governance_priority": result.governance_priority,
        "readiness_score": result.readiness_score,
        "ai_framework_risk": result.ai_framework_risk,
        "governance_priority_score": result.governance_priority_score,
        "governance_reasons": result.governance_reasons,
        "recommended_action": result.recommended_action,
    }


def build_governance_queue(results: list[AuditResult]) -> list[dict[str, object]]:
    priority_rank = {"high": 0, "medium": 1, "archive review": 2, "standard": 3}

    queued = [
        queue_item(result)
        for result in results
        if result.governance_priority != "standard"
    ]

    return sorted(
        queued,
        key=lambda item: (
            priority_rank.get(str(item["governance_priority"]), 99),
            -float(item["governance_priority_score"]),
            -float(item["ai_framework_risk"]),
            str(item["item"]),
        ),
    )
