#!/usr/bin/env python3
"""
Catalyst Canvas Digital Knowledge System Engine

Professional-grade, dependency-free audit workflow for:
"Frameworks for Digital Knowledge Systems"

This workflow audits:
- content inventories
- metadata readiness
- taxonomy coverage
- internal-link degree and relationship types
- repository readiness
- review currency
- system-health status
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
CONFIG = ROOT / "config" / "digital_knowledge_system_config.json"
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


def build_link_degrees(links: list[dict[str, str]]) -> tuple[Counter[str], Counter[str]]:
    outgoing = Counter(row["source_slug"] for row in links)
    incoming = Counter(row["target_slug"] for row in links)
    return outgoing, incoming


def repository_score(row: dict[str, str], repository_fields: list[str]) -> tuple[float, list[str]]:
    completed = [field for field in repository_fields if yes(row.get(field, ""))]
    missing = [field for field in repository_fields if field not in completed]
    return round(len(completed) / len(repository_fields), 4), missing


def content_system_audit(
    content: list[dict[str, str]],
    metadata: list[dict[str, str]],
    taxonomy: list[dict[str, str]],
    links: list[dict[str, str]],
    repositories: list[dict[str, str]],
    config: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[AuditFinding]]:
    required_metadata = config["required_metadata_fields"]
    repository_fields = config["repository_fields"]
    minimum_metadata = float(config["minimum_metadata_completion"])
    minimum_link_degree = int(config["minimum_link_degree"])
    minimum_repository = float(config["minimum_repository_readiness"])
    minimum_health = float(config["minimum_system_health"])

    metadata_by_slug = {row["slug"]: row for row in metadata}
    repo_by_slug = {row["slug"]: row for row in repositories}
    taxonomy_categories = {row["category"] for row in taxonomy}
    outgoing, incoming = build_link_degrees(links)

    rows: list[dict[str, Any]] = []
    findings: list[AuditFinding] = []

    for row in content:
        slug = row["slug"]
        meta = metadata_by_slug.get(slug, {})
        repo = repo_by_slug.get(slug, {})

        metadata_rate, missing_metadata = metadata_completion(meta, required_metadata) if meta else (0.0, required_metadata)
        repo_rate, missing_repo = repository_score(repo, repository_fields) if repo else (0.0, repository_fields)

        outgoing_count = outgoing[slug]
        incoming_count = incoming[slug]
        total_degree = outgoing_count + incoming_count

        taxonomy_ready = row["cluster"] in taxonomy_categories
        review_current = yes(row["review_current"])

        coverage_score = 1.0 if row["status"] == "published" else 0.5 if row["status"] == "planned" else 0.25
        link_score = min(total_degree / max(minimum_link_degree, 1), 1.0)
        taxonomy_score = 1.0 if taxonomy_ready else 0.0
        review_score = 1.0 if review_current else 0.0

        system_health = round((coverage_score + metadata_rate + link_score + repo_rate + taxonomy_score + review_score) / 6, 4)

        health_status = readiness_label(system_health, ready=minimum_health, developing=0.55)

        rows.append({
            "slug": slug,
            "title": row["title"],
            "cluster": row["cluster"],
            "status": row["status"],
            "content_type": row["content_type"],
            "article_role": row["article_role"],
            "public_use_level": row["public_use_level"],
            "review_owner": row["review_owner"],
            "metadata_completion": metadata_rate,
            "missing_metadata": "; ".join(missing_metadata) if missing_metadata else "none",
            "outgoing_links": outgoing_count,
            "incoming_links": incoming_count,
            "total_link_degree": total_degree,
            "taxonomy_ready": taxonomy_ready,
            "repository_readiness": repo_rate,
            "missing_repository_fields": "; ".join(missing_repo) if missing_repo else "none",
            "review_current": review_current,
            "system_health_score": system_health,
            "system_health_status": health_status
        })

        if row["status"] == "published" and metadata_rate < minimum_metadata:
            findings.append(
                AuditFinding(
                    "medium",
                    "metadata",
                    slug,
                    f"Published content metadata completion is {metadata_rate:.0%}.",
                    "Complete required metadata fields."
                )
            )

        if row["status"] == "published" and total_degree < minimum_link_degree:
            findings.append(
                AuditFinding(
                    "medium",
                    "internal_links",
                    slug,
                    f"Published content has link degree {total_degree}.",
                    "Add meaningful internal links to strengthen relationship infrastructure."
                )
            )

        if not taxonomy_ready:
            findings.append(
                AuditFinding(
                    "medium",
                    "taxonomy",
                    slug,
                    f"Content cluster `{row['cluster']}` is not present in taxonomy categories.",
                    "Update taxonomy or correct the content cluster field."
                )
            )

        if row["status"] == "published" and repo_rate < minimum_repository:
            findings.append(
                AuditFinding(
                    "low",
                    "repository",
                    slug,
                    f"Repository readiness is {repo_rate:.0%}.",
                    "Add README, workflows, generated outputs, SQL schemas, and governance documentation where repository support is expected."
                )
            )

        if row["status"] == "published" and not review_current:
            findings.append(
                AuditFinding(
                    "medium",
                    "review_currency",
                    slug,
                    "Published content review is not current.",
                    "Schedule review and update the review metadata."
                )
            )

        if system_health < minimum_health:
            findings.append(
                AuditFinding(
                    "medium",
                    "system_health",
                    slug,
                    f"System health score is {system_health:.0%}.",
                    "Review metadata, links, taxonomy, repository readiness, and review status."
                )
            )

    return rows, findings


def cluster_coverage(content: list[dict[str, str]]) -> list[dict[str, Any]]:
    cluster_counts = Counter(row["cluster"] for row in content)
    published_counts = Counter(row["cluster"] for row in content if row["status"] == "published")

    rows = []
    for cluster in sorted(cluster_counts):
        total = cluster_counts[cluster]
        published = published_counts[cluster]
        coverage = round(published / total, 4) if total else 0.0
        rows.append({
            "cluster": cluster,
            "published_items": published,
            "total_items": total,
            "planned_or_unpublished_items": total - published,
            "coverage_rate": coverage,
            "coverage_status": readiness_label(coverage, ready=0.75, developing=0.40)
        })
    return rows


def link_type_summary(links: list[dict[str, str]]) -> list[dict[str, Any]]:
    return [
        {"relationship_type": relationship_type, "link_count": count}
        for relationship_type, count in sorted(Counter(row["relationship_type"] for row in links).items())
    ]


def repository_readiness(repositories: list[dict[str, str]], config: dict[str, Any]) -> list[dict[str, Any]]:
    repository_fields = config["repository_fields"]
    rows = []

    for row in repositories:
        score, missing = repository_score(row, repository_fields)
        rows.append({
            "slug": row["slug"],
            "repository_url": row["repository_url"],
            "repository_score": score,
            "missing_repository_fields": "; ".join(missing) if missing else "none",
            "repository_status": readiness_label(score, ready=float(config["minimum_repository_readiness"]), developing=0.50)
        })

    return rows


def taxonomy_coverage(content: list[dict[str, str]], taxonomy: list[dict[str, str]]) -> list[dict[str, Any]]:
    counts = Counter(row["cluster"] for row in content)

    return [
        {
            "category": row["category"],
            "expected_role": row["expected_role"],
            "governance_owner": row["governance_owner"],
            "content_count_in_sample": counts[row["category"]],
            "taxonomy_status": "active" if counts[row["category"]] else "missing from sample"
        }
        for row in taxonomy
    ]


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
            "source": "digital_knowledge_system_audit",
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


def catalog_export(system_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "catalog_product": "Catalyst Canvas",
            "series": "Content Frameworks",
            "slug": row["slug"],
            "title": row["title"],
            "cluster": row["cluster"],
            "status": row["status"],
            "content_type": row["content_type"],
            "article_role": row["article_role"],
            "metadata_completion": row["metadata_completion"],
            "total_link_degree": row["total_link_degree"],
            "repository_readiness": row["repository_readiness"],
            "system_health_score": row["system_health_score"],
            "system_health_status": row["system_health_status"],
            "github_path": f"articles/{row['slug']}/"
        }
        for row in system_rows
    ]


def markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Catalyst Canvas Digital Knowledge System Audit",
        "",
        f"Article: {report['article']}",
        f"Generated: {report['generated_at']}",
        "",
        "## Key Counts",
        "",
        f"- Content items reviewed: {report['counts']['content_items']}",
        f"- Metadata records reviewed: {report['counts']['metadata_records']}",
        f"- Taxonomy categories reviewed: {report['counts']['taxonomy_categories']}",
        f"- Internal links reviewed: {report['counts']['internal_links']}",
        f"- Repository records reviewed: {report['counts']['repositories']}",
        f"- Governance queue items: {report['counts']['governance_queue']}",
        "",
        "## Records Requiring Review",
        ""
    ]

    review_items = [row for row in report["content_audit"] if row["system_health_status"] == "review required"]

    if not review_items:
        lines.append("- No records are below the system-health threshold.")
    else:
        for row in review_items:
            lines.append(f"- `{row['slug']}` **{row['title']}** — {row['system_health_status']}")

    return "\n".join(lines) + "\n"


def main() -> None:
    ensure_dirs()

    config = read_json(CONFIG)
    content = read_csv(DATA / "content_inventory.csv")
    metadata = read_csv(DATA / "metadata_inventory.csv")
    taxonomy = read_csv(DATA / "taxonomy_categories.csv")
    links = read_csv(DATA / "internal_links.csv")
    repositories = read_csv(DATA / "repository_inventory.csv")
    rules = read_csv(DATA / "system_quality_rules.csv")

    findings: list[AuditFinding] = []
    findings.extend(validate_columns(content, ["slug", "title", "cluster", "status", "content_type", "article_role"], "content_inventory"))
    findings.extend(validate_columns(metadata, ["slug", "title", "status"], "metadata_inventory"))
    findings.extend(validate_columns(taxonomy, ["category", "description", "expected_role"], "taxonomy_categories"))
    findings.extend(validate_columns(links, ["source_slug", "target_slug", "relationship_type"], "internal_links"))
    findings.extend(validate_columns(repositories, ["slug", "repository_url"], "repository_inventory"))

    system_rows, system_findings = content_system_audit(content, metadata, taxonomy, links, repositories, config)
    findings.extend(system_findings)

    cluster_rows = cluster_coverage(content)
    link_rows = link_type_summary(links)
    repository_rows = repository_readiness(repositories, config)
    taxonomy_rows = taxonomy_coverage(content, taxonomy)
    rule_rows = quality_rule_audit(rules)
    governance_rows = governance_queue(findings)
    catalog_rows = catalog_export(system_rows)

    content_type_summary = [
        {"content_type": content_type, "content_count": count}
        for content_type, count in sorted(Counter(row["content_type"] for row in content).items())
    ]

    article_role_summary = [
        {"article_role": article_role, "article_count": count}
        for article_role, count in sorted(Counter(row["article_role"] for row in content).items())
    ]

    write_csv(TABLES / "digital_knowledge_content_audit.csv", system_rows)
    write_csv(TABLES / "digital_knowledge_cluster_coverage.csv", cluster_rows)
    write_csv(TABLES / "digital_knowledge_link_type_summary.csv", link_rows)
    write_csv(TABLES / "digital_knowledge_repository_readiness.csv", repository_rows)
    write_csv(TABLES / "digital_knowledge_taxonomy_coverage.csv", taxonomy_rows)
    write_csv(TABLES / "digital_knowledge_content_type_summary.csv", content_type_summary)
    write_csv(TABLES / "digital_knowledge_article_role_summary.csv", article_role_summary)
    write_csv(TABLES / "digital_knowledge_quality_rules.csv", rule_rows)
    write_csv(TABLES / "digital_knowledge_governance_queue.csv", governance_rows)
    write_csv(CATALOG_EXPORTS / "catalyst_canvas_digital_knowledge_catalog.csv", catalog_rows)

    generated_at = datetime.now(timezone.utc).isoformat()

    report = {
        "article": "Frameworks for Digital Knowledge Systems",
        "generated_at": generated_at,
        "config": config,
        "counts": {
            "content_items": len(content),
            "metadata_records": len(metadata),
            "taxonomy_categories": len(taxonomy),
            "internal_links": len(links),
            "repositories": len(repositories),
            "governance_queue": len(governance_rows)
        },
        "content_audit": system_rows,
        "cluster_coverage": cluster_rows,
        "link_type_summary": link_rows,
        "repository_readiness": repository_rows,
        "taxonomy_coverage": taxonomy_rows,
        "content_type_summary": content_type_summary,
        "article_role_summary": article_role_summary,
        "quality_rules": rule_rows,
        "governance_queue": governance_rows
    }

    write_json(REPORTS / "catalyst_canvas_digital_knowledge_system_audit.json", report)
    write_json(AUDIT_LOGS / "audit_findings.json", [asdict(finding) for finding in findings])
    (REPORTS / "catalyst_canvas_digital_knowledge_system_audit.md").write_text(markdown_report(report), encoding="utf-8")

    print("Catalyst Canvas digital knowledge system audit complete.")
    print(TABLES / "digital_knowledge_content_audit.csv")
    print(TABLES / "digital_knowledge_cluster_coverage.csv")
    print(TABLES / "digital_knowledge_governance_queue.csv")
    print(REPORTS / "catalyst_canvas_digital_knowledge_system_audit.json")
    print(CATALOG_EXPORTS / "catalyst_canvas_digital_knowledge_catalog.csv")


if __name__ == "__main__":
    main()
