"""Export utilities for Content Framework Value Catalyst Canvas integration."""

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
            "card_id": f"content-framework-value-item-{slugify(result.item)}",
            "type": "content_framework_value_item_card",
            "article_slug": ARTICLE_SLUG,
            "title": result.item,
            "subtitle": result.framework_type,
            "description": result.description,
            "badges": [
                f"priority: {result.review_priority}",
                f"value: {result.value_score}",
                f"risk: {result.framework_risk}",
                result.status,
            ],
            "metrics": {
                "value_score": result.value_score,
                "framework_risk": result.framework_risk,
                "review_priority_score": result.review_priority_score,
                "coherence": result.coherence,
                "reuse_readiness": result.reuse_readiness,
                "evidence_visibility": result.evidence_visibility,
                "audience_pathway_clarity": result.audience_pathway_clarity,
                "governance_maturity": result.governance_maturity,
                "platform_readiness": result.platform_readiness,
                "learning_support": result.learning_support,
                "ai_readiness": result.ai_readiness
            },
            "risk_profile": {
                "framework_type": result.framework_type,
                "fragmentation_risk": result.fragmentation_risk,
                "context_preservation": result.context_preservation,
                "maintenance_burden": result.maintenance_burden
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
    framework_type_counts: dict[str, int] = {}

    for result in results:
        framework_type_counts[result.framework_type] = framework_type_counts.get(result.framework_type, 0) + 1

    return {
        "module": MODULE_NAME,
        "version": __version__,
        "article_slug": ARTICLE_SLUG,
        "article_title": ARTICLE_TITLE,
        "generated_at": generated_at(),
        "record_count": len(results),
        "framework_type_counts": framework_type_counts,
        "metrics": [
            "value_score",
            "framework_risk",
            "review_priority_score"
        ],
        "outputs": {
            "audit_table": "outputs/tables/content_framework_value_canvas_audit.csv",
            "canvas_cards": "canvas/canvas_cards.json",
            "governance_queue": "canvas/governance_queue.json",
            "full_export": "outputs/json/content_framework_value_canvas_export.json"
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
        "# Why Content Frameworks Matter Today Catalyst Canvas Governance Queue",
        "",
        "Generated review queue for coherence, reuse readiness, evidence visibility, audience pathway clarity, governance maturity, platform readiness, learning support, AI-readiness, fragmentation risk, context preservation, maintenance burden, and framework risk.",
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
                f"- Framework type: {item['framework_type']}",
                f"- Owner: {item['owner']}",
                f"- Status: {item['status']}",
                f"- Review date: {item['review_date']}",
                f"- Value score: {item['value_score']}",
                f"- Framework risk: {item['framework_risk']}",
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

    write_csv(article_root / "outputs" / "tables" / "content_framework_value_canvas_audit.csv", result_dicts)
    write_json(article_root / "outputs" / "json" / "catalog.json", catalog)
    write_json(article_root / "outputs" / "json" / "governance_queue.json", governance_queue)
    write_json(article_root / "outputs" / "json" / "canvas_cards.json", cards)
    write_json(article_root / "outputs" / "json" / "content_framework_value_canvas_export.json", full_export)
    write_json(article_root / "canvas" / "governance_queue.json", governance_queue)
    write_json(article_root / "canvas" / "canvas_cards.json", cards)
    write_markdown_queue(article_root / "outputs" / "markdown" / "governance_queue.md", governance_queue)
