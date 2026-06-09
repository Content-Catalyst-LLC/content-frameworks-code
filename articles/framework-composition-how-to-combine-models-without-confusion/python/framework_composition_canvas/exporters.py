"""Export utilities for framework composition Catalyst Canvas integration."""

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
            "card_id": f"framework-composition-item-{slugify(result.item)}",
            "type": "framework_composition_item_card",
            "article_slug": ARTICLE_SLUG,
            "title": result.item,
            "subtitle": result.composition_type,
            "description": result.description,
            "badges": [
                f"priority: {result.review_priority}",
                f"quality: {result.quality_score}",
                f"confusion risk: {result.confusion_risk}",
                result.status,
            ],
            "metrics": {
                "quality_score": result.quality_score,
                "confusion_risk": result.confusion_risk,
                "review_priority_score": result.review_priority_score,
                "purpose_fit": result.purpose_fit,
                "role_clarity": result.role_clarity,
                "boundary_clarity": result.boundary_clarity,
                "sequence_clarity": result.sequence_clarity,
                "translation_quality": result.translation_quality
            },
            "composition": {
                "composition_type": result.composition_type,
                "evidence_alignment": result.evidence_alignment,
                "governance_readiness": result.governance_readiness,
                "audience_burden": result.audience_burden,
                "conflict_risk": result.conflict_risk
            },
            "governance": {
                "owner": result.owner,
                "status": result.status,
                "review_date": result.review_date,
                "review_priority": result.review_priority,
                "reasons": result.governance_reasons,
                "recommended_action": result.recommended_action
            }
        })

    return cards


def build_catalog(results: list[AuditResult]) -> dict[str, object]:
    composition_type_counts: dict[str, int] = {}

    for result in results:
        composition_type_counts[result.composition_type] = composition_type_counts.get(result.composition_type, 0) + 1

    return {
        "module": MODULE_NAME,
        "version": __version__,
        "article_slug": ARTICLE_SLUG,
        "article_title": ARTICLE_TITLE,
        "generated_at": generated_at(),
        "record_count": len(results),
        "composition_type_counts": composition_type_counts,
        "metrics": [
            "quality_score",
            "confusion_risk",
            "review_priority_score"
        ],
        "outputs": {
            "audit_table": "outputs/tables/framework_composition_canvas_audit.csv",
            "canvas_cards": "canvas/canvas_cards.json",
            "governance_queue": "canvas/governance_queue.json",
            "full_export": "outputs/json/framework_composition_canvas_export.json"
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
        "# Framework Composition Catalyst Canvas Governance Queue",
        "",
        "Generated review queue for purpose fit, role clarity, boundary clarity, sequencing, translation quality, evidence alignment, governance readiness, audience burden, conflict risk, and composition status.",
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
                f"- Composition type: {item['composition_type']}",
                f"- Owner: {item['owner']}",
                f"- Status: {item['status']}",
                f"- Review date: {item['review_date']}",
                f"- Quality score: {item['quality_score']}",
                f"- Confusion risk: {item['confusion_risk']}",
                f"- Review priority score: {item['review_priority_score']}",
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

    write_csv(article_root / "outputs" / "tables" / "framework_composition_canvas_audit.csv", result_dicts)
    write_json(article_root / "outputs" / "json" / "catalog.json", catalog)
    write_json(article_root / "outputs" / "json" / "governance_queue.json", governance_queue)
    write_json(article_root / "outputs" / "json" / "canvas_cards.json", cards)
    write_json(article_root / "outputs" / "json" / "framework_composition_canvas_export.json", full_export)
    write_json(article_root / "canvas" / "governance_queue.json", governance_queue)
    write_json(article_root / "canvas" / "canvas_cards.json", cards)
    write_markdown_queue(article_root / "outputs" / "markdown" / "governance_queue.md", governance_queue)
