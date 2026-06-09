"""Export utilities for BCG Matrix Catalyst Canvas integration."""

from __future__ import annotations

from datetime import datetime, timezone
import csv
import json
from pathlib import Path

from . import ARTICLE_SLUG, ARTICLE_TITLE, MODULE_NAME, __version__
from .governance import build_governance_queue, slugify
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
            "card_id": f"bcg-item-{slugify(result.item)}",
            "type": "bcg_portfolio_item_card",
            "article_slug": ARTICLE_SLUG,
            "title": result.item,
            "subtitle": f"{result.quadrant} / {result.portfolio_area}",
            "description": result.description,
            "badges": [
                f"priority: {result.review_priority}",
                f"quadrant: {result.quadrant}",
                f"portfolio priority: {result.portfolio_priority}",
                result.status,
            ],
            "metrics": {
                "growth_score": result.growth_score,
                "relative_share_score": result.relative_share_score,
                "evidence_strength": result.evidence_strength,
                "strategic_fit": result.strategic_fit,
                "maintenance_burden": result.maintenance_burden,
                "evidence_gap": result.evidence_gap,
                "portfolio_priority": result.portfolio_priority
            },
            "bcg": {
                "portfolio_area": result.portfolio_area,
                "quadrant": result.quadrant,
                "recommended_action": result.recommended_action
            },
            "governance": {
                "owner": result.owner,
                "status": result.status,
                "review_date": result.review_date,
                "review_priority": result.review_priority,
                "reasons": result.governance_reasons
            }
        })

    return cards


def build_catalog(results: list[AuditResult]) -> dict[str, object]:
    quadrant_counts: dict[str, int] = {}
    portfolio_area_counts: dict[str, int] = {}

    for result in results:
        quadrant_counts[result.quadrant] = quadrant_counts.get(result.quadrant, 0) + 1
        portfolio_area_counts[result.portfolio_area] = portfolio_area_counts.get(result.portfolio_area, 0) + 1

    return {
        "module": MODULE_NAME,
        "version": __version__,
        "article_slug": ARTICLE_SLUG,
        "article_title": ARTICLE_TITLE,
        "generated_at": generated_at(),
        "record_count": len(results),
        "quadrant_counts": quadrant_counts,
        "portfolio_area_counts": portfolio_area_counts,
        "metrics": [
            "growth_score",
            "relative_share_score",
            "evidence_gap",
            "portfolio_priority"
        ],
        "outputs": {
            "audit_table": "outputs/tables/bcg_canvas_audit.csv",
            "canvas_cards": "canvas/canvas_cards.json",
            "governance_queue": "canvas/governance_queue.json",
            "full_export": "outputs/json/bcg_canvas_export.json"
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
        "# BCG Matrix Catalyst Canvas Governance Queue",
        "",
        "Generated review queue for portfolio classification evidence gaps growth-share claims and communication governance.",
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
                f"- Portfolio area: {item['portfolio_area']}",
                f"- Quadrant: {item['quadrant']}",
                f"- Owner: {item['owner']}",
                f"- Status: {item['status']}",
                f"- Review date: {item['review_date']}",
                f"- Growth score: {item['growth_score']}",
                f"- Relative share score: {item['relative_share_score']}",
                f"- Evidence gap: {item['evidence_gap']}",
                f"- Portfolio priority: {item['portfolio_priority']}",
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

    write_csv(article_root / "outputs" / "tables" / "bcg_canvas_audit.csv", result_dicts)
    write_json(article_root / "outputs" / "json" / "catalog.json", catalog)
    write_json(article_root / "outputs" / "json" / "governance_queue.json", governance_queue)
    write_json(article_root / "outputs" / "json" / "canvas_cards.json", cards)
    write_json(article_root / "outputs" / "json" / "bcg_canvas_export.json", full_export)
    write_json(article_root / "canvas" / "governance_queue.json", governance_queue)
    write_json(article_root / "canvas" / "canvas_cards.json", cards)
    write_markdown_queue(article_root / "outputs" / "markdown" / "governance_queue.md", governance_queue)
