"""Export utilities for Framework Drift Catalyst Canvas integration."""

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
            "card_id": f"framework-drift-item-{slugify(result.item)}",
            "type": "framework_drift_item_card",
            "article_slug": ARTICLE_SLUG,
            "title": result.item,
            "subtitle": result.item_type,
            "description": result.description,
            "badges": [
                f"priority: {result.repair_priority}",
                f"integrity: {result.conceptual_integrity}",
                f"drift risk: {result.drift_risk}",
                result.status,
            ],
            "metrics": {
                "conceptual_integrity": result.conceptual_integrity,
                "drift_risk": result.drift_risk,
                "repair_priority_score": result.repair_priority_score,
                "definition_consistency": result.definition_consistency,
                "boundary_clarity": result.boundary_clarity,
                "evidence_currency": result.evidence_currency,
                "metadata_consistency": result.metadata_consistency,
                "link_health": result.link_health,
                "governance_maturity": result.governance_maturity
            },
            "risk_profile": {
                "item_type": result.item_type,
                "reuse_pressure": result.reuse_pressure,
                "stale_evidence_risk": result.stale_evidence_risk,
                "dependency_complexity": result.dependency_complexity,
                "platform_alignment": result.platform_alignment,
                "audience_impact": result.audience_impact
            },
            "governance": {
                "owner": result.owner,
                "status": result.status,
                "review_date": result.review_date,
                "repair_priority": result.repair_priority,
                "reasons": result.governance_reasons,
                "recommended_action": result.recommended_action
            }
        })

    return cards


def build_catalog(results: list[AuditResult]) -> dict[str, object]:
    item_type_counts: dict[str, int] = {}

    for result in results:
        item_type_counts[result.item_type] = item_type_counts.get(result.item_type, 0) + 1

    return {
        "module": MODULE_NAME,
        "version": __version__,
        "article_slug": ARTICLE_SLUG,
        "article_title": ARTICLE_TITLE,
        "generated_at": generated_at(),
        "record_count": len(results),
        "item_type_counts": item_type_counts,
        "metrics": [
            "conceptual_integrity",
            "drift_risk",
            "repair_priority_score"
        ],
        "outputs": {
            "audit_table": "outputs/tables/framework_drift_canvas_audit.csv",
            "canvas_cards": "canvas/canvas_cards.json",
            "governance_queue": "canvas/governance_queue.json",
            "full_export": "outputs/json/framework_drift_canvas_export.json"
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
        "# Framework Drift and Conceptual Decay Catalyst Canvas Repair Queue",
        "",
        "Generated repair queue for definition consistency, boundary clarity, evidence currency, metadata consistency, link health, governance maturity, reuse pressure, stale evidence risk, dependency complexity, platform alignment, audience impact, and drift risk.",
        "",
    ]

    if not queue:
        lines.append("No repair queue items were generated.")
    else:
        for item in queue:
            lines.extend([
                f"## {item['item']}",
                "",
                f"- Priority: {item['repair_priority']}",
                f"- Item type: {item['item_type']}",
                f"- Owner: {item['owner']}",
                f"- Status: {item['status']}",
                f"- Review date: {item['review_date']}",
                f"- Conceptual integrity: {item['conceptual_integrity']}",
                f"- Drift risk: {item['drift_risk']}",
                f"- Repair priority score: {item['repair_priority_score']}",
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

    write_csv(article_root / "outputs" / "tables" / "framework_drift_canvas_audit.csv", result_dicts)
    write_json(article_root / "outputs" / "json" / "catalog.json", catalog)
    write_json(article_root / "outputs" / "json" / "governance_queue.json", governance_queue)
    write_json(article_root / "outputs" / "json" / "canvas_cards.json", cards)
    write_json(article_root / "outputs" / "json" / "framework_drift_canvas_export.json", full_export)
    write_json(article_root / "canvas" / "governance_queue.json", governance_queue)
    write_json(article_root / "canvas" / "canvas_cards.json", cards)
    write_markdown_queue(article_root / "outputs" / "markdown" / "repair_queue.md", governance_queue)
