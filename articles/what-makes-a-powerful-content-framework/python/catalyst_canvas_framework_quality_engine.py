#!/usr/bin/env python3
"""
Catalyst Canvas Framework Quality Engine

Professional-grade, dependency-free audit workflow for:
"What Makes a Powerful Content Framework?"

This script demonstrates how a content-intelligence product can audit:
- framework quality dimensions
- evidence alignment
- ethical safety
- governability
- maturity level
- metadata readiness
- internal-link support
- taxonomy coverage
- governance review queues
- catalog exports

Uses only Python standard library for portability.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timezone
import csv
import json
from collections import Counter, defaultdict
from statistics import mean
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "framework_quality_audit_config.json"
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


@dataclass(frozen=True)
class FrameworkQualityRecord:
    framework_id: str
    framework_name: str
    domain: str
    primary_use: str
    quality_score: int
    average_quality: float
    readiness_score: float
    maturity_level: str
    governance_status: str
    weakest_dimensions: str
    risk_severity: str
    risk_note: str


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
    findings: list[AuditFinding] = []

    if not rows:
        return [
            AuditFinding(
                "critical",
                "schema",
                dataset_name,
                "Dataset is empty.",
                "Provide records before running production audit."
            )
        ]

    columns = set(rows[0].keys())

    for column in required:
        if column not in columns:
            findings.append(
                AuditFinding(
                    "critical",
                    "schema",
                    dataset_name,
                    f"Missing required column: {column}",
                    "Update source export or mapping."
                )
            )

    return findings


def maturity_level(quality_score: int, readiness_score: float) -> str:
    if quality_score >= 44 and readiness_score >= 4.0:
        return "product-ready"
    if quality_score >= 36:
        return "strong but review"
    if quality_score >= 28:
        return "developing"
    return "not ready"


def governance_status(row: dict[str, str], config: dict[str, Any]) -> str:
    minimum_dimension = int(config["minimum_dimension_score"])

    if int(row["evidence_alignment"]) < 4:
        return "evidence review required"
    if int(row["ethical_safety"]) < 4:
        return "ethical review required"
    if int(row["governability"]) < 4:
        return "governance plan required"

    weak = [
        dimension for dimension in config["quality_dimensions"]
        if int(row[dimension]) < minimum_dimension
    ]

    if weak:
        return "dimension review required"

    if severity_rank(row["risk_severity"]) <= severity_rank("medium"):
        return "risk review required"

    return "ready for managed use"


def framework_quality_audit(frameworks: list[dict[str, str]], config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[AuditFinding]]:
    rows: list[dict[str, Any]] = []
    findings: list[AuditFinding] = []
    dimensions = config["quality_dimensions"]
    readiness_dimensions = config["readiness_dimensions"]

    for row in frameworks:
        scores = {dimension: int(row[dimension]) for dimension in dimensions}
        quality_score = sum(scores.values())
        readiness_score = mean(int(row[dimension]) for dimension in readiness_dimensions)
        maturity = maturity_level(quality_score, readiness_score)
        governance = governance_status(row, config)

        weakest = [
            name for name, value in sorted(scores.items(), key=lambda item: item[1])
            if value == min(scores.values())
        ]

        record = FrameworkQualityRecord(
            framework_id=row["framework_id"],
            framework_name=row["framework_name"],
            domain=row["domain"],
            primary_use=row["primary_use"],
            quality_score=quality_score,
            average_quality=round(mean(scores.values()), 3),
            readiness_score=round(readiness_score, 3),
            maturity_level=maturity,
            governance_status=governance,
            weakest_dimensions="; ".join(weakest),
            risk_severity=row["risk_severity"],
            risk_note=row["risk_note"],
        )

        rows.append(asdict(record))

        if maturity != "product-ready" or governance != "ready for managed use":
            severity = "high" if row["risk_severity"] == "high" or "ethical" in governance else "medium"
            findings.append(
                AuditFinding(
                    severity,
                    "framework_quality",
                    row["framework_id"],
                    f"{row['framework_name']} is {maturity}; governance status: {governance}.",
                    "Review weak dimensions, evidence alignment, ethical safety, and governance before broad reuse."
                )
            )

    rows.sort(key=lambda item: (item["maturity_level"] != "product-ready", -item["quality_score"], item["framework_name"]))
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
                "completed_fields": len(completed),
                "required_fields": len(fields),
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

    rows: list[dict[str, Any]] = []
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
            findings.append(
                AuditFinding(
                    "low",
                    "links",
                    link["source_slug"],
                    "Link source is not in the sample article map.",
                    "Confirm whether the linked article exists outside the sample."
                )
            )
        if link["target_slug"] not in known_slugs:
            findings.append(
                AuditFinding(
                    "low",
                    "links",
                    link["target_slug"],
                    "Link target is not in the sample article map.",
                    "Confirm whether the linked article exists outside the sample."
                )
            )

    slugs = sorted(known_slugs | set(outgoing) | set(incoming))
    rows: list[dict[str, Any]] = []

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


def review_case_summary(cases: list[dict[str, str]]) -> list[dict[str, Any]]:
    return [
        {
            "case_id": row["case_id"],
            "framework_id": row["framework_id"],
            "use_context": row["use_context"],
            "review_question": row["review_question"],
            "decision": row["decision"],
            "requires_review": "review" in row["decision"] or "revise" in row["decision"],
        }
        for row in cases
    ]


def governance_queue(findings: list[AuditFinding], quality_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
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

    for row in quality_rows:
        if row["governance_status"] != "ready for managed use":
            rows.append(
                {
                    "source": "framework_quality",
                    "severity": "high" if row["risk_severity"] == "high" else "medium",
                    "category": "governance",
                    "identifier": row["framework_id"],
                    "message": f"{row['framework_name']} governance status: {row['governance_status']}.",
                    "recommended_action": "Resolve governance gate before product deployment.",
                }
            )

    rows.sort(key=lambda item: (severity_rank(item["severity"]), item["category"], item["identifier"]))
    return rows


def catalog_export(article_map: list[dict[str, str]], metadata_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    metadata_by_slug = {row["slug"]: row for row in metadata_rows}

    rows: list[dict[str, Any]] = []
    for row in article_map:
        meta = metadata_by_slug.get(row["slug"], {})
        rows.append(
            {
                "catalog_product": "Catalyst Canvas",
                "series": "Content Frameworks",
                "slug": row["slug"],
                "title": row["title"],
                "cluster": row["cluster"],
                "status": row["status"],
                "metadata_completion_rate": meta.get("completion_rate", 0.0),
                "metadata_readiness": meta.get("metadata_readiness", "unknown"),
                "github_path": f"articles/{row['slug']}/",
            }
        )
    return rows


def markdown_report(payload: dict[str, Any]) -> str:
    lines = [
        "# Catalyst Canvas Framework Quality Audit",
        "",
        f"Article: {payload['article']}",
        f"Generated: {payload['generated_at']}",
        "",
        "## Key Counts",
        "",
        f"- Framework records: {payload['counts']['frameworks']}",
        f"- Article records: {payload['counts']['articles']}",
        f"- Governance queue items: {payload['counts']['governance_queue']}",
        "",
        "## Frameworks Requiring Review",
        "",
    ]

    review_items = [
        row for row in payload["framework_quality"]
        if row["governance_status"] != "ready for managed use"
    ]

    if not review_items:
        lines.append("- No frameworks require review.")
    else:
        for row in review_items:
            lines.append(f"- `{row['framework_id']}` **{row['framework_name']}** — {row['governance_status']}")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    ensure_dirs()

    config = read_json(CONFIG)
    frameworks = read_csv(DATA / "framework_quality_scores.csv")
    article_map = read_csv(DATA / "content_framework_article_map.csv")
    metadata = read_csv(DATA / "metadata_inventory.csv")
    links = read_csv(DATA / "internal_links.csv")
    taxonomy = read_csv(DATA / "taxonomy_categories.csv")
    cases = read_csv(DATA / "framework_review_cases.csv")

    findings: list[AuditFinding] = []
    findings.extend(validate_columns(frameworks, ["framework_id", "framework_name", "domain", "primary_use"], "framework_quality_scores"))
    findings.extend(validate_columns(article_map, ["article_order", "title", "status", "cluster", "slug"], "article_map"))
    findings.extend(validate_columns(metadata, ["slug", "title", "status"], "metadata_inventory"))
    findings.extend(validate_columns(links, ["source_slug", "target_slug", "relationship_type"], "internal_links"))

    quality_rows, quality_findings = framework_quality_audit(frameworks, config)
    metadata_rows, metadata_findings = metadata_audit(metadata)
    coverage_rows = article_map_coverage(article_map)
    link_rows, link_findings = link_diagnostics(article_map, links)
    taxonomy_rows = taxonomy_coverage(article_map, taxonomy)
    case_rows = review_case_summary(cases)

    findings.extend(quality_findings)
    findings.extend(metadata_findings)
    findings.extend(link_findings)

    governance_rows = governance_queue(findings, quality_rows)
    catalog_rows = catalog_export(article_map, metadata_rows)

    write_csv(TABLES / "framework_quality_audit.csv", quality_rows)
    write_csv(TABLES / "metadata_quality_report.csv", metadata_rows)
    write_csv(TABLES / "article_map_coverage_summary.csv", coverage_rows)
    write_csv(TABLES / "internal_link_quality_diagnostics.csv", link_rows)
    write_csv(TABLES / "taxonomy_quality_coverage.csv", taxonomy_rows)
    write_csv(TABLES / "framework_review_case_summary.csv", case_rows)
    write_csv(TABLES / "framework_governance_review_queue.csv", governance_rows)
    write_csv(CATALOG_EXPORTS / "catalyst_canvas_framework_quality_catalog.csv", catalog_rows)

    generated_at = datetime.now(timezone.utc).isoformat()
    report = {
        "article": "What Makes a Powerful Content Framework?",
        "generated_at": generated_at,
        "config": config,
        "counts": {
            "frameworks": len(frameworks),
            "articles": len(article_map),
            "metadata_records": len(metadata),
            "links": len(links),
            "governance_queue": len(governance_rows),
        },
        "framework_quality": quality_rows,
        "metadata_quality": metadata_rows,
        "coverage": coverage_rows,
        "link_diagnostics": link_rows,
        "taxonomy_coverage": taxonomy_rows,
        "review_cases": case_rows,
        "governance_queue": governance_rows,
    }

    write_json(REPORTS / "catalyst_canvas_framework_quality_audit.json", report)
    write_json(AUDIT_LOGS / "audit_findings.json", [asdict(finding) for finding in findings])
    (REPORTS / "catalyst_canvas_framework_quality_audit.md").write_text(markdown_report(report), encoding="utf-8")

    print("Catalyst Canvas framework quality audit complete.")
    print(TABLES / "framework_quality_audit.csv")
    print(TABLES / "framework_governance_review_queue.csv")
    print(REPORTS / "catalyst_canvas_framework_quality_audit.json")
    print(CATALOG_EXPORTS / "catalyst_canvas_framework_quality_catalog.csv")


if __name__ == "__main__":
    main()
