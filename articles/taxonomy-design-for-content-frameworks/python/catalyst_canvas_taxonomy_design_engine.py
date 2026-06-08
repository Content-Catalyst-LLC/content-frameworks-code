#!/usr/bin/env python3
"""
Catalyst Canvas Taxonomy Design Engine

Professional-grade, dependency-free audit workflow for:
"Taxonomy Design for Content Frameworks"

This workflow audits:
- taxonomy categories
- article-category assignments
- primary and secondary category coverage
- tag-sprawl risk
- taxonomy metadata readiness
- category balance
- deprecated category usage
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
import statistics

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "taxonomy_design_config.json"
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


def readiness_label(score: float, ready: float = 0.85, developing: float = 0.60) -> str:
    if score >= ready:
        return "ready"
    if score >= developing:
        return "developing"
    return "review required"


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
                    "Update the source data export or mapping."
                )
            )

    return findings


def metadata_completion(row: dict[str, str], required_fields: list[str]) -> tuple[float, list[str]]:
    completed = [field for field in required_fields if yes(row.get(field, ""))]
    missing = [field for field in required_fields if field not in completed]
    return round(len(completed) / len(required_fields), 4), missing


def split_tags(tag_string: str) -> list[str]:
    return [tag.strip() for tag in tag_string.split("|") if tag.strip()]


def article_assignment_audit(
    articles: list[dict[str, str]],
    assignments: list[dict[str, str]],
    metadata: list[dict[str, str]],
    config: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[AuditFinding]]:
    required_fields = config["required_taxonomy_metadata_fields"]
    minimum_metadata = float(config["minimum_taxonomy_metadata_completion"])
    maximum_tags = int(config["maximum_tags_per_article"])

    assignment_by_article: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in assignments:
        assignment_by_article[row["slug"]].append(row)

    metadata_by_slug = {row["slug"]: row for row in metadata}

    rows: list[dict[str, Any]] = []
    findings: list[AuditFinding] = []

    for article in articles:
        slug = article["slug"]
        assigned = assignment_by_article.get(slug, [])
        primary = [row for row in assigned if row["assignment_type"] == "primary"]
        secondary = [row for row in assigned if row["assignment_type"] == "secondary"]
        facets = [row for row in assigned if row["assignment_type"] == "facet"]

        tag_list = split_tags(article["tags"])
        tag_count = len(tag_list)

        meta = metadata_by_slug.get(slug, {})
        metadata_rate, missing_metadata = metadata_completion(meta, required_fields) if meta else (0.0, required_fields)

        assignment_status = "ready"
        if len(primary) == 0:
            assignment_status = "missing primary category"
        elif len(primary) > int(config["maximum_primary_categories_per_article"]):
            assignment_status = "multiple primary categories"
        elif metadata_rate < minimum_metadata:
            assignment_status = "metadata review required"
        elif tag_count > maximum_tags:
            assignment_status = "tag sprawl review required"

        rows.append({
            "slug": slug,
            "title": article["title"],
            "status": article["status"],
            "article_role": article["article_role"],
            "reader_stage": article["reader_stage"],
            "primary_category_count": len(primary),
            "secondary_category_count": len(secondary),
            "facet_assignment_count": len(facets),
            "tag_count": tag_count,
            "tags": "; ".join(tag_list),
            "taxonomy_metadata_completion": metadata_rate,
            "missing_taxonomy_metadata": "; ".join(missing_metadata) if missing_metadata else "none",
            "assignment_status": assignment_status,
            "review_owner": article["review_owner"]
        })

        if len(primary) == 0:
            findings.append(
                AuditFinding(
                    "medium",
                    "assignment",
                    slug,
                    "Article has no primary taxonomy category.",
                    "Assign one primary category or review whether the article belongs in the system."
                )
            )

        if len(primary) > int(config["maximum_primary_categories_per_article"]):
            findings.append(
                AuditFinding(
                    "medium",
                    "assignment",
                    slug,
                    "Article has multiple primary categories.",
                    "Choose one primary category and use secondary categories or facets for cross-cutting relationships."
                )
            )

        if tag_count > maximum_tags:
            findings.append(
                AuditFinding(
                    "low",
                    "tag_sprawl",
                    slug,
                    f"Article has {tag_count} tags.",
                    "Review tags for duplication, vague labels, and unnecessary granularity."
                )
            )

        if metadata_rate < minimum_metadata and article["status"] == "published":
            findings.append(
                AuditFinding(
                    "medium",
                    "metadata",
                    slug,
                    f"Published article taxonomy metadata completion is {metadata_rate:.0%}.",
                    "Complete required taxonomy metadata fields."
                )
            )

    return rows, findings


def category_coverage_audit(
    categories: list[dict[str, str]],
    assignments: list[dict[str, str]],
    config: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[AuditFinding], float]:
    assignment_by_category: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in assignments:
        assignment_by_category[row["category_id"]].append(row)

    minimum_items = int(config["minimum_items_per_active_category"])
    rows: list[dict[str, Any]] = []
    findings: list[AuditFinding] = []
    primary_counts: list[int] = []
    deprecated_category_ids = {row["category_id"] for row in categories if row["status"] == "deprecated"}

    for category in categories:
        category_id = category["category_id"]
        assigned_items = assignment_by_category.get(category_id, [])
        primary_items = [row for row in assigned_items if row["assignment_type"] == "primary"]
        secondary_items = [row for row in assigned_items if row["assignment_type"] == "secondary"]
        facet_items = [row for row in assigned_items if row["assignment_type"] == "facet"]

        primary_count = len(primary_items)
        total_count = len(assigned_items)
        primary_counts.append(primary_count)

        category_status = "active"
        if category["status"] == "deprecated":
            category_status = "deprecated"
        elif primary_count < minimum_items:
            category_status = "thin category review"

        rows.append({
            "category_id": category_id,
            "category_name": category["category_name"],
            "parent_category_id": category["parent_category_id"] or "none",
            "category_type": category["category_type"],
            "relationship_type": category["relationship_type"],
            "status": category["status"],
            "primary_item_count": primary_count,
            "secondary_item_count": len(secondary_items),
            "facet_item_count": len(facet_items),
            "total_assignment_count": total_count,
            "category_status": category_status,
            "category_definition": category["category_definition"],
            "boundary_notes": category["boundary_notes"],
            "governance_owner": category["governance_owner"]
        })

        if category["status"] == "active" and primary_count < minimum_items:
            findings.append(
                AuditFinding(
                    "low",
                    "thin_category",
                    category_id,
                    f"Active category has only {primary_count} primary item(s).",
                    "Review whether the category should remain active, be merged, or be reserved for planned content."
                )
            )

    for assignment in assignments:
        if assignment["category_id"] in deprecated_category_ids:
            findings.append(
                AuditFinding(
                    "medium",
                    "deprecated_category",
                    assignment["slug"],
                    f"Article is assigned to deprecated category {assignment['category_id']}.",
                    "Remove deprecated category assignment or migrate to an active category."
                )
            )

    mean_count = statistics.mean(primary_counts) if primary_counts else 0.0
    stdev_count = statistics.pstdev(primary_counts) if len(primary_counts) > 1 else 0.0
    balance_score = round(1 - (stdev_count / mean_count), 4) if mean_count else 0.0

    return rows, findings, balance_score


def assignment_relationship_summary(assignments: list[dict[str, str]], categories: list[dict[str, str]]) -> list[dict[str, Any]]:
    category_by_id = {row["category_id"]: row for row in categories}
    rows = []

    for assignment_type, count in sorted(Counter(row["assignment_type"] for row in assignments).items()):
        rows.append({
            "summary_type": "assignment_type",
            "name": assignment_type,
            "count": count
        })

    for category_type, count in sorted(Counter(row["category_type"] for row in categories).items()):
        rows.append({
            "summary_type": "category_type",
            "name": category_type,
            "count": count
        })

    for relationship_type, count in sorted(Counter(row["relationship_type"] for row in categories).items()):
        rows.append({
            "summary_type": "relationship_type",
            "name": relationship_type,
            "count": count
        })

    for status, count in sorted(Counter(row["status"] for row in categories).items()):
        rows.append({
            "summary_type": "category_status",
            "name": status,
            "count": count
        })

    category_assignment_counts = Counter(row["category_id"] for row in assignments)
    for category_id, count in sorted(category_assignment_counts.items()):
        category = category_by_id.get(category_id, {})
        rows.append({
            "summary_type": "category_assignment_count",
            "name": category.get("category_name", category_id),
            "count": count
        })

    return rows


def quality_rule_audit(rules: list[dict[str, str]]) -> list[dict[str, Any]]:
    return [
        {
            "rule_id": row["rule_id"],
            "rule_name": row["rule_name"],
            "description": row["description"],
            "severity": row["severity"],
            "active": True
        }
        for row in rules
    ]


def governance_queue(findings: list[AuditFinding]) -> list[dict[str, Any]]:
    rows = [
        {
            "source": "taxonomy_design_audit",
            "severity": finding.severity,
            "category": finding.category,
            "identifier": finding.identifier,
            "message": finding.message,
            "recommended_action": finding.recommended_action
        }
        for finding in findings
    ]
    rows.sort(key=lambda item: (severity_rank(item["severity"]), item["category"], item["identifier"]))
    return rows


def catalog_export(article_rows: list[dict[str, Any]], category_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    category_review_count = Counter(row["category_status"] for row in category_rows)
    return [
        {
            "catalog_product": "Catalyst Canvas",
            "series": "Content Frameworks",
            "slug": row["slug"],
            "title": row["title"],
            "status": row["status"],
            "article_role": row["article_role"],
            "reader_stage": row["reader_stage"],
            "primary_category_count": row["primary_category_count"],
            "secondary_category_count": row["secondary_category_count"],
            "tag_count": row["tag_count"],
            "taxonomy_metadata_completion": row["taxonomy_metadata_completion"],
            "assignment_status": row["assignment_status"],
            "thin_category_count": category_review_count["thin category review"],
            "github_path": f"articles/{row['slug']}/"
        }
        for row in article_rows
    ]


def markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Catalyst Canvas Taxonomy Design Audit",
        "",
        f"Article: {report['article']}",
        f"Generated: {report['generated_at']}",
        "",
        "## Key Counts",
        "",
        f"- Articles reviewed: {report['counts']['articles']}",
        f"- Categories reviewed: {report['counts']['categories']}",
        f"- Assignments reviewed: {report['counts']['assignments']}",
        f"- Governance queue items: {report['counts']['governance_queue']}",
        f"- Taxonomy balance score: {report['taxonomy_balance_score']}",
        "",
        "## Articles Requiring Review",
        ""
    ]

    review_items = [row for row in report["article_assignment_audit"] if row["assignment_status"] != "ready"]

    if not review_items:
        lines.append("- No article assignments require review.")
    else:
        for row in review_items:
            lines.append(f"- `{row['slug']}` **{row['title']}** — {row['assignment_status']}")

    lines.extend(["", "## Categories Requiring Review", ""])

    category_items = [row for row in report["category_coverage"] if row["category_status"] == "thin category review"]

    if not category_items:
        lines.append("- No active categories require thin-category review.")
    else:
        for row in category_items:
            lines.append(f"- `{row['category_id']}` **{row['category_name']}** — {row['category_status']}")

    return "\n".join(lines) + "\n"


def main() -> None:
    ensure_dirs()

    config = read_json(CONFIG)
    articles = read_csv(DATA / "article_inventory.csv")
    categories = read_csv(DATA / "taxonomy_categories.csv")
    assignments = read_csv(DATA / "taxonomy_assignments.csv")
    metadata = read_csv(DATA / "taxonomy_metadata_inventory.csv")
    rules = read_csv(DATA / "taxonomy_quality_rules.csv")

    findings: list[AuditFinding] = []
    findings.extend(validate_columns(articles, ["slug", "title", "status", "article_role", "reader_stage", "tags"], "article_inventory"))
    findings.extend(validate_columns(categories, ["category_id", "category_name", "status", "category_type"], "taxonomy_categories"))
    findings.extend(validate_columns(assignments, ["assignment_id", "slug", "category_id", "assignment_type"], "taxonomy_assignments"))
    findings.extend(validate_columns(metadata, ["slug", "title", "status"], "taxonomy_metadata_inventory"))

    article_rows, article_findings = article_assignment_audit(articles, assignments, metadata, config)
    category_rows, category_findings, balance_score = category_coverage_audit(categories, assignments, config)
    relationship_rows = assignment_relationship_summary(assignments, categories)
    rule_rows = quality_rule_audit(rules)

    findings.extend(article_findings)
    findings.extend(category_findings)

    if balance_score < float(config["minimum_category_balance_score"]):
        findings.append(
            AuditFinding(
                "low",
                "category_balance",
                "taxonomy",
                f"Taxonomy balance score is {balance_score}.",
                "Review overloaded and thin categories, but interpret balance in context."
            )
        )

    governance_rows = governance_queue(findings)
    catalog_rows = catalog_export(article_rows, category_rows)

    write_csv(TABLES / "taxonomy_article_assignment_audit.csv", article_rows)
    write_csv(TABLES / "taxonomy_category_coverage.csv", category_rows)
    write_csv(TABLES / "taxonomy_relationship_summary.csv", relationship_rows)
    write_csv(TABLES / "taxonomy_quality_rules.csv", rule_rows)
    write_csv(TABLES / "taxonomy_governance_queue.csv", governance_rows)
    write_csv(CATALOG_EXPORTS / "catalyst_canvas_taxonomy_catalog.csv", catalog_rows)

    generated_at = datetime.now(timezone.utc).isoformat()

    report = {
        "article": "Taxonomy Design for Content Frameworks",
        "generated_at": generated_at,
        "config": config,
        "counts": {
            "articles": len(articles),
            "categories": len(categories),
            "assignments": len(assignments),
            "governance_queue": len(governance_rows)
        },
        "taxonomy_balance_score": balance_score,
        "article_assignment_audit": article_rows,
        "category_coverage": category_rows,
        "relationship_summary": relationship_rows,
        "quality_rules": rule_rows,
        "governance_queue": governance_rows
    }

    write_json(REPORTS / "catalyst_canvas_taxonomy_design_audit.json", report)
    write_json(AUDIT_LOGS / "audit_findings.json", [asdict(finding) for finding in findings])
    (REPORTS / "catalyst_canvas_taxonomy_design_audit.md").write_text(markdown_report(report), encoding="utf-8")

    print("Catalyst Canvas taxonomy design audit complete.")
    print(TABLES / "taxonomy_article_assignment_audit.csv")
    print(TABLES / "taxonomy_category_coverage.csv")
    print(TABLES / "taxonomy_governance_queue.csv")
    print(REPORTS / "catalyst_canvas_taxonomy_design_audit.json")
    print(CATALOG_EXPORTS / "catalyst_canvas_taxonomy_catalog.csv")


if __name__ == "__main__":
    main()
