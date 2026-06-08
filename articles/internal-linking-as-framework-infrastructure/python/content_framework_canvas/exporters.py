"""Export utilities for generic Content Frameworks Catalyst Canvas audits."""

from __future__ import annotations

from datetime import datetime, timezone
import csv
import json
from pathlib import Path

from . import ARTICLE_SLUG, ARTICLE_TITLE, MODULE_NAME, __version__
from .governance import build_governance_queue
from .models import AuditResult


def generated_at() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_canvas_cards(results: list[AuditResult]) -> list[dict[str, object]]:
    cards: list[dict[str, object]] = []

    for result in results:
        cards.append({
            "card_id": f"{result.article_slug}-{result.record_id}",
            "type": "content_framework_canvas_dimension",
            "article_slug": result.article_slug,
            "title": result.canvas_dimension,
            "subtitle": result.article_title,
            "description": result.description,
            "badges": [
                f"readiness: {result.readiness_score}",
                f"priority: {result.review_priority}",
                result.status,
            ],
            "metrics": {
                "content_score": result.content_score,
                "audience_score": result.audience_score,
                "evidence_score": result.evidence_score,
                "repository_score": result.repository_score,
                "governance_pressure": result.governance_pressure,
                "ethical_risk": result.ethical_risk,
                "readiness_score": result.readiness_score,
            },
            "governance": {
                "owner": result.owner,
                "status": result.status,
                "review_date": result.review_date,
                "review_priority": result.review_priority,
                "reasons": result.governance_reasons,
            },
        })

    return cards


def build_catalog(results: list[AuditResult]) -> dict[str, object]:
    readiness_values = [result.readiness_score for result in results]
    average_readiness = round(sum(readiness_values) / len(readiness_values), 3) if readiness_values else 0.0

    return {
        "module": MODULE_NAME,
        "version": __version__,
        "article_slug": ARTICLE_SLUG,
        "article_title": ARTICLE_TITLE,
        "generated_at": generated_at(),
        "record_count": len(results),
        "average_readiness_score": average_readiness,
        "metrics": [
            "content_score",
            "audience_score",
            "evidence_score",
            "repository_score",
            "governance_pressure",
            "ethical_risk",
            "readiness_score",
        ],
        "outputs": {
            "audit_table": "outputs/tables/article_canvas_audit.csv",
            "canvas_cards": "canvas/canvas_cards.json",
            "governance_queue": "canvas/governance_queue.json",
            "full_export": "outputs/json/article_canvas_export.json",
        },
    }


def build_full_export(results: list[AuditResult]) -> dict[str, object]:
    governance_queue = build_governance_queue(results)
    cards = build_canvas_cards(results)

    return {
        "module": MODULE_NAME,
        "version": __version__,
        "article_slug": ARTICLE_SLUG,
        "article_title": ARTICLE_TITLE,
        "generated_at": generated_at(),
        "results": [result.to_dict() for result in results],
        "governance_queue": governance_queue,
        "canvas_cards": cards,
    }


def write_markdown_queue(path: Path, queue: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        f"# Catalyst Canvas Governance Queue: {ARTICLE_TITLE}",
        "",
        "Generated review queue for Canvas readiness across content value, audience value, evidence strength, repository support, governance pressure, and ethical risk.",
        "",
    ]

    if not queue:
        lines.append("No governance queue items were generated.")
    else:
        for item in queue:
            lines.extend([
                f"## {item['canvas_dimension']}",
                "",
                f"- Priority: {item['review_priority']}",
                f"- Owner: {item['owner']}",
                f"- Status: {item['status']}",
                f"- Review date: {item['review_date']}",
                f"- Readiness score: {item['readiness_score']}",
                f"- Governance pressure: {item['governance_pressure']}",
                f"- Ethical risk: {item['ethical_risk']}",
                f"- Reasons: {item['governance_reasons']}",
                f"- Recommended action: {item['recommended_action']}",
                "",
            ])

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def export_all(article_root: Path, results: list[AuditResult]) -> None:
    result_dicts = [result.to_dict() for result in results]
    governance_queue = build_governance_queue(results)
    cards = build_canvas_cards(results)
    catalog = build_catalog(results)
    full_export = build_full_export(results)

    write_csv(article_root / "outputs" / "tables" / "article_canvas_audit.csv", result_dicts)
    write_json(article_root / "outputs" / "json" / "catalog.json", catalog)
    write_json(article_root / "outputs" / "json" / "governance_queue.json", governance_queue)
    write_json(article_root / "outputs" / "json" / "canvas_cards.json", cards)
    write_json(article_root / "outputs" / "json" / "article_canvas_export.json", full_export)
    write_json(article_root / "canvas" / "governance_queue.json", governance_queue)
    write_json(article_root / "canvas" / "canvas_cards.json", cards)
    write_markdown_queue(article_root / "outputs" / "markdown" / "governance_queue.md", governance_queue)
