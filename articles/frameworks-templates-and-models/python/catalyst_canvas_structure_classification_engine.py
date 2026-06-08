#!/usr/bin/env python3
"""
Catalyst Canvas Structure Classification Engine

Professional-grade, dependency-free audit workflow for:
"Frameworks, Templates, and Models"

This workflow audits:
- frameworks, templates, models, methods, and workflows
- declared-vs-observed structure type
- structural signal scores
- governance completion
- high-risk structure patterns
- metadata completeness
- article-map coverage
- internal-link diagnostics
- taxonomy coverage
- governance review queues
- Catalyst Canvas catalog exports
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter, defaultdict
from typing import Any, Iterable
import csv
import json

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "structure_classification_config.json"
DATA = ROOT / "data"
TABLES = ROOT / "outputs" / "tables"
REPORTS = ROOT / "outputs" / "reports"
AUDIT_LOGS = ROOT / "outputs" / "audit_logs"
CATALOG_EXPORTS = ROOT / "outputs" / "catalog_exports"


@dataclass(frozen=True)
class AuditFinding:
    severity: str
    category: str
    identifier: str
    message: str
    recommended_action: str


def ensure_dirs() -> None:
    for directory in [TABLES, REPORTS, AUDIT_LOGS, CATALOG_EXPORTS]:
        directory.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"No rows supplied for {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def yes(value: str) -> bool:
    return value.strip().lower() in {"yes", "true", "1", "complete", "completed"}


def severity_rank(severity: str) -> int:
    return {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}.get(severity.lower(), 99)


def validate_columns(rows: list[dict[str, str]], required: Iterable[str], dataset_name: str) -> list[AuditFinding]:
    if not rows:
        return [
            AuditFinding(
                "critical",
                "schema",
                dataset_name,
                "Dataset is empty.",
                "Provide records before running the audit."
            )
        ]

    findings: list[AuditFinding] = []
    columns = set(rows[0].keys())

    for column in required:
        if column not in columns:
            findings.append(
                AuditFinding(
                    "critical",
                    "schema",
                    dataset_name,
                    f"Missing required column: {column}",
                    "Update the data export or mapping."
                )
            )

    return findings


def classify_observed_use(row: dict[str, str], config: dict[str, Any]) -> tuple[str, dict[str, int]]:
    signal_scores: dict[str, int] = {}

    for structure_type, fields in config["classification_signals"].items():
        signal_scores[structure_type] = sum(int(row[field]) for field in fields)

    observed_type = max(signal_scores, key=signal_scores.get)
    return observed_type, signal_scores


def governance_completion(row: dict[str, str], config: dict[str, Any]) -> tuple[float, list[str], list[str]]:
    fields = config["governance_fields"]
    completed = [field for field in fields if yes(row.get(field, ""))]
    missing = [field for field in fields if field not in completed]
    return round(len(completed) / len(fields), 4), completed, missing


def structure_classification_audit(structures: list[dict[str, str]], config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[AuditFinding]]:
    rows: list[dict[str, Any]] = []
    findings: list[AuditFinding] = []
    governance_threshold = float(config["minimum_governance_completion"])

    for row in structures:
        inferred_type, signals = classify_observed_use(row, config)
        declared_type = row["declared_type"]
        observed_type = row["observed_type"] or inferred_type
        declared_matches_observed = declared_type == observed_type
        inferred_matches_observed = inferred_type == observed_type
        completion, completed, missing = governance_completion(row, config)

        review_status = "ready for managed use"
        if not declared_matches_observed:
            review_status = "declared type mismatch"
        elif completion < governance_threshold:
            review_status = "governance incomplete"
        elif severity_rank(row["risk_severity"]) <= severity_rank("medium"):
            review_status = "risk review required"

        audit_row = {
            "structure_id": row["structure_id"],
            "structure_name": row["structure_name"],
            "declared_type": declared_type,
            "observed_type": observed_type,
            "inferred_type": inferred_type,
            "declared_matches_observed": declared_matches_observed,
            "inferred_matches_observed": inferred_matches_observed,
            "governance_completion": completion,
            "missing_governance_fields": "; ".join(missing) if missing else "none",
            "review_status": review_status,
            "risk_severity": row["risk_severity"],
            "risk_note": row["risk_note"],
            "framework_signal": signals["framework"],
            "template_signal": signals["template"],
            "model_signal": signals["model"],
            "method_signal": signals["method"],
            "workflow_signal": signals["workflow"],
        }
        rows.append(audit_row)

        if not declared_matches_observed:
            findings.append(
                AuditFinding(
                    "medium",
                    "structure_type",
                    row["structure_id"],
                    f"Declared type is {declared_type}, but observed type is {observed_type}.",
                    "Review whether the structure is being named and used correctly."
                )
            )

        if not inferred_matches_observed:
            findings.append(
                AuditFinding(
                    "low",
                    "classification_signal",
                    row["structure_id"],
                    f"Inferred type is {inferred_type}, but observed type is {observed_type}.",
                    "Review classification signals and structure documentation."
                )
            )

        if completion < governance_threshold:
            findings.append(
                AuditFinding(
                    "medium",
                    "governance",
                    row["structure_id"],
                    f"Governance completion is {completion:.0%}.",
                    "Complete purpose, use conditions, limitations, evidence review, ethical review, owner, and review cycle."
                )
            )

        if row["risk_severity"] == "high":
            findings.append(
                AuditFinding(
                    "high",
                    "risk",
                    row["structure_id"],
                    f"High-risk structure: {row['risk_note']}",
                    "Route to governance review before reuse in publication, AI workflows, or product catalogs."
                )
            )

    rows.sort(key=lambda item: (item["review_status"] == "ready for managed use", -severity_rank(item["risk_severity"]), item["structure_name"]))
    return rows, findings


def metadata_audit(metadata: list[dict[str, str]]) -> tuple[list[dict[str, Any]], list[AuditFinding]]:
    fields = [
        "excerpt",
        "tags",
        "github_url",
        "image_alt",
        "references",
        "last_reviewed",
        "series_context",
        "footer_navigation",
    ]

    rows: list[dict[str, Any]] = []
    findings: list[AuditFinding] = []

    for row in metadata:
        completed = [field for field in fields if yes(row.get(field, ""))]
        missing = [field for field in fields if field not in completed]
        completion_rate = len(completed) / len(fields)

        rows.append(
            {
                "slug": row["slug"],
                "title": row["title"],
                "status": row["status"],
                "completion_rate": round(completion_rate, 4),
                "missing_fields": "; ".join(missing) if missing else "none",
                "metadata_readiness": "ready" if completion_rate >= 0.85 else "needs metadata work",
            }
        )

        if row["status"] == "published" and completion_rate < 0.85:
            findings.append(
                AuditFinding(
                    "medium",
                    "metadata",
                    row["slug"],
                    f"Published article metadata completion is {completion_rate:.0%}.",
                    "Complete missing metadata fields."
                )
            )

    return rows, findings


def article_map_coverage(article_map: list[dict[str, str]]) -> list[dict[str, Any]]:
    grouped: dict[str, Counter[str]] = defaultdict(Counter)

    for row in article_map:
        grouped[row["cluster"]][row["status"]] += 1

    rows = []
    for cluster in sorted(grouped):
        published = grouped[cluster]["published"]
        planned = grouped[cluster]["planned"]
        total = published + planned
        rows.append(
            {
                "cluster": cluster,
                "published": published,
                "planned": planned,
                "total": total,
                "coverage_rate": round(published / total, 4) if total else 0.0,
                "gap_count": planned,
            }
        )
    return rows


def link_diagnostics(article_map: list[dict[str, str]], links: list[dict[str, str]]) -> tuple[list[dict[str, Any]], list[AuditFinding]]:
    known_slugs = {row["slug"] for row in article_map}
    outgoing = Counter(row["source_slug"] for row in links)
    incoming = Counter(row["target_slug"] for row in links)
    findings: list[AuditFinding] = []

    for link in links:
        if link["source_slug"] not in known_slugs:
            findings.append(AuditFinding("low", "links", link["source_slug"], "Link source is outside sample article map.", "Confirm linked article exists."))
        if link["target_slug"] not in known_slugs:
            findings.append(AuditFinding("low", "links", link["target_slug"], "Link target is outside sample article map.", "Confirm linked article exists."))

    slugs = sorted(known_slugs | set(outgoing) | set(incoming))
    rows = []
    for slug in slugs:
        degree = outgoing[slug] + incoming[slug]
        rows.append(
            {
                "slug": slug,
                "outgoing_links": outgoing[slug],
                "incoming_links": incoming[slug],
                "total_link_degree": degree,
                "network_role": "hub" if degree >= 5 else "connector" if degree >= 3 else "thinly linked",
            }
        )

    return rows, findings


def taxonomy_coverage(article_map: list[dict[str, str]], taxonomy: list[dict[str, str]]) -> list[dict[str, Any]]:
    counts = Counter(row["cluster"] for row in article_map)
    return [
        {
            "category": row["category"],
            "expected_role": row["expected_role"],
            "article_count_in_sample": counts[row["category"]],
            "taxonomy_status": "active" if counts[row["category"]] else "missing from sample",
        }
        for row in taxonomy
    ]


def misuse_case_audit(cases: list[dict[str, str]]) -> list[dict[str, Any]]:
    return [
        {
            "case_id": row["case_id"],
            "structure_id": row["structure_id"],
            "misuse_pattern": row["misuse_pattern"],
            "likely_consequence": row["likely_consequence"],
            "recommended_review": row["recommended_review"],
            "requires_governance_review": True,
        }
        for row in cases
    ]


def governance_queue(findings: list[AuditFinding], structure_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = [
        {
            "source": "automated_audit",
            "severity": finding.severity,
            "category": finding.category,
            "identifier": finding.identifier,
            "message": finding.message,
            "recommended_action": finding.recommended_action,
        }
        for finding in findings
    ]

    for row in structure_rows:
        if row["review_status"] != "ready for managed use":
            rows.append(
                {
                    "source": "structure_classification",
                    "severity": "high" if row["risk_severity"] == "high" else "medium",
                    "category": "structure_review",
                    "identifier": row["structure_id"],
                    "message": f"{row['structure_name']} status: {row['review_status']}.",
                    "recommended_action": "Review structure type, governance, use conditions, and documented limitations before reuse."
                }
            )

    rows.sort(key=lambda item: (severity_rank(item["severity"]), item["category"], item["identifier"]))
    return rows


def catalog_export(article_map: list[dict[str, str]], metadata_rows: list[dict[str, Any]], structure_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    metadata_by_slug = {row["slug"]: row for row in metadata_rows}
    review_count = sum(1 for row in structure_rows if row["review_status"] != "ready for managed use")

    rows = []
    for row in article_map:
        metadata = metadata_by_slug.get(row["slug"], {})
        rows.append(
            {
                "catalog_product": "Catalyst Canvas",
                "series": "Content Frameworks",
                "slug": row["slug"],
                "title": row["title"],
                "cluster": row["cluster"],
                "status": row["status"],
                "metadata_completion_rate": metadata.get("completion_rate", 0.0),
                "metadata_readiness": metadata.get("metadata_readiness", "unknown"),
                "structure_review_items": review_count if row["slug"] == "frameworks-templates-and-models" else 0,
                "github_path": f"articles/{row['slug']}/",
            }
        )

    return rows


def markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Catalyst Canvas Structure Classification Audit",
        "",
        f"Article: {report['article']}",
        f"Generated: {report['generated_at']}",
        "",
        "## Key Counts",
        "",
        f"- Structures reviewed: {report['counts']['structures']}",
        f"- Article records: {report['counts']['articles']}",
        f"- Type mismatches: {report['counts']['type_mismatches']}",
        f"- Governance queue items: {report['counts']['governance_queue']}",
        "",
        "## Structures Requiring Review",
        "",
    ]

    review_items = [row for row in report["structure_classification"] if row["review_status"] != "ready for managed use"]

    if not review_items:
        lines.append("- No structures require review.")
    else:
        for row in review_items:
            lines.append(f"- `{row['structure_id']}` **{row['structure_name']}** — {row['review_status']}")

    return "\n".join(lines) + "\n"


def main() -> None:
    ensure_dirs()

    config = read_json(CONFIG)
    structures = read_csv(DATA / "content_structure_inventory.csv")
    article_map = read_csv(DATA / "content_framework_article_map.csv")
    metadata = read_csv(DATA / "metadata_inventory.csv")
    links = read_csv(DATA / "internal_links.csv")
    taxonomy = read_csv(DATA / "taxonomy_categories.csv")
    misuse_cases = read_csv(DATA / "structure_misuse_cases.csv")

    findings: list[AuditFinding] = []
    findings.extend(validate_columns(structures, ["structure_id", "structure_name", "declared_type", "observed_type"], "content_structure_inventory"))
    findings.extend(validate_columns(article_map, ["article_order", "title", "status", "cluster", "slug"], "content_framework_article_map"))
    findings.extend(validate_columns(metadata, ["slug", "title", "status"], "metadata_inventory"))
    findings.extend(validate_columns(links, ["source_slug", "target_slug", "relationship_type"], "internal_links"))

    structure_rows, structure_findings = structure_classification_audit(structures, config)
    metadata_rows, metadata_findings = metadata_audit(metadata)
    coverage_rows = article_map_coverage(article_map)
    link_rows, link_findings = link_diagnostics(article_map, links)
    taxonomy_rows = taxonomy_coverage(article_map, taxonomy)
    misuse_rows = misuse_case_audit(misuse_cases)

    findings.extend(structure_findings)
    findings.extend(metadata_findings)
    findings.extend(link_findings)

    governance_rows = governance_queue(findings, structure_rows)
    catalog_rows = catalog_export(article_map, metadata_rows, structure_rows)

    write_csv(TABLES / "structure_classification_audit.csv", structure_rows)
    write_csv(TABLES / "metadata_structure_readiness.csv", metadata_rows)
    write_csv(TABLES / "article_map_coverage_summary.csv", coverage_rows)
    write_csv(TABLES / "internal_link_structure_diagnostics.csv", link_rows)
    write_csv(TABLES / "taxonomy_structure_coverage.csv", taxonomy_rows)
    write_csv(TABLES / "structure_misuse_case_audit.csv", misuse_rows)
    write_csv(TABLES / "structure_governance_queue.csv", governance_rows)
    write_csv(CATALOG_EXPORTS / "catalyst_canvas_structure_catalog.csv", catalog_rows)

    generated_at = datetime.now(timezone.utc).isoformat()
    type_mismatches = sum(1 for row in structure_rows if not row["declared_matches_observed"])

    report = {
        "article": "Frameworks, Templates, and Models",
        "generated_at": generated_at,
        "config": config,
        "counts": {
            "structures": len(structures),
            "articles": len(article_map),
            "links": len(links),
            "taxonomy_categories": len(taxonomy),
            "misuse_cases": len(misuse_cases),
            "type_mismatches": type_mismatches,
            "governance_queue": len(governance_rows),
        },
        "structure_classification": structure_rows,
        "metadata_readiness": metadata_rows,
        "coverage": coverage_rows,
        "link_diagnostics": link_rows,
        "taxonomy_coverage": taxonomy_rows,
        "misuse_cases": misuse_rows,
        "governance_queue": governance_rows,
    }

    write_json(REPORTS / "catalyst_canvas_structure_classification_audit.json", report)
    write_json(AUDIT_LOGS / "audit_findings.json", [asdict(finding) for finding in findings])
    (REPORTS / "catalyst_canvas_structure_classification_audit.md").write_text(markdown_report(report), encoding="utf-8")

    print("Catalyst Canvas structure classification audit complete.")
    print(TABLES / "structure_classification_audit.csv")
    print(TABLES / "structure_governance_queue.csv")
    print(REPORTS / "catalyst_canvas_structure_classification_audit.json")
    print(CATALOG_EXPORTS / "catalyst_canvas_structure_catalog.csv")


if __name__ == "__main__":
    main()
