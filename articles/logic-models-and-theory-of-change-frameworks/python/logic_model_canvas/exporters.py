# Export utilities for logic-model and Theory of Change Catalyst Canvas integration.

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
            "card_id": f"logic-model-element-{slugify(result.element)}",
            "type": "logic_model_element_card",
            "article_slug": ARTICLE_SLUG,
            "title": result.element,
            "subtitle": result.model_layer,
            "description": result.description,
            "badges": [
                f"priority: {result.review_priority}",
                f"quality: {result.pathway_quality}",
                f"assumption risk: {result.assumption_risk}",
                result.status,
            ],
            "metrics": {
                "assumption_risk": result.assumption_risk,
                "evidence_gap": result.evidence_gap,
                "pathway_quality": result.pathway_quality,
                "governance_priority": result.governance_priority,
                "evidence_strength": result.evidence_strength,
                "measurement_coverage": result.measurement_coverage,
                "outcome_clarity": result.outcome_clarity
            },
            "logic_model": {
                "model_layer": result.model_layer,
                "assumption_importance": result.assumption_importance,
                "assumption_evidence": result.assumption_evidence,
                "claim_strength": result.claim_strength
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
    layer_counts: dict[str, int] = {}
    for result in results:
        layer_counts[result.model_layer] = layer_counts.get(result.model_layer, 0) + 1
    return {
        "module": MODULE_NAME,
        "version": __version__,
        "article_slug": ARTICLE_SLUG,
        "article_title": ARTICLE_TITLE,
        "generated_at": generated_at(),
        "record_count": len(results),
        "model_layer_counts": layer_counts,
        "metrics": ["assumption_risk", "evidence_gap", "pathway_quality", "governance_priority"],
        "outputs": {
            "audit_table": "outputs/tables/logic_model_canvas_audit.csv",
            "canvas_cards": "canvas/canvas_cards.json",
            "governance_queue": "canvas/governance_queue.json",
            "full_export": "outputs/json/logic_model_canvas_export.json"
        }
    }


def build_full_export(results: list[AuditResult]) -> dict[str, object]:
    return {
        "module": MODULE_NAME,
        "version": __version__,
        "article_slug": ARTICLE_SLUG,
        "article_title": ARTICLE_TITLE,
        "generated_at": generated_at(),
        "results": [result.to_dict() for result in results],
        "governance_queue": build_governance_queue(results),
        "canvas_cards": build_canvas_cards(results)
    }


def write_markdown_queue(path: Path, queue: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Logic Models and Theory of Change Catalyst Canvas Governance Queue",
        "",
        "Generated review queue for causal pathway evidence gaps assumption risk measurement coverage and governance status.",
        "",
    ]
    if not queue:
        lines.append("No governance queue items were generated.")
    else:
        for item in queue:
            lines.extend([
                f"## {item['element']}",
                "",
                f"- Priority: {item['review_priority']}",
                f"- Model layer: {item['model_layer']}",
                f"- Owner: {item['owner']}",
                f"- Status: {item['status']}",
                f"- Review date: {item['review_date']}",
                f"- Assumption risk: {item['assumption_risk']}",
                f"- Evidence gap: {item['evidence_gap']}",
                f"- Pathway quality: {item['pathway_quality']}",
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

    write_csv(article_root / "outputs" / "tables" / "logic_model_canvas_audit.csv", result_dicts)
    write_json(article_root / "outputs" / "json" / "catalog.json", catalog)
    write_json(article_root / "outputs" / "json" / "governance_queue.json", governance_queue)
    write_json(article_root / "outputs" / "json" / "canvas_cards.json", cards)
    write_json(article_root / "outputs" / "json" / "logic_model_canvas_export.json", full_export)
    write_json(article_root / "canvas" / "governance_queue.json", governance_queue)
    write_json(article_root / "canvas" / "canvas_cards.json", cards)
    write_markdown_queue(article_root / "outputs" / "markdown" / "governance_queue.md", governance_queue)
