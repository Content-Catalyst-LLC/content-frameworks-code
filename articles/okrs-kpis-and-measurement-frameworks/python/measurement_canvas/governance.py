"""Governance transformations for OKRs KPIs Measurement Frameworks Canvas exports."""

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
        "queue_id": f"measurement-review-{slugify(result.item)}",
        "article_slug": "okrs-kpis-and-measurement-frameworks",
        "item": result.item,
        "measurement_type": result.measurement_type,
        "owner": result.owner,
        "status": result.status,
        "review_date": result.review_date,
        "review_priority": result.review_priority,
        "quality_score": result.quality_score,
        "measurement_risk": result.measurement_risk,
        "evidence_gap": result.evidence_gap,
        "governance_priority": result.governance_priority,
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
            -float(item["governance_priority"]),
            -float(item["measurement_risk"]),
            str(item["item"]),
        ),
    )
