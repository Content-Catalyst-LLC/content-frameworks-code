#!/usr/bin/env python3
"""
Catalyst Canvas Content Audit and Framework Governance Engine

Professional-grade, dependency-free audit workflow for:
"Content Audits and Framework Governance."

This script audits:
- article inventory schema
- metadata completeness
- coverage by cluster and status
- evidence readiness
- internal-link health
- freshness and review cycles
- accessibility readiness
- duplicate and overlap risks
- framework-health scoring
- governance review queues
- Catalyst Canvas catalog exports

Uses only the Python standard library.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timezone, date
from collections import Counter, defaultdict
from typing import Any, Iterable
import csv
import json

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "content_audit_governance_config.json"
DATA = ROOT / "data"
TABLES = ROOT / "outputs" / "tables"
REPORTS = ROOT / "outputs" / "reports"
AUDIT_LOGS = ROOT / "outputs" / "audit_logs"
CATALOG_EXPORTS = ROOT / "outputs" / "catalog_exports"


@dataclass(frozen=True)
class Finding:
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
        raise ValueError(f"No rows to write: {path}")
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


def parse_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def severity_rank(severity: str) -> int:
    return {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}.get(severity.lower(), 99)


def validate_columns(rows: list[dict[str, str]], required: Iterable[str], dataset_name: str) -> list[Finding]:
    if not rows:
        return [Finding("critical", "schema", dataset_name, "Dataset is empty.", "Provide at least one record.")]

    columns = set(rows[0].keys())
    findings: list[Finding] = []

    for column in required:
        if column not in columns:
            findings.append(
                Finding(
                    "critical",
                    "schema",
                    dataset_name,
                    f"Missing required column: {column}",
                    "Update the export or schema mapping.",
                )
            )

    return findings


def metadata_audit(records: list[dict[str, str]], config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[Finding]]:
    required = config["required_metadata_fields"]
    threshold = float(config["thresholds"]["metadata_completion_minimum"])
    findings: list[Finding] = []
    rows: list[dict[str, Any]] = []

    for record in records:
        completed = [field for field in required if yes(record.get(field, ""))]
        missing = [field for field in required if field not in completed]
        completion_rate = len(completed) / len(required) if required else 1.0

        rows.append(
            {
                "slug": record["slug"],
                "title": record["title"],
                "status": record["status"],
                "cluster": record["cluster"],
                "completed_fields": len(completed),
                "required_fields": len(required),
                "metadata_completion_rate": round(completion_rate, 4),
                "missing_fields": "; ".join(missing) if missing else "none",
                "metadata_status": "ready" if completion_rate >= threshold else "needs metadata work",
            }
        )

        if record["status"] == "published" and completion_rate < threshold:
            findings.append(
                Finding(
                    "medium",
                    "metadata",
                    record["slug"],
                    f"Published article metadata completion is {completion_rate:.0%}, below threshold {threshold:.0%}.",
                    "Complete required metadata fields before the next governance review.",
                )
            )

    return rows, findings


def coverage_audit(records: list[dict[str, str]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    status_by_cluster: dict[str, Counter[str]] = defaultdict(Counter)
    type_by_cluster: dict[str, Counter[str]] = defaultdict(Counter)

    for record in records:
        status_by_cluster[record["cluster"]][record["status"]] += 1
        type_by_cluster[record["cluster"]][record["article_type"]] += 1

    coverage_rows: list[dict[str, Any]] = []
    type_rows: list[dict[str, Any]] = []

    for cluster in sorted(status_by_cluster):
        counts = status_by_cluster[cluster]
        total = sum(counts.values())
        published = counts["published"]
        planned = counts["planned"]
        draft = counts["draft"]
        review = counts["review"]
        needs_update = counts["needs update"]
        archive_candidate = counts["archive candidate"]

        coverage_rows.append(
            {
                "cluster": cluster,
                "published": published,
                "planned": planned,
                "draft": draft,
                "review": review,
                "needs_update": needs_update,
                "archive_candidate": archive_candidate,
                "total": total,
                "published_coverage_rate": round(published / total, 4) if total else 0.0,
                "active_gap_count": planned + draft + review + needs_update,
                "coverage_status": "healthy" if total and published / total >= 0.6 else "needs development",
            }
        )

        for article_type, count in sorted(type_by_cluster[cluster].items()):
            type_rows.append(
                {
                    "cluster": cluster,
                    "article_type": article_type,
                    "article_count": count,
                }
            )

    return coverage_rows, type_rows


def link_health(records: list[dict[str, str]], links: list[dict[str, str]], config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[Finding]]:
    min_total = int(config["thresholds"]["minimum_total_links_for_published"])
    min_incoming = int(config["thresholds"]["minimum_incoming_links_for_published"])

    incoming = Counter(link["target_slug"] for link in links)
    outgoing = Counter(link["source_slug"] for link in links)
    known = {record["slug"] for record in records}
    findings: list[Finding] = []
    rows: list[dict[str, Any]] = []

    for link in links:
        if link["source_slug"] not in known:
            findings.append(
                Finding(
                    "high",
                    "link_schema",
                    link["source_slug"],
                    "Internal-link source is missing from content inventory.",
                    "Correct source slug or add article to inventory.",
                )
            )
        if link["target_slug"] not in known and link["target_slug"] != "content-frameworks":
            findings.append(
                Finding(
                    "high",
                    "link_schema",
                    link["target_slug"],
                    "Internal-link target is missing from content inventory.",
                    "Correct target slug or add article to inventory.",
                )
            )

    for record in records:
        slug = record["slug"]
        in_count = incoming[slug]
        out_count = outgoing[slug]
        total = in_count + out_count
        link_score = min(total / max(min_total * 2, 1), 1.0)

        if total >= 8:
            role = "hub"
        elif total >= 5:
            role = "bridge"
        elif total >= 3:
            role = "connector"
        elif total >= 1:
            role = "thinly linked"
        else:
            role = "orphaned"

        rows.append(
            {
                "slug": slug,
                "title": record["title"],
                "status": record["status"],
                "incoming_links": in_count,
                "outgoing_links": out_count,
                "total_link_degree": total,
                "network_role": role,
                "link_health_score": round(link_score, 4),
                "meets_total_link_threshold": total >= min_total,
                "meets_incoming_threshold": in_count >= min_incoming,
            }
        )

        if record["status"] == "published" and in_count < min_incoming:
            findings.append(
                Finding(
                    "high",
                    "internal_links",
                    slug,
                    f"Published article has {in_count} incoming links.",
                    "Add links from the article map, cluster hub, or related articles.",
                )
            )

        if record["status"] == "published" and total < min_total:
            findings.append(
                Finding(
                    "medium",
                    "internal_links",
                    slug,
                    f"Published article has total link degree {total}, below threshold {min_total}.",
                    "Add relevant prerequisite, cluster, method, or governance links.",
                )
            )

    return rows, findings


def evidence_audit(records: list[dict[str, str]], evidence_register: list[dict[str, str]], config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[Finding]]:
    threshold = float(config["thresholds"]["evidence_readiness_minimum"])
    evidence_count = Counter(row["slug"] for row in evidence_register)
    high_authority_count = Counter(row["slug"] for row in evidence_register if row["authority_level"] == "high")
    ready_count = Counter(row["slug"] for row in evidence_register if row["review_status"] == "ready")
    findings: list[Finding] = []
    rows: list[dict[str, Any]] = []

    for record in records:
        slug = record["slug"]
        field_score = (
            int(yes(record.get("references", ""))) +
            int(yes(record.get("evidence_notes", ""))) +
            int(yes(record.get("limitations", "")))
        ) / 3

        register_support = min(evidence_count[slug] / 3, 1.0)
        authority_support = min(high_authority_count[slug] / 2, 1.0)
        readiness_support = min(ready_count[slug] / max(evidence_count[slug], 1), 1.0) if evidence_count[slug] else 0.0

        score = 0.40 * field_score + 0.25 * register_support + 0.20 * authority_support + 0.15 * readiness_support

        rows.append(
            {
                "slug": slug,
                "title": record["title"],
                "status": record["status"],
                "evidence_field_score": round(field_score, 4),
                "evidence_register_count": evidence_count[slug],
                "high_authority_sources": high_authority_count[slug],
                "ready_evidence_records": ready_count[slug],
                "evidence_readiness_score": round(score, 4),
                "evidence_status": "ready" if score >= threshold else "needs evidence review",
            }
        )

        if record["status"] == "published" and score < threshold:
            findings.append(
                Finding(
                    "medium",
                    "evidence",
                    slug,
                    f"Evidence readiness score is {score:.2f}, below threshold {threshold:.2f}.",
                    "Review references, evidence notes, source authority, and limitations.",
                )
            )

    return rows, findings


def freshness_audit(records: list[dict[str, str]], config: dict[str, Any], today: date) -> tuple[list[dict[str, Any]], list[Finding]]:
    cycles = config["review_cycles_by_article_type"]
    findings: list[Finding] = []
    rows: list[dict[str, Any]] = []

    for record in records:
        article_type = record["article_type"]
        fallback_cycle = int(cycles.get(article_type, 365))
        review_cycle = int(record.get("review_cycle_days", "") or fallback_cycle)
        reviewed = parse_date(record.get("last_reviewed_date", ""))

        if reviewed is None:
            age = None
            score = 0.0
            status = "missing review date"
        else:
            age = (today - reviewed).days
            score = max(0.0, min(1.0, 1 - (age / max(review_cycle, 1))))
            status = "fresh" if age <= review_cycle else "review overdue"

        rows.append(
            {
                "slug": record["slug"],
                "title": record["title"],
                "status": record["status"],
                "article_type": article_type,
                "last_reviewed_date": record.get("last_reviewed_date", ""),
                "review_cycle_days": review_cycle,
                "content_age_days": age if age is not None else "unknown",
                "freshness_score": round(score, 4),
                "freshness_status": status,
            }
        )

        if record["status"] == "published" and status != "fresh":
            findings.append(
                Finding(
                    "medium",
                    "freshness",
                    record["slug"],
                    f"Freshness status is {status}.",
                    "Schedule article review and update last-reviewed metadata.",
                )
            )

    return rows, findings


def accessibility_audit(records: list[dict[str, str]], config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[Finding]]:
    threshold = float(config["thresholds"]["accessibility_readiness_minimum"])
    findings: list[Finding] = []
    rows: list[dict[str, Any]] = []

    for record in records:
        score = (
            int(yes(record.get("image_alt", ""))) +
            int(yes(record.get("accessibility_notes", ""))) +
            int(yes(record.get("footer_navigation", ""))) +
            int(yes(record.get("series_context", "")))
        ) / 4

        rows.append(
            {
                "slug": record["slug"],
                "title": record["title"],
                "status": record["status"],
                "accessibility_readiness_score": round(score, 4),
                "accessibility_status": "ready" if score >= threshold else "needs accessibility review",
            }
        )

        if record["status"] == "published" and score < threshold:
            findings.append(
                Finding(
                    "medium",
                    "accessibility",
                    record["slug"],
                    f"Accessibility readiness score is {score:.2f}, below threshold {threshold:.2f}.",
                    "Review image alt text, link clarity, headings, navigation, and accessibility notes.",
                )
            )

    return rows, findings


def duplication_audit(records: list[dict[str, str]]) -> tuple[list[dict[str, Any]], list[Finding]]:
    findings: list[Finding] = []
    rows: list[dict[str, Any]] = []

    for record in records:
        risk = record.get("duplicate_risk", "low").lower()
        if risk == "high":
            severity = "high"
        elif risk == "medium":
            severity = "medium"
        else:
            severity = "low"

        rows.append(
            {
                "slug": record["slug"],
                "title": record["title"],
                "cluster": record["cluster"],
                "duplicate_risk": risk,
                "review_priority": severity,
            }
        )

        if risk in {"medium", "high"}:
            findings.append(
                Finding(
                    severity,
                    "duplication",
                    record["slug"],
                    f"Duplicate or overlap risk is marked {risk}.",
                    "Review conceptual boundaries, merge candidates, redirects, and article differentiation.",
                )
            )

    return rows, findings


def taxonomy_coverage(records: list[dict[str, str]], taxonomy: list[dict[str, str]]) -> tuple[list[dict[str, Any]], list[Finding]]:
    status_by_cluster: dict[str, Counter[str]] = defaultdict(Counter)
    for record in records:
        status_by_cluster[record["cluster"]][record["status"]] += 1

    findings: list[Finding] = []
    rows: list[dict[str, Any]] = []

    for category in taxonomy:
        cluster = category["category"]
        counts = status_by_cluster[cluster]
        total = sum(counts.values())
        published = counts["published"]
        planned = counts["planned"]
        coverage_rate = published / total if total else 0.0

        rows.append(
            {
                "category": cluster,
                "expected_role": category["expected_role"],
                "total_articles": total,
                "published_articles": published,
                "planned_articles": planned,
                "coverage_rate": round(coverage_rate, 4),
                "taxonomy_status": "active" if total else "missing from inventory sample",
            }
        )

        if total == 0:
            findings.append(
                Finding(
                    "low",
                    "taxonomy",
                    cluster,
                    "Taxonomy category has no articles in the current inventory sample.",
                    "Confirm whether this category should be represented in the current audit.",
                )
            )

    return rows, findings


def framework_health(
    records: list[dict[str, str]],
    config: dict[str, Any],
    metadata_rows: list[dict[str, Any]],
    link_rows: list[dict[str, Any]],
    evidence_rows: list[dict[str, Any]],
    freshness_rows: list[dict[str, Any]],
    accessibility_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[Finding]]:
    weights = config["framework_health_weights"]
    threshold = float(config["thresholds"]["framework_health_minimum"])

    metadata_by_slug = {row["slug"]: row for row in metadata_rows}
    link_by_slug = {row["slug"]: row for row in link_rows}
    evidence_by_slug = {row["slug"]: row for row in evidence_rows}
    freshness_by_slug = {row["slug"]: row for row in freshness_rows}
    accessibility_by_slug = {row["slug"]: row for row in accessibility_rows}

    findings: list[Finding] = []
    rows: list[dict[str, Any]] = []

    for record in records:
        slug = record["slug"]
        metadata_score = float(metadata_by_slug[slug]["metadata_completion_rate"])
        link_score = float(link_by_slug[slug]["link_health_score"])
        evidence_score = float(evidence_by_slug[slug]["evidence_readiness_score"])
        freshness_score = float(freshness_by_slug[slug]["freshness_score"])
        accessibility_score = float(accessibility_by_slug[slug]["accessibility_readiness_score"])
        governance_score = 1.0 if yes(record.get("governance_notes", "")) else 0.5 if record["status"] == "published" else 0.25

        health = (
            weights["metadata"] * metadata_score
            + weights["links"] * link_score
            + weights["evidence"] * evidence_score
            + weights["freshness"] * freshness_score
            + weights["governance"] * governance_score
            + weights["accessibility"] * accessibility_score
        )

        status = "ready" if health >= threshold else "governance review"

        rows.append(
            {
                "slug": slug,
                "title": record["title"],
                "status": record["status"],
                "cluster": record["cluster"],
                "article_type": record["article_type"],
                "metadata_score": round(metadata_score, 4),
                "link_score": round(link_score, 4),
                "evidence_score": round(evidence_score, 4),
                "freshness_score": round(freshness_score, 4),
                "governance_score": round(governance_score, 4),
                "accessibility_score": round(accessibility_score, 4),
                "framework_health_score": round(health, 4),
                "health_status": status,
            }
        )

        if record["status"] == "published" and health < threshold:
            findings.append(
                Finding(
                    "medium",
                    "framework_health",
                    slug,
                    f"Framework health score is {health:.2f}, below threshold {threshold:.2f}.",
                    "Review metadata, links, evidence, freshness, governance, and accessibility.",
                )
            )

    return rows, findings


def governance_queue(existing_queue: list[dict[str, str]], findings: list[Finding]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for item in existing_queue:
        rows.append(
            {
                "source": "manual_review_queue",
                "severity": item["severity"],
                "category": item["issue_type"],
                "identifier": item["slug"],
                "message": item["review_note"],
                "recommended_action": "Resolve through editorial governance workflow.",
            }
        )

    for finding in findings:
        rows.append(
            {
                "source": "automated_audit",
                "severity": finding.severity,
                "category": finding.category,
                "identifier": finding.identifier,
                "message": finding.message,
                "recommended_action": finding.recommended_action,
            }
        )

    rows.sort(key=lambda row: (severity_rank(row["severity"]), row["category"], row["identifier"]))
    return rows


def catalog_export(health_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "catalog_product": "Catalyst Canvas",
            "series": "Content Frameworks",
            "slug": row["slug"],
            "title": row["title"],
            "status": row["status"],
            "cluster": row["cluster"],
            "article_type": row["article_type"],
            "framework_health_score": row["framework_health_score"],
            "health_status": row["health_status"],
            "github_path": f"articles/{row['slug']}/",
        }
        for row in health_rows
    ]


def markdown_summary(report: dict[str, Any]) -> str:
    lines = [
        "# Catalyst Canvas Content Audit and Framework Governance Report",
        "",
        f"Generated: {report['generated_at']}",
        "",
        "## Counts",
        "",
        f"- Content records: {report['counts']['content_records']}",
        f"- Internal links: {report['counts']['internal_links']}",
        f"- Evidence records: {report['counts']['evidence_records']}",
        f"- Governance queue items: {report['counts']['governance_queue']}",
        "",
        "## High and Medium Governance Items",
        "",
    ]

    important = [
        item for item in report["governance_queue"]
        if item["severity"] in {"critical", "high", "medium"}
    ]

    if not important:
        lines.append("- No high or medium governance items.")
    else:
        for item in important[:35]:
            lines.append(f"- **{item['severity'].upper()}** `{item['identifier']}` — {item['message']}")

    lines.append("")
    lines.append("This report uses synthetic data and demonstrates Catalyst Canvas-style content audit and framework governance diagnostics.")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    ensure_dirs()
    config = read_json(CONFIG_PATH)
    records = read_csv(DATA / "content_inventory.csv")
    links = read_csv(DATA / "internal_links.csv")
    taxonomy = read_csv(DATA / "taxonomy_categories.csv")
    evidence_register = read_csv(DATA / "evidence_register.csv")
    existing_queue = read_csv(DATA / "editorial_review_queue.csv")

    findings: list[Finding] = []
    findings.extend(validate_columns(records, ["slug", "title", "status", "cluster", "article_type"], "content_inventory"))
    findings.extend(validate_columns(links, ["source_slug", "target_slug", "relationship_type", "status"], "internal_links"))

    today = date.today()

    metadata_rows, metadata_findings = metadata_audit(records, config)
    coverage_rows, article_type_rows = coverage_audit(records)
    link_rows, link_findings = link_health(records, links, config)
    evidence_rows, evidence_findings = evidence_audit(records, evidence_register, config)
    freshness_rows, freshness_findings = freshness_audit(records, config, today)
    accessibility_rows, accessibility_findings = accessibility_audit(records, config)
    duplication_rows, duplication_findings = duplication_audit(records)
    taxonomy_rows, taxonomy_findings = taxonomy_coverage(records, taxonomy)

    findings.extend(metadata_findings)
    findings.extend(link_findings)
    findings.extend(evidence_findings)
    findings.extend(freshness_findings)
    findings.extend(accessibility_findings)
    findings.extend(duplication_findings)
    findings.extend(taxonomy_findings)

    health_rows, health_findings = framework_health(
        records,
        config,
        metadata_rows,
        link_rows,
        evidence_rows,
        freshness_rows,
        accessibility_rows,
    )
    findings.extend(health_findings)

    governance_rows = governance_queue(existing_queue, findings)
    catalog_rows = catalog_export(health_rows)

    write_csv(TABLES / "metadata_audit_report.csv", metadata_rows)
    write_csv(TABLES / "coverage_audit_report.csv", coverage_rows)
    write_csv(TABLES / "article_type_distribution.csv", article_type_rows)
    write_csv(TABLES / "internal_link_health_report.csv", link_rows)
    write_csv(TABLES / "evidence_audit_report.csv", evidence_rows)
    write_csv(TABLES / "freshness_audit_report.csv", freshness_rows)
    write_csv(TABLES / "accessibility_audit_report.csv", accessibility_rows)
    write_csv(TABLES / "duplication_risk_report.csv", duplication_rows)
    write_csv(TABLES / "taxonomy_coverage_report.csv", taxonomy_rows)
    write_csv(TABLES / "framework_health_report.csv", health_rows)
    write_csv(TABLES / "governance_review_queue.csv", governance_rows)
    write_csv(CATALOG_EXPORTS / "catalyst_canvas_content_audit_catalog.csv", catalog_rows)

    report = {
        "article": "Content Audits and Framework Governance",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "config": config,
        "counts": {
            "content_records": len(records),
            "internal_links": len(links),
            "evidence_records": len(evidence_register),
            "taxonomy_categories": len(taxonomy),
            "findings": len(findings),
            "governance_queue": len(governance_rows),
        },
        "coverage": coverage_rows,
        "framework_health": health_rows,
        "taxonomy_coverage": taxonomy_rows,
        "governance_queue": governance_rows,
        "catalog_export_preview": catalog_rows[:5],
    }

    write_json(REPORTS / "catalyst_canvas_content_audit_report.json", report)
    write_json(AUDIT_LOGS / "audit_findings.json", [asdict(finding) for finding in findings])
    (REPORTS / "catalyst_canvas_content_audit_report.md").write_text(markdown_summary(report), encoding="utf-8")

    print("Catalyst Canvas content audit complete.")
    print(TABLES / "metadata_audit_report.csv")
    print(TABLES / "coverage_audit_report.csv")
    print(TABLES / "framework_health_report.csv")
    print(TABLES / "governance_review_queue.csv")
    print(REPORTS / "catalyst_canvas_content_audit_report.json")
    print(CATALOG_EXPORTS / "catalyst_canvas_content_audit_catalog.csv")


if __name__ == "__main__":
    main()
