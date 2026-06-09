"""Governance transformations for Framework Drift Catalyst Canvas exports."""

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
        "queue_id": f"framework-drift-repair-{slugify(result.item)}",
        "article_slug": "framework-drift-and-conceptual-decay",
        "item": result.item,
        "item_type": result.item_type,
        "owner": result.owner,
        "status": result.status,
        "review_date": result.review_date,
        "repair_priority": result.repair_priority,
        "conceptual_integrity": result.conceptual_integrity,
        "drift_risk": result.drift_risk,
        "repair_priority_score": result.repair_priority_score,
        "governance_reasons": result.governance_reasons,
        "recommended_action": result.recommended_action,
    }


def build_governance_queue(results: list[AuditResult]) -> list[dict[str, object]]:
    priority_rank = {"high": 0, "medium": 1, "archive review": 2, "standard": 3}

    queued = [
        queue_item(result)
        for result in results
        if result.repair_priority != "standard"
    ]

    return sorted(
        queued,
        key=lambda item: (
            priority_rank.get(str(item["repair_priority"]), 99),
            -float(item["repair_priority_score"]),
            -float(item["drift_risk"]),
            str(item["item"]),
        ),
    )
