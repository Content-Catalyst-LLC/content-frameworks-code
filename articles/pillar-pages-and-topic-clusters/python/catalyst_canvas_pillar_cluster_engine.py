#!/usr/bin/env python3
"""
Catalyst Canvas Pillar-Cluster Engine

Professional-grade, dependency-free audit workflow for:
"Pillar Pages and Topic Clusters"

This workflow audits:
- pillar and cluster article inventories
- internal-link graph structure
- pillar coverage density
- cluster readiness
- article role coverage
- metadata completeness
- orphan and weakly linked articles
- taxonomy coverage
- governance review queue
- Catalyst Canvas catalog exports
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter, defaultdict, deque
from typing import Any, Iterable
import csv
import json

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "pillar_cluster_config.json"
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
                    "Update the source data export or mapping."
                )
            )

    return findings


def metadata_completion(row: dict[str, str], required_fields: list[str]) -> tuple[float, list[str]]:
    completed = [field for field in required_fields if yes(row.get(field, ""))]
    missing = [field for field in required_fields if field not in completed]
    return round(len(completed) / len(required_fields), 4), missing


def build_graph(links: list[dict[str, str]]) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    outgoing: dict[str, set[str]] = defaultdict(set)
    incoming: dict[str, set[str]] = defaultdict(set)

    for link in links:
        source = link["source_slug"]
        target = link["target_slug"]
        outgoing[source].add(target)
        incoming[target].add(source)

    return outgoing, incoming


def shortest_path_exists(outgoing: dict[str, set[str]], start: str, target: str, max_depth: int = 4) -> bool:
    queue = deque([(start, 0)])
    visited = {start}

    while queue:
        node, depth = queue.popleft()

        if node == target:
            return True

        if depth >= max_depth:
            continue

        for neighbor in outgoing.get(node, set()):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, depth + 1))

    return False


def article_audit(
    articles: list[dict[str, str]],
    links: list[dict[str, str]],
    metadata: list[dict[str, str]],
    config: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[AuditFinding]]:
    pillar_slug = config["pillar_slug"]
    required_metadata = config["required_metadata_fields"]
    min_metadata = float(config["minimum_metadata_completion"])
    min_degree = int(config["minimum_link_degree"])

    outgoing, incoming = build_graph(links)
    metadata_by_slug = {row["slug"]: row for row in metadata}
    article_slugs = {row["slug"] for row in articles}
    rows: list[dict[str, Any]] = []
    findings: list[AuditFinding] = []

    for article in articles:
        slug = article["slug"]
        meta = metadata_by_slug.get(slug, {})
        metadata_rate, missing_metadata = metadata_completion(meta, required_metadata) if meta else (0.0, required_metadata)

        outgoing_count = len(outgoing.get(slug, set()))
        incoming_count = len(incoming.get(slug, set()))
        total_degree = outgoing_count + incoming_count
        is_pillar = slug == pillar_slug
        links_to_pillar = pillar_slug in outgoing.get(slug, set())
        linked_from_pillar = slug in outgoing.get(pillar_slug, set())

        if is_pillar:
            architecture_role = "pillar"
        elif linked_from_pillar and links_to_pillar:
            architecture_role = "well-connected cluster article"
        elif linked_from_pillar:
            architecture_role = "pillar-linked cluster article"
        elif links_to_pillar:
            architecture_role = "cluster article linking to pillar"
        elif total_degree == 0:
            architecture_role = "orphan"
        else:
            architecture_role = "weakly connected article"

        readiness = "ready"
        if article["status"] == "planned":
            readiness = "planned"
        elif metadata_rate < min_metadata:
            readiness = "metadata review required"
        elif total_degree < min_degree:
            readiness = "link review required"
        elif not is_pillar and not links_to_pillar:
            readiness = "orientation review required"
        elif not is_pillar and not linked_from_pillar:
            readiness = "pillar coverage review required"

        rows.append({
            "slug": slug,
            "title": article["title"],
            "cluster": article["cluster"],
            "status": article["status"],
            "article_role": article["article_role"],
            "priority": article["priority"],
            "review_owner": article["review_owner"],
            "architecture_role": architecture_role,
            "outgoing_links": outgoing_count,
            "incoming_links": incoming_count,
            "total_link_degree": total_degree,
            "metadata_completion": metadata_rate,
            "missing_metadata": "; ".join(missing_metadata) if missing_metadata else "none",
            "linked_from_pillar": linked_from_pillar,
            "links_to_pillar": links_to_pillar,
            "readiness": readiness,
            "reachable_from_pillar_within_4_steps": shortest_path_exists(outgoing, pillar_slug, slug) if not is_pillar else True
        })

        if article["status"] == "published" and metadata_rate < min_metadata:
            findings.append(
                AuditFinding(
                    "medium",
                    "metadata",
                    slug,
                    f"Published article metadata completion is {metadata_rate:.0%}.",
                    "Complete required metadata fields before the next review cycle."
                )
            )

        if article["status"] == "published" and total_degree < min_degree:
            findings.append(
                AuditFinding(
                    "low",
                    "internal_links",
                    slug,
                    f"Published article has total link degree {total_degree}.",
                    "Add meaningful internal links to strengthen reader pathways."
                )
            )

        if not is_pillar and article["status"] == "published" and not links_to_pillar:
            findings.append(
                AuditFinding(
                    "medium",
                    "cluster_orientation",
                    slug,
                    "Published cluster article does not link back to the pillar page.",
                    "Add a meaningful link back to the pillar or article map."
                )
            )

        if not is_pillar and article["status"] == "published" and not linked_from_pillar:
            findings.append(
                AuditFinding(
                    "medium",
                    "pillar_coverage",
                    slug,
                    "Published cluster article is not linked from the pillar page.",
                    "Add the article to the pillar page or review whether it belongs in the cluster."
                )
            )

    for link in links:
        if link["source_slug"] not in article_slugs:
            findings.append(
                AuditFinding(
                    "low",
                    "link_integrity",
                    link["source_slug"],
                    "Internal link source is not present in the article inventory sample.",
                    "Confirm the source article exists or update the inventory."
                )
            )
        if link["target_slug"] not in article_slugs:
            findings.append(
                AuditFinding(
                    "low",
                    "link_integrity",
                    link["target_slug"],
                    "Internal link target is not present in the article inventory sample.",
                    "Confirm the target article exists or update the inventory."
                )
            )

    return rows, findings


def cluster_summary(articles: list[dict[str, str]], config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[AuditFinding]]:
    min_readiness = float(config["minimum_cluster_readiness"])
    grouped: dict[str, Counter[str]] = defaultdict(Counter)
    role_counts: dict[str, Counter[str]] = defaultdict(Counter)
    findings: list[AuditFinding] = []

    for article in articles:
        grouped[article["cluster"]][article["status"]] += 1
        role_counts[article["cluster"]][article["article_role"]] += 1

    rows = []
    for cluster in sorted(grouped):
        published = grouped[cluster]["published"]
        planned = grouped[cluster]["planned"]
        total = published + planned
        readiness = round(published / total, 4) if total else 0.0
        status = "mature" if readiness >= 0.75 else "developing" if readiness >= min_readiness else "early stage"

        rows.append({
            "cluster": cluster,
            "published_articles": published,
            "planned_articles": planned,
            "total_articles": total,
            "cluster_readiness": readiness,
            "cluster_status": status,
            "role_mix": "; ".join(f"{role}:{count}" for role, count in sorted(role_counts[cluster].items()))
        })

        if readiness < min_readiness:
            findings.append(
                AuditFinding(
                    "medium",
                    "cluster_readiness",
                    cluster,
                    f"Cluster readiness is {readiness:.0%}.",
                    "Review whether the cluster should be described as early-stage or prioritize planned articles."
                )
            )

    return rows, findings


def taxonomy_coverage(articles: list[dict[str, str]], taxonomy: list[dict[str, str]]) -> list[dict[str, Any]]:
    counts = Counter(row["cluster"] for row in articles)
    return [
        {
            "category": row["category"],
            "expected_role": row["expected_role"],
            "article_count_in_sample": counts[row["category"]],
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
            "source": "pillar_cluster_audit",
            "severity": finding.severity,
            "category": finding.category,
            "identifier": finding.identifier,
            "message": finding.message,
            "recommended_action": finding.recommended_action,
        }
        for finding in findings
    ]

    rows.sort(key=lambda item: (severity_rank(item["severity"]), item["category"], item["identifier"]))
    return rows


def catalog_export(article_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "catalog_product": "Catalyst Canvas",
            "series": "Content Frameworks",
            "slug": row["slug"],
            "title": row["title"],
            "cluster": row["cluster"],
            "status": row["status"],
            "article_role": row["article_role"],
            "architecture_role": row["architecture_role"],
            "metadata_completion": row["metadata_completion"],
            "readiness": row["readiness"],
            "github_path": f"articles/{row['slug']}/"
        }
        for row in article_rows
    ]


def markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Catalyst Canvas Pillar-Cluster Audit",
        "",
        f"Article: {report['article']}",
        f"Generated: {report['generated_at']}",
        "",
        "## Key Counts",
        "",
        f"- Articles reviewed: {report['counts']['articles']}",
        f"- Internal links reviewed: {report['counts']['links']}",
        f"- Clusters reviewed: {report['counts']['clusters']}",
        f"- Governance queue items: {report['counts']['governance_queue']}",
        f"- Pillar coverage density: {report['pillar_coverage_density']}",
        "",
        "## Articles Requiring Review",
        "",
    ]

    review_items = [row for row in report["article_audit"] if row["readiness"] not in {"ready", "planned"}]

    if not review_items:
        lines.append("- No published articles require review.")
    else:
        for row in review_items:
            lines.append(f"- `{row['slug']}` **{row['title']}** — {row['readiness']}")

    return "\n".join(lines) + "\n"


def main() -> None:
    ensure_dirs()

    config = read_json(CONFIG)
    articles = read_csv(DATA / "pillar_cluster_articles.csv")
    links = read_csv(DATA / "internal_links.csv")
    metadata = read_csv(DATA / "metadata_inventory.csv")
    taxonomy = read_csv(DATA / "taxonomy_categories.csv")
    rules = read_csv(DATA / "pillar_cluster_quality_rules.csv")

    findings: list[AuditFinding] = []
    findings.extend(validate_columns(articles, ["slug", "title", "cluster", "status", "article_role"], "pillar_cluster_articles"))
    findings.extend(validate_columns(links, ["source_slug", "target_slug", "relationship_type"], "internal_links"))
    findings.extend(validate_columns(metadata, ["slug", "title", "status"], "metadata_inventory"))

    article_rows, article_findings = article_audit(articles, links, metadata, config)
    cluster_rows, cluster_findings = cluster_summary(articles, config)
    taxonomy_rows = taxonomy_coverage(articles, taxonomy)
    rule_rows = quality_rule_audit(rules)

    findings.extend(article_findings)
    findings.extend(cluster_findings)

    governance_rows = governance_queue(findings)
    catalog_rows = catalog_export(article_rows)

    pillar_slug = config["pillar_slug"]
    pillar_links = len([row for row in links if row["source_slug"] == pillar_slug and row["relationship_type"] == "pillar_to_cluster"])
    cluster_article_count = len([row for row in articles if row["slug"] != pillar_slug and row["cluster"] == "Knowledge Architecture"])
    pillar_coverage_density = round(pillar_links / cluster_article_count, 4) if cluster_article_count else 0.0

    write_csv(TABLES / "pillar_cluster_article_audit.csv", article_rows)
    write_csv(TABLES / "pillar_cluster_coverage_summary.csv", cluster_rows)
    write_csv(TABLES / "taxonomy_pillar_cluster_coverage.csv", taxonomy_rows)
    write_csv(TABLES / "pillar_cluster_quality_rules.csv", rule_rows)
    write_csv(TABLES / "pillar_cluster_governance_queue.csv", governance_rows)
    write_csv(CATALOG_EXPORTS / "catalyst_canvas_pillar_cluster_catalog.csv", catalog_rows)

    generated_at = datetime.now(timezone.utc).isoformat()

    report = {
        "article": "Pillar Pages and Topic Clusters",
        "generated_at": generated_at,
        "config": config,
        "counts": {
            "articles": len(articles),
            "links": len(links),
            "clusters": len(cluster_rows),
            "governance_queue": len(governance_rows)
        },
        "pillar_slug": pillar_slug,
        "pillar_coverage_density": pillar_coverage_density,
        "article_audit": article_rows,
        "cluster_summary": cluster_rows,
        "taxonomy_coverage": taxonomy_rows,
        "quality_rules": rule_rows,
        "governance_queue": governance_rows
    }

    write_json(REPORTS / "catalyst_canvas_pillar_cluster_audit.json", report)
    write_json(AUDIT_LOGS / "audit_findings.json", [asdict(finding) for finding in findings])
    (REPORTS / "catalyst_canvas_pillar_cluster_audit.md").write_text(markdown_report(report), encoding="utf-8")

    print("Catalyst Canvas pillar-cluster audit complete.")
    print(TABLES / "pillar_cluster_article_audit.csv")
    print(TABLES / "pillar_cluster_coverage_summary.csv")
    print(TABLES / "pillar_cluster_governance_queue.csv")
    print(REPORTS / "catalyst_canvas_pillar_cluster_audit.json")
    print(CATALOG_EXPORTS / "catalyst_canvas_pillar_cluster_catalog.csv")


if __name__ == "__main__":
    main()
