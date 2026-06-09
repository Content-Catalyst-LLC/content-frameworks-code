"""Governance transformations for Policy Governance Catalyst Canvas exports."""

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
        "queue_id": f"policy-governance-review-{slugify(result.item)}",
        "article_slug": "frameworks-for-policy-explanation-and-governance-communication",
        "item": result.item,
        "policy_area": result.policy_area,
        "owner": result.owner,
        "status": result.status,
        "review_date": result.review_date,
        "review_priority": result.review_priority,
        "completeness_score": result.completeness_score,
        "evidence_gap": result.evidence_gap,
        "governance_risk": result.governance_risk,
        "review_priority_score": result.review_priority_score,
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
            -float(item["review_priority_score"]),
            -float(item["governance_risk"]),
            str(item["item"]),
        ),
    )
