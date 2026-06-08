#!/usr/bin/env python3
"""
Catalyst Canvas Framework Value Engine

Professional-grade, dependency-free audit workflow for the article:
"Why Frameworks Matter in Research, Education, and Strategic Communication."

This script demonstrates how a content-framework product layer could audit:
- article-map coverage
- metadata completeness and readiness
- framework-value scoring
- internal-link graph diagnostics
- taxonomy coverage
- governance review queues
- Catalyst Canvas catalog exports

Uses only the Python standard library so it can run in minimal environments.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timezone
import csv
import json
from collections import Counter, defaultdict, deque
from typing import Any, Iterable

ARTICLE_ROOT = Path(__file__).resolve().parents[1]
CONFIG = ARTICLE_ROOT / "config" / "catalyst_canvas_audit_config.json"
DATA = ARTICLE_ROOT / "data"
TABLES = ARTICLE_ROOT / "outputs" / "tables"
REPORTS = ARTICLE_ROOT / "outputs" / "reports"
AUDIT_LOGS = ARTICLE_ROOT / "outputs" / "audit_logs"
CATALOG_EXPORTS = ARTICLE_ROOT / "outputs" / "catalog_exports"


@dataclass(frozen=True)
class AuditFinding:
    severity: str
    category: str
    slug: str
    message: str
    recommended_action: str


@dataclass(frozen=True)
class FrameworkScore:
    framework_id: str
    framework_name: str
    domain: str
    primary_use: str
    total_score: int
    average_score: float
    product_readiness: str
    risk_severity: str
    risk_if_misused: str


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


def normalize_yes_no(value: str) -> bool:
    return value.strip().lower() in {"yes", "true", "1", "complete", "completed"}


def severity_rank(severity: str) -> int:
    return {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}.get(severity.lower(), 99)


def load_inputs() -> dict[str, Any]:
    return {
        "config": read_json(CONFIG),
        "article_map": read_csv(DATA / "content_framework_article_map.csv"),
        "frameworks": read_csv(DATA / "framework_value_examples.csv"),
        "metadata": read_csv(DATA / "metadata_inventory.csv"),
        "links": read_csv(DATA / "internal_links.csv"),
        "taxonomy": read_csv(DATA / "taxonomy_categories.csv"),
        "review_queue": read_csv(DATA / "editorial_review_queue.csv"),
    }


def validate_required_columns(rows: list[dict[str, str]], required: Iterable[str], dataset_name: str) -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    if not rows:
        return [AuditFinding("critical", "schema", dataset_name, "Dataset is empty.", "Provide at least one record.")]

    columns = set(rows[0].keys())
    for column in required:
        if column not in columns:
            findings.append(
                AuditFinding(
                    "critical",
                    "schema",
                    dataset_name,
                    f"Missing required column: {column}",
                    "Update the dataset export or schema mapping.",
                )
            )
    return findings


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
                "coverage_status": "healthy" if total and published / total >= 0.6 else "needs development",
            }
        )
    return rows


def metadata_audit(metadata: list[dict[str, str]], required_fields: list[str], threshold: float) -> tuple[list[dict[str, Any]], list[AuditFinding]]:
    rows: list[dict[str, Any]] = []
    findings: list[AuditFinding] = []

    for row in metadata:
        completed = [field for field in required_fields if normalize_yes_no(row.get(field, ""))]
        missing = [field for field in required_fields if field not in completed]
        completion_rate = len(completed) / len(required_fields) if required_fields else 1.0
        readiness = "ready" if completion_rate >= threshold else "needs metadata work"

        rows.append(
            {
                "slug": row["slug"],
                "title": row["title"],
                "status": row["status"],
                "completed_fields": len(completed),
                "required_fields": len(required_fields),
                "completion_rate": round(completion_rate, 4),
                "readiness": readiness,
                "missing_fields": "; ".join(missing) if missing else "none",
            }
        )

        if completion_rate < threshold and row["status"] == "published":
            findings.append(
                AuditFinding(
                    "medium",
                    "metadata",
                    row["slug"],
                    f"Published article metadata completion is {completion_rate:.0%}, below threshold {threshold:.0%}.",
                    "Complete missing metadata fields before the next governance review.",
                )
            )

    return rows, findings


def framework_value_scores(frameworks: list[dict[str, str]], dimensions: list[str], minimum_score: int) -> tuple[list[dict[str, Any]], list[AuditFinding]]:
    rows: list[dict[str, Any]] = []
    findings: list[AuditFinding] = []

    for row in frameworks:
        scores = [int(row[dimension]) for dimension in dimensions]
        total = sum(scores)
        average = total / len(scores)
        evidence_integrity = int(row.get("evidence_integrity", "0"))
        ethical_safety = int(row.get("ethical_safety", "0"))
        risk = row["risk_severity"].lower()

        product_readiness = "ready"
        if total < minimum_score:
            product_readiness = "score below threshold"
        if evidence_integrity < 4:
            product_readiness = "evidence review needed"
        if ethical_safety < 4:
            product_readiness = "ethical review needed"

        score = FrameworkScore(
            framework_id=row["framework_id"],
            framework_name=row["framework_name"],
            domain=row["domain"],
            primary_use=row["primary_use"],
            total_score=total,
            average_score=round(average, 3),
            product_readiness=product_readiness,
            risk_severity=row["risk_severity"],
            risk_if_misused=row["risk_if_misused"],
        )
        rows.append(asdict(score))

        if product_readiness != "ready" or severity_rank(risk) <= severity_rank("medium"):
            findings.append(
                AuditFinding(
                    "medium" if risk != "high" else "high",
                    "framework_value",
                    row["framework_id"],
                    f"{row['framework_name']} requires review: {product_readiness}; risk severity is {row['risk_severity']}.",
                    "Review evidence integrity, ethical safety, and use conditions before product deployment.",
                )
            )

    rows.sort(key=lambda item: (item["product_readiness"] != "ready", -item["total_score"], item["framework_name"]))
    return rows, findings


def graph_diagnostics(article_map: list[dict[str, str]], links: list[dict[str, str]], min_links: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[AuditFinding]]:
    known_slugs = {row["slug"] for row in article_map}
    adjacency: dict[str, set[str]] = {slug: set() for slug in known_slugs}
    reverse: dict[str, set[str]] = {slug: set() for slug in known_slugs}
    findings: list[AuditFinding] = []

    for link in links:
        source = link["source_slug"]
        target = link["target_slug"]

        if source not in known_slugs:
            findings.append(AuditFinding("medium", "links", source, "Link source is not present in article map.", "Add source to article map or correct source slug."))
        if target not in known_slugs:
            findings.append(AuditFinding("medium", "links", target, "Link target is not present in article map.", "Add target to article map or correct target slug."))

        adjacency.setdefault(source, set()).add(target)
        reverse.setdefault(target, set()).add(source)

    rows: list[dict[str, Any]] = []
    for slug in sorted(set(adjacency) | set(reverse) | known_slugs):
        outgoing = len(adjacency.get(slug, set()))
        incoming = len(reverse.get(slug, set()))
        degree = outgoing + incoming
        role = "hub" if degree >= 5 else "connector" if degree >= 3 else "thinly linked"

        rows.append(
            {
                "slug": slug,
                "outgoing_links": outgoing,
                "incoming_links": incoming,
                "total_link_degree": degree,
                "network_role": role,
                "meets_minimum_link_threshold": degree >= min_links,
            }
        )

        status = next((row["status"] for row in article_map if row["slug"] == slug), "unknown")
        if status == "published" and degree < min_links:
            findings.append(
                AuditFinding(
                    "medium",
                    "links",
                    slug,
                    f"Published article has only {degree} total internal-link relationships.",
                    "Add relevant links to strengthen series navigation and semantic connectivity.",
                )
            )

    recommendations: list[dict[str, Any]] = []
    by_cluster: dict[str, list[str]] = defaultdict(list)
    for row in article_map:
        by_cluster[row["cluster"]].append(row["slug"])

    existing_edges = {(link["source_slug"], link["target_slug"]) for link in links}
    for cluster, slugs in by_cluster.items():
        published = [row["slug"] for row in article_map if row["cluster"] == cluster and row["status"] == "published"]
        for source in published:
            for target in published:
                if source != target and (source, target) not in existing_edges:
                    recommendations.append(
                        {
                            "source_slug": source,
                            "target_slug": target,
                            "cluster": cluster,
                            "recommendation_type": "same-cluster semantic link",
                            "priority": "medium",
                        }
                    )

    return rows, recommendations[:25], findings


def taxonomy_coverage(article_map: list[dict[str, str]], taxonomy: list[dict[str, str]]) -> tuple[list[dict[str, Any]], list[AuditFinding]]:
    counts = Counter(row["cluster"] for row in article_map)
    status_by_cluster: dict[str, Counter[str]] = defaultdict(Counter)
    for row in article_map:
        status_by_cluster[row["cluster"]][row["status"]] += 1

    rows: list[dict[str, Any]] = []
    findings: list[AuditFinding] = []

    for category in taxonomy:
        name = category["category"]
        total = counts.get(name, 0)
        published = status_by_cluster[name]["published"]
        planned = status_by_cluster[name]["planned"]
        coverage_rate = published / total if total else 0.0

        rows.append(
            {
                "category": name,
                "expected_role": category["expected_role"],
                "article_count": total,
                "published": published,
                "planned": planned,
                "coverage_rate": round(coverage_rate, 4),
                "taxonomy_status": "active" if total else "missing from current article map sample",
            }
        )

        if total == 0:
            findings.append(
                AuditFinding(
                    "low",
                    "taxonomy",
                    name,
                    "Taxonomy category has no articles in the current sample.",
                    "Confirm whether this category is intentionally out of scope for the sample.",
                )
            )

    return rows, findings


def build_governance_queue(existing_queue: list[dict[str, str]], findings: list[AuditFinding]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for item in existing_queue:
        rows.append(
            {
                "source": "editorial_review_queue",
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
                "identifier": finding.slug,
                "message": finding.message,
                "recommended_action": finding.recommended_action,
            }
        )

    rows.sort(key=lambda row: (severity_rank(row["severity"]), row["category"], row["identifier"]))
    return rows


def connected_components(slugs: set[str], links: list[dict[str, str]]) -> list[list[str]]:
    graph: dict[str, set[str]] = {slug: set() for slug in slugs}
    for link in links:
        source = link["source_slug"]
        target = link["target_slug"]
        graph.setdefault(source, set()).add(target)
        graph.setdefault(target, set()).add(source)

    seen: set[str] = set()
    components: list[list[str]] = []

    for slug in sorted(graph):
        if slug in seen:
            continue
        queue = deque([slug])
        seen.add(slug)
        component: list[str] = []

        while queue:
            current = queue.popleft()
            component.append(current)
            for neighbor in graph.get(current, set()):
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)

        components.append(sorted(component))

    return components


def build_catalog_export(
    article_map: list[dict[str, str]],
    metadata_rows: list[dict[str, Any]],
    graph_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    metadata_by_slug = {row["slug"]: row for row in metadata_rows}
    graph_by_slug = {row["slug"]: row for row in graph_rows}

    export: list[dict[str, Any]] = []
    for row in article_map:
        slug = row["slug"]
        metadata = metadata_by_slug.get(slug, {})
        graph = graph_by_slug.get(slug, {})

        export.append(
            {
                "catalog_product": "Catalyst Canvas",
                "series": "Content Frameworks",
                "slug": slug,
                "title": row["title"],
                "cluster": row["cluster"],
                "status": row["status"],
                "metadata_completion_rate": metadata.get("completion_rate", 0.0),
                "metadata_readiness": metadata.get("readiness", "unknown"),
                "total_link_degree": graph.get("total_link_degree", 0),
                "network_role": graph.get("network_role", "unknown"),
                "github_path": f"articles/{slug}/",
            }
        )
    return export


def markdown_summary(payload: dict[str, Any]) -> str:
    lines = [
        "# Catalyst Canvas Framework Value Audit",
        "",
        f"Article: {payload['article']}",
        f"Generated: {payload['generated_at']}",
        "",
        "## Key Counts",
        "",
        f"- Article records: {payload['counts']['articles']}",
        f"- Framework records: {payload['counts']['frameworks']}",
        f"- Internal links: {payload['counts']['links']}",
        f"- Governance queue items: {payload['counts']['governance_queue']}",
        "",
        "## Product Notes",
        "",
        "This report is generated from synthetic data and demonstrates a professional content-system audit workflow for Catalyst Canvas-style editorial intelligence.",
        "",
        "## High and Medium Findings",
        "",
    ]

    findings = [
        item for item in payload["governance_queue"]
        if item["severity"] in {"critical", "high", "medium"}
    ]

    if not findings:
        lines.append("- No high or medium findings.")
    else:
        for item in findings[:25]:
            lines.append(f"- **{item['severity'].upper()}** `{item['identifier']}` — {item['message']}")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    ensure_dirs()
    inputs = load_inputs()

    config = inputs["config"]
    article_map = inputs["article_map"]
    frameworks = inputs["frameworks"]
    metadata = inputs["metadata"]
    links = inputs["links"]
    taxonomy = inputs["taxonomy"]
    review_queue = inputs["review_queue"]

    findings: list[AuditFinding] = []
    findings.extend(validate_required_columns(article_map, ["article_order", "title", "status", "cluster", "slug"], "article_map"))
    findings.extend(validate_required_columns(frameworks, ["framework_id", "framework_name", "domain", "primary_use"], "frameworks"))
    findings.extend(validate_required_columns(metadata, ["slug", "title", "status"], "metadata"))
    findings.extend(validate_required_columns(links, ["source_slug", "target_slug", "relationship_type"], "internal_links"))

    coverage_rows = article_map_coverage(article_map)
    metadata_rows, metadata_findings = metadata_audit(
        metadata,
        config["required_metadata_fields"],
        float(config["minimum_metadata_completion_rate"]),
    )
    findings.extend(metadata_findings)

    score_rows, score_findings = framework_value_scores(
        frameworks,
        config["framework_value_dimensions"],
        int(config["minimum_framework_value_score"]),
    )
    findings.extend(score_findings)

    graph_rows, link_recommendations, graph_findings = graph_diagnostics(
        article_map,
        links,
        int(config["minimum_internal_links_for_published_article"]),
    )
    findings.extend(graph_findings)

    taxonomy_rows, taxonomy_findings = taxonomy_coverage(article_map, taxonomy)
    findings.extend(taxonomy_findings)

    governance_rows = build_governance_queue(review_queue, findings)
    catalog_rows = build_catalog_export(article_map, metadata_rows, graph_rows)

    slugs = {row["slug"] for row in article_map}
    components = connected_components(slugs, links)

    write_csv(TABLES / "article_map_coverage_summary.csv", coverage_rows)
    write_csv(TABLES / "metadata_completeness_report.csv", metadata_rows)
    write_csv(TABLES / "framework_value_scores.csv", score_rows)
    write_csv(TABLES / "internal_link_graph_diagnostics.csv", graph_rows)
    write_csv(TABLES / "internal_link_recommendations.csv", link_recommendations)
    write_csv(TABLES / "taxonomy_coverage_summary.csv", taxonomy_rows)
    write_csv(TABLES / "governance_review_queue.csv", governance_rows)
    write_csv(CATALOG_EXPORTS / "catalyst_canvas_article_catalog.csv", catalog_rows)

    generated_at = datetime.now(timezone.utc).isoformat()
    report_payload = {
        "article": "Why Frameworks Matter in Research, Education, and Strategic Communication",
        "generated_at": generated_at,
        "config": config,
        "counts": {
            "articles": len(article_map),
            "frameworks": len(frameworks),
            "links": len(links),
            "taxonomy_categories": len(taxonomy),
            "governance_queue": len(governance_rows),
            "connected_components": len(components),
        },
        "coverage_summary": coverage_rows,
        "metadata_summary": metadata_rows,
        "framework_value_scores": score_rows,
        "graph_diagnostics": graph_rows,
        "link_recommendations": link_recommendations,
        "taxonomy_coverage": taxonomy_rows,
        "connected_components": components,
        "governance_queue": governance_rows,
        "catalog_export_preview": catalog_rows[:5],
    }

    write_json(REPORTS / "catalyst_canvas_framework_value_audit.json", report_payload)
    write_json(AUDIT_LOGS / "audit_findings.json", [asdict(finding) for finding in findings])
    (REPORTS / "catalyst_canvas_framework_value_audit.md").write_text(markdown_summary(report_payload), encoding="utf-8")

    print("Catalyst Canvas framework value audit complete.")
    print(TABLES / "article_map_coverage_summary.csv")
    print(TABLES / "metadata_completeness_report.csv")
    print(TABLES / "framework_value_scores.csv")
    print(TABLES / "internal_link_graph_diagnostics.csv")
    print(TABLES / "governance_review_queue.csv")
    print(REPORTS / "catalyst_canvas_framework_value_audit.json")
    print(CATALOG_EXPORTS / "catalyst_canvas_article_catalog.csv")


if __name__ == "__main__":
    main()
