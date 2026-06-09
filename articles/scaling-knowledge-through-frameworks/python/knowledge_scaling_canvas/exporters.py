"""Export utilities for Knowledge Scaling Catalyst Canvas integration."""

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
            "card_id": f"knowledge-scaling-item-{slugify(result.item)}",
            "type": "knowledge_scaling_item_card",
            "article_slug": ARTICLE_SLUG,
            "title": result.item,
            "subtitle": result.asset_type,
            "description": result.description,
            "badges": [
                f"priority: {result.review_priority}",
                f"scalability: {result.scalability_score}",
                f"maintenance risk: {result.maintenance_risk}",
                result.status,
            ],
            "metrics": {
                "scalability_score": result.scalability_score,
                "maintenance_risk": result.maintenance_risk,
                "review_priority_score": result.review_priority_score,
                "modularity": result.modularity,
                "taxonomy_quality": result.taxonomy_quality,
                "metadata_completeness": result.metadata_completeness,
                "link_coverage": result.link_coverage,
                "evidence_alignment": result.evidence_alignment,
                "reuse_readiness": result.reuse_readiness
            },
            "knowledge_system": {
                "asset_type": result.asset_type,
                "governance_maturity": result.governance_maturity,
                "platform_readiness": result.platform_readiness,
                "audience_pathway_clarity": result.audience_pathway_clarity,
                "dependency_complexity": result.dependency_complexity
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
    asset_type_counts: dict[str, int] = {}

    for result in results:
        asset_type_counts[result.asset_type] = asset_type_counts.get(result.asset_type, 0) + 1

    return {
        "module": MODULE_NAME,
        "version": __version__,
        "article_slug": ARTICLE_SLUG,
        "article_title": ARTICLE_TITLE,
        "generated_at": generated_at(),
        "record_count": len(results),
        "asset_type_counts": asset_type_counts,
        "metrics": [
            "scalability_score",
            "maintenance_risk",
            "review_priority_score"
        ],
        "outputs": {
            "audit_table": "outputs/tables/knowledge_scaling_canvas_audit.csv",
            "canvas_cards": "canvas/canvas_cards.json",
            "governance_queue": "canvas/governance_queue.json",
            "full_export": "outputs/json/knowledge_scaling_canvas_export.json"
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
        "# Scaling Knowledge Through Frameworks Catalyst Canvas Governance Queue",
        "",
        "Generated review queue for modularity, taxonomy quality, metadata completeness, link coverage, evidence alignment, reuse readiness, governance maturity, platform readiness, audience pathway clarity, dependency complexity, and maintenance risk.",
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
                f"- Asset type: {item['asset_type']}",
                f"- Owner: {item['owner']}",
                f"- Status: {item['status']}",
                f"- Review date: {item['review_date']}",
                f"- Scalability score: {item['scalability_score']}",
                f"- Maintenance risk: {item['maintenance_risk']}",
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

    write_csv(article_root / "outputs" / "tables" / "knowledge_scaling_canvas_audit.csv", result_dicts)
    write_json(article_root / "outputs" / "json" / "catalog.json", catalog)
    write_json(article_root / "outputs" / "json" / "governance_queue.json", governance_queue)
    write_json(article_root / "outputs" / "json" / "canvas_cards.json", cards)
    write_json(article_root / "outputs" / "json" / "knowledge_scaling_canvas_export.json", full_export)
    write_json(article_root / "canvas" / "governance_queue.json", governance_queue)
    write_json(article_root / "canvas" / "canvas_cards.json", cards)
    write_markdown_queue(article_root / "outputs" / "markdown" / "governance_queue.md", governance_queue)
