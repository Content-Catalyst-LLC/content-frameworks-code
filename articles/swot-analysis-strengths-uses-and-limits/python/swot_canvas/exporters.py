"""Export utilities for SWOT Analysis Catalyst Canvas integration."""

from __future__ import annotations

from datetime import datetime, timezone
import csv
import json
from pathlib import Path

from . import ARTICLE_SLUG, ARTICLE_TITLE, MODULE_NAME, __version__
from .governance import build_governance_queue, recommended_action, slugify
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
            "card_id": f"swot-item-{slugify(result.item)}",
            "type": "swot_item_card",
            "article_slug": ARTICLE_SLUG,
            "title": result.item,
            "subtitle": f"{result.quadrant} / {result.orientation}",
            "description": result.description,
            "badges": [
                f"priority: {result.review_priority}",
                f"governance: {result.governance_priority}",
                result.status,
            ],
            "metrics": {
                "priority_score": result.priority_score,
                "weighted_priority": result.weighted_priority,
                "evidence_gap": result.evidence_gap,
                "governance_priority": result.governance_priority,
                "evidence_strength": result.evidence_strength
            },
            "swot": {
                "quadrant": result.quadrant,
                "orientation": result.orientation,
                "impact": result.impact,
                "confidence": result.confidence,
                "urgency": result.urgency,
                "feasibility": result.feasibility,
                "strategic_fit": result.strategic_fit,
                "claim_strength": result.claim_strength
            },
            "governance": {
                "owner": result.owner,
                "status": result.status,
                "review_date": result.review_date,
                "review_priority": result.review_priority,
                "reasons": result.governance_reasons
            },
            "recommended_action": recommended_action(result)
        })

    return cards


def build_catalog(results: list[AuditResult]) -> dict[str, object]:
    quadrant_counts: dict[str, int] = {}
    for result in results:
        quadrant_counts[result.quadrant] = quadrant_counts.get(result.quadrant, 0) + 1

    return {
        "module": MODULE_NAME,
        "version": __version__,
        "article_slug": ARTICLE_SLUG,
        "article_title": ARTICLE_TITLE,
        "generated_at": generated_at(),
        "record_count": len(results),
        "quadrant_counts": quadrant_counts,
        "metrics": [
            "priority_score",
            "weighted_priority",
            "evidence_gap",
            "governance_priority"
        ],
        "outputs": {
            "audit_table": "outputs/tables/swot_canvas_audit.csv",
            "canvas_cards": "canvas/canvas_cards.json",
            "governance_queue": "canvas/governance_queue.json",
            "full_export": "outputs/json/swot_canvas_export.json"
        }
    }


def build_full_export(results: list[AuditResult]) -> dict[str, object]:
    result_dicts = [result.to_dict() for result in results]
    governance_queue = build_governance_queue(results)
    cards = build_canvas_cards(results)

    return {
        "module": MODULE_NAME,
        "version": __version__,
        "article_slug": ARTICLE_SLUG,
        "article_title": ARTICLE_TITLE,
        "generated_at": generated_at(),
        "results": result_dicts,
        "governance_queue": governance_queue,
        "canvas_cards": cards
    }


def write_markdown_queue(path: Path, queue: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# SWOT Analysis Catalyst Canvas Governance Queue",
        "",
        "Generated review queue for SWOT evidence gaps, vague claims, priority scoring, and governance status.",
        "",
    ]

    if not queue:
        lines.append("No governance queue items were generated.")
    else:
        for item in queue:
            lines.extend([
                f"## {item['item']}",
                "",
                f"- Priority: {item['review_priority']}",
                f"- Quadrant: {item['quadrant']}",
                f"- Orientation: {item['orientation']}",
                f"- Owner: {item['owner']}",
                f"- Status: {item['status']}",
                f"- Review date: {item['review_date']}",
                f"- Weighted priority: {item['weighted_priority']}",
                f"- Evidence gap: {item['evidence_gap']}",
                f"- Governance priority: {item['governance_priority']}",
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

    write_csv(article_root / "outputs" / "tables" / "swot_canvas_audit.csv", result_dicts)
    write_json(article_root / "outputs" / "json" / "catalog.json", catalog)
    write_json(article_root / "outputs" / "json" / "governance_queue.json", governance_queue)
    write_json(article_root / "outputs" / "json" / "canvas_cards.json", cards)
    write_json(article_root / "outputs" / "json" / "swot_canvas_export.json", full_export)
    write_json(article_root / "canvas" / "governance_queue.json", governance_queue)
    write_json(article_root / "canvas" / "canvas_cards.json", cards)
    write_markdown_queue(article_root / "outputs" / "markdown" / "governance_queue.md", governance_queue)
