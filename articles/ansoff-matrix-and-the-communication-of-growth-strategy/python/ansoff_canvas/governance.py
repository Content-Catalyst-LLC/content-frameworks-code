"""Governance transformations for Ansoff Matrix Catalyst Canvas exports."""

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


def recommended_action(result: AuditResult) -> str:
    if result.review_priority == "archive review":
        return "Review whether this growth option should be archived or retained for historical context."
    if result.review_priority == "high":
        return "Revise this growth option before reuse and strengthen evidence, market definition, and feasibility logic."
    if result.review_priority == "medium":
        return "Review evidence, risk, feasibility, capability readiness, and communication framing before public use."
    return "Keep active and review during the next growth-strategy governance cycle."


def queue_item(result: AuditResult) -> dict[str, object]:
    return {
        "queue_id": f"ansoff-review-{slugify(result.option)}",
        "article_slug": "ansoff-matrix-and-the-communication-of-growth-strategy",
        "option": result.option,
        "growth_path": result.growth_path,
        "market_status": result.market_status,
        "product_status": result.product_status,
        "owner": result.owner,
        "status": result.status,
        "review_date": result.review_date,
        "review_priority": result.review_priority,
        "readiness_score": result.readiness_score,
        "risk_score": result.risk_score,
        "evidence_gap": result.evidence_gap,
        "growth_quality": result.growth_quality,
        "governance_priority": result.governance_priority,
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
            -float(item["governance_priority"]),
            -float(item["risk_score"]),
            str(item["option"]),
        ),
    )
