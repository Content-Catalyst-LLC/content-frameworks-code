"""Export utilities for Persona Frameworks Catalyst Canvas integration."""

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
            "card_id": f"persona-record-{slugify(result.persona)}",
            "type": "persona_framework_card",
            "article_slug": ARTICLE_SLUG,
            "title": result.persona,
            "subtitle": result.segment,
            "description": result.description,
            "badges": [
                f"priority: {result.review_priority}",
                f"readiness: {result.weighted_readiness}",
                result.status,
            ],
            "metrics": {
                "readiness_score": result.readiness_score,
                "weighted_readiness": result.weighted_readiness,
                "risk_score": result.risk_score,
                "revision_pressure": result.revision_pressure,
                "evidence_strength": result.evidence_strength
            },
            "persona": {
                "segment": result.segment,
                "content_pathway": result.content_pathway,
                "specificity": result.specificity,
                "content_fit": result.content_fit,
                "segment_alignment": result.segment_alignment,
                "governance_readiness": result.governance_readiness
            },
            "risk": {
                "stereotype_risk": result.stereotype_risk,
                "exclusion_risk": result.exclusion_risk,
                "weak_evidence_risk": result.weak_evidence_risk,
                "overgeneralization_risk": result.overgeneralization_risk
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
    return {
        "module": MODULE_NAME,
        "version": __version__,
        "article_slug": ARTICLE_SLUG,
        "article_title": ARTICLE_TITLE,
        "generated_at": generated_at(),
        "record_count": len(results),
        "metrics": [
            "readiness_score",
            "weighted_readiness",
            "risk_score",
            "revision_pressure",
            "evidence_strength"
        ],
        "outputs": {
            "audit_table": "outputs/tables/persona_canvas_audit.csv",
            "canvas_cards": "canvas/canvas_cards.json",
            "governance_queue": "canvas/governance_queue.json",
            "full_export": "outputs/json/persona_canvas_export.json"
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
        "# Persona Frameworks Catalyst Canvas Governance Queue",
        "",
        "Generated review queue for persona evidence readiness representation risk segment alignment and governance status.",
        "",
    ]

    if not queue:
        lines.append("No governance queue items were generated.")
    else:
        for item in queue:
            lines.extend([
                f"## {item['persona']}",
                "",
                f"- Priority: {item['review_priority']}",
                f"- Segment: {item['segment']}",
                f"- Content pathway: {item['content_pathway']}",
                f"- Owner: {item['owner']}",
                f"- Status: {item['status']}",
                f"- Review date: {item['review_date']}",
                f"- Evidence strength: {item['evidence_strength']}",
                f"- Risk score: {item['risk_score']}",
                f"- Revision pressure: {item['revision_pressure']}",
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

    write_csv(article_root / "outputs" / "tables" / "persona_canvas_audit.csv", result_dicts)
    write_json(article_root / "outputs" / "json" / "catalog.json", catalog)
    write_json(article_root / "outputs" / "json" / "governance_queue.json", governance_queue)
    write_json(article_root / "outputs" / "json" / "canvas_cards.json", cards)
    write_json(article_root / "outputs" / "json" / "persona_canvas_export.json", full_export)
    write_json(article_root / "canvas" / "governance_queue.json", governance_queue)
    write_json(article_root / "canvas" / "canvas_cards.json", cards)
    write_markdown_queue(article_root / "outputs" / "markdown" / "governance_queue.md", governance_queue)
