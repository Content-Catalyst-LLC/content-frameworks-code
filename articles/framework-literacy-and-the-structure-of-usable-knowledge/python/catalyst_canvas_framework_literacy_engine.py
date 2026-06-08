#!/usr/bin/env python3
"""
Catalyst Canvas Framework Literacy Engine

Professional-grade, dependency-free audit workflow for:
"Framework Literacy and the Structure of Usable Knowledge"

This workflow audits:
- assumption awareness
- blind-spot recognition
- boundary clarity
- use-condition clarity
- evidence alignment
- ethical safety
- audience fit
- domain fit
- adaptability
- governance readiness
- metadata completeness
- internal-link support
- taxonomy coverage
- governance review queue
- Catalyst Canvas catalog export
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timezone
from statistics import mean
from collections import Counter, defaultdict
from typing import Any, Iterable
import csv
import json

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "framework_literacy_config.json"
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


def readiness_status(row: dict[str, str], config: dict[str, Any], score: int, scores: dict[str, int]) -> str:
    if score >= int(config["minimum_literacy_score"]) and min(scores.values()) >= int(config["minimum_dimension_score"]):
        if all(int(row[gate]) >= 4 for gate in config["readiness_gates"]):
            if severity_rank(row["risk_severity"]) > severity_rank("medium"):
                return "framework-literate use ready"

    if int(row["ethical_safety"]) < 4:
        return "ethical review required"
    if int(row["evidence_alignment"]) < 4:
        return "evidence review required"
    if int(row["blind_spot_recognition"]) < 4:
        return "blind-spot documentation required"
    if int(row["use_condition_clarity"]) < 4:
        return "use-condition review required"
    if int(row["governance_readiness"]) < 4:
        return "governance plan required"
    if severity_rank(row["risk_severity"]) <= severity_rank("medium"):
        return "risk review required"

    return "revision recommended"


def literacy_audit(frameworks: list[dict[str, str]], config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[AuditFinding]]:
    dimensions = config["literacy_dimensions"]
    rows: list[dict[str, Any]] = []
    findings: list[AuditFinding] = []

    for row in frameworks:
        scores = {dimension: int(row[dimension]) for dimension in dimensions}
        score = sum(scores.values())
        average_score = round(mean(scores.values()), 3)
        weakest_value = min(scores.values())
        weakest_dimensions = [dimension for dimension, value in scores.items() if value == weakest_value]
        readiness = readiness_status(row, config, score, scores)

        audit_row = {
            "framework_id": row["framework_id"],
            "framework_name": row["framework_name"],
            "domain": row["domain"],
            "primary_use": row["primary_use"],
            "literacy_score": score,
            "average_score": average_score,
            "readiness_status": readiness,
            "weakest_dimensions": "; ".join(weakest_dimensions),
            "risk_severity": row["risk_severity"],
            "primary_blind_spot": row["primary_blind_spot"],
        }
        rows.append(audit_row)

        if readiness != "framework-literate use ready":
            findings.append(
                AuditFinding(
                    "high" if "ethical" in readiness or row["risk_severity"] == "high" else "medium",
                    "framework_literacy",
                    row["framework_id"],
                    f"{row['framework_name']} requires review: {readiness}.",
                    "Review assumptions, blind spots, use conditions, evidence alignment, ethical safety, and governance readiness before reuse."
                )
            )

    rows.sort(key=lambda item: (item["readiness_status"] != "framework-literate use ready", -item["literacy_score"], item["framework_name"]))
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


def use_condition_audit(use_conditions: list[dict[str, str]]) -> list[dict[str, Any]]:
    return [
        {
            "condition_id": row["condition_id"],
            "framework_id": row["framework_id"],
            "use_condition": row["use_condition"],
            "avoid_when": row["avoid_when"],
            "review_owner": row["review_owner"],
            "has_avoid_condition": bool(row["avoid_when"].strip()),
            "has_owner": bool(row["review_owner"].strip()),
        }
        for row in use_conditions
    ]


def governance_queue(findings: list[AuditFinding], literacy_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
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

    for row in literacy_rows:
        if row["readiness_status"] != "framework-literate use ready":
            rows.append(
                {
                    "source": "framework_literacy",
                    "severity": "high" if row["risk_severity"] == "high" else "medium",
                    "category": "framework_review",
                    "identifier": row["framework_id"],
                    "message": f"{row['framework_name']} status: {row['readiness_status']}.",
                    "recommended_action": "Resolve literacy gates before reuse in article templates, AI workflows, or framework libraries.",
                }
            )

    rows.sort(key=lambda item: (severity_rank(item["severity"]), item["category"], item["identifier"]))
    return rows


def catalog_export(article_map: list[dict[str, str]], metadata_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    metadata_by_slug = {row["slug"]: row for row in metadata_rows}
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
                "github_path": f"articles/{row['slug']}/",
            }
        )

    return rows


def markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Catalyst Canvas Framework Literacy Audit",
        "",
        f"Article: {report['article']}",
        f"Generated: {report['generated_at']}",
        "",
        "## Key Counts",
        "",
        f"- Framework records: {report['counts']['frameworks']}",
        f"- Article records: {report['counts']['articles']}",
        f"- Internal links: {report['counts']['links']}",
        f"- Governance queue items: {report['counts']['governance_queue']}",
        "",
        "## Frameworks Requiring Review",
        "",
    ]

    review_items = [row for row in report["framework_literacy"] if row["readiness_status"] != "framework-literate use ready"]

    if not review_items:
        lines.append("- No frameworks require review.")
    else:
        for row in review_items:
            lines.append(f"- `{row['framework_id']}` **{row['framework_name']}** — {row['readiness_status']}")

    return "\n".join(lines) + "\n"


def main() -> None:
    ensure_dirs()

    config = read_json(CONFIG)
    frameworks = read_csv(DATA / "framework_literacy_records.csv")
    article_map = read_csv(DATA / "content_framework_article_map.csv")
    metadata = read_csv(DATA / "metadata_inventory.csv")
    links = read_csv(DATA / "internal_links.csv")
    taxonomy = read_csv(DATA / "taxonomy_categories.csv")
    use_conditions = read_csv(DATA / "framework_use_conditions.csv")

    findings: list[AuditFinding] = []
    findings.extend(validate_columns(frameworks, ["framework_id", "framework_name", "domain", "primary_use"], "framework_literacy_records"))
    findings.extend(validate_columns(article_map, ["article_order", "title", "status", "cluster", "slug"], "content_framework_article_map"))
    findings.extend(validate_columns(metadata, ["slug", "title", "status"], "metadata_inventory"))
    findings.extend(validate_columns(links, ["source_slug", "target_slug", "relationship_type"], "internal_links"))

    literacy_rows, literacy_findings = literacy_audit(frameworks, config)
    metadata_rows, metadata_findings = metadata_audit(metadata)
    coverage_rows = article_map_coverage(article_map)
    link_rows, link_findings = link_diagnostics(article_map, links)
    taxonomy_rows = taxonomy_coverage(article_map, taxonomy)
    condition_rows = use_condition_audit(use_conditions)

    findings.extend(literacy_findings)
    findings.extend(metadata_findings)
    findings.extend(link_findings)

    governance_rows = governance_queue(findings, literacy_rows)
    catalog_rows = catalog_export(article_map, metadata_rows)

    write_csv(TABLES / "framework_literacy_audit.csv", literacy_rows)
    write_csv(TABLES / "metadata_literacy_readiness.csv", metadata_rows)
    write_csv(TABLES / "article_map_coverage_summary.csv", coverage_rows)
    write_csv(TABLES / "internal_link_literacy_diagnostics.csv", link_rows)
    write_csv(TABLES / "taxonomy_literacy_coverage.csv", taxonomy_rows)
    write_csv(TABLES / "framework_use_condition_audit.csv", condition_rows)
    write_csv(TABLES / "framework_literacy_governance_queue.csv", governance_rows)
    write_csv(CATALOG_EXPORTS / "catalyst_canvas_framework_literacy_catalog.csv", catalog_rows)

    generated_at = datetime.now(timezone.utc).isoformat()
    report = {
        "article": "Framework Literacy and the Structure of Usable Knowledge",
        "generated_at": generated_at,
        "config": config,
        "counts": {
            "frameworks": len(frameworks),
            "articles": len(article_map),
            "links": len(links),
            "taxonomy_categories": len(taxonomy),
            "use_conditions": len(use_conditions),
            "governance_queue": len(governance_rows),
        },
        "framework_literacy": literacy_rows,
        "metadata_readiness": metadata_rows,
        "coverage": coverage_rows,
        "link_diagnostics": link_rows,
        "taxonomy_coverage": taxonomy_rows,
        "use_condition_audit": condition_rows,
        "governance_queue": governance_rows,
    }

    write_json(REPORTS / "catalyst_canvas_framework_literacy_audit.json", report)
    write_json(AUDIT_LOGS / "audit_findings.json", [asdict(finding) for finding in findings])
    (REPORTS / "catalyst_canvas_framework_literacy_audit.md").write_text(markdown_report(report), encoding="utf-8")

    print("Catalyst Canvas framework literacy audit complete.")
    print(TABLES / "framework_literacy_audit.csv")
    print(TABLES / "framework_literacy_governance_queue.csv")
    print(REPORTS / "catalyst_canvas_framework_literacy_audit.json")
    print(CATALOG_EXPORTS / "catalyst_canvas_framework_literacy_catalog.csv")


if __name__ == "__main__":
    main()
