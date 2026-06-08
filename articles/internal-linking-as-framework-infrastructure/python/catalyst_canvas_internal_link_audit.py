#!/usr/bin/env python3
"""Catalyst Canvas Internal Link Audit Engine.

Professional-grade, dependency-free audit workflow for internal-link infrastructure.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter, defaultdict, deque
from typing import Any, Iterable
import csv
import json
import re

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "internal_link_audit_config.json"
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


def severity_rank(severity: str) -> int:
    return {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}.get(severity.lower(), 99)


def validate_columns(rows: list[dict[str, str]], required: Iterable[str], dataset_name: str) -> list[Finding]:
    if not rows:
        return [Finding("critical", "schema", dataset_name, "Dataset is empty.", "Provide at least one record.")]
    columns = set(rows[0].keys())
    return [
        Finding("critical", "schema", dataset_name, f"Missing required column: {column}", "Update the dataset export or schema mapping.")
        for column in required if column not in columns
    ]


def build_graph(articles: list[dict[str, str]], links: list[dict[str, str]], config: dict[str, Any]):
    known_slugs = {row["slug"] for row in articles}
    outgoing: dict[str, set[str]] = {slug: set() for slug in known_slugs}
    incoming: dict[str, set[str]] = {slug: set() for slug in known_slugs}
    findings: list[Finding] = []
    valid_relationships = set(config["valid_relationship_types"])

    for link in links:
        source = link["source_slug"]
        target = link["target_slug"]
        relationship = link["relationship_type"]

        if source not in known_slugs:
            findings.append(Finding("high", "link_schema", source, "Link source is not present in article inventory.", "Correct source slug or add source article."))
        if target not in known_slugs:
            findings.append(Finding("high", "link_schema", target, "Link target is not present in article inventory.", "Correct target slug or add target article."))
        if relationship not in valid_relationships:
            findings.append(Finding("medium", "relationship_type", f"{source}->{target}", f"Invalid relationship type: {relationship}", "Map to controlled vocabulary."))

        outgoing.setdefault(source, set()).add(target)
        incoming.setdefault(target, set()).add(source)

    return outgoing, incoming, findings


def anchor_text_quality(links: list[dict[str, str]], config: dict[str, Any]):
    rows: list[dict[str, Any]] = []
    findings: list[Finding] = []
    weak_patterns = [pattern.lower() for pattern in config["weak_anchor_text_patterns"]]
    min_chars = int(config["anchor_text_min_characters"])
    max_chars = int(config["anchor_text_max_characters"])

    for link in links:
        anchor = link["anchor_text"].strip()
        anchor_lower = anchor.lower()
        source = link["source_slug"]
        target = link["target_slug"]
        identifier = f"{source}->{target}"
        problems: list[str] = []

        if len(anchor) < min_chars:
            problems.append("too_short")
        if len(anchor) > max_chars:
            problems.append("too_long")
        if anchor_lower in weak_patterns or re.search(r"\b(click here|read more|learn more)\b", anchor_lower):
            problems.append("generic_anchor")

        rows.append({
            "source_slug": source,
            "target_slug": target,
            "anchor_text": anchor,
            "anchor_length": len(anchor),
            "quality": "strong" if not problems else "needs review",
            "problems": "; ".join(problems) if problems else "none",
        })

        if problems:
            findings.append(Finding("medium", "anchor_text", identifier, f"Anchor text needs review: {', '.join(problems)}.", "Use descriptive anchor text."))

    return rows, findings


def link_degree_report(articles: list[dict[str, str]], outgoing: dict[str, set[str]], incoming: dict[str, set[str]], config: dict[str, Any]):
    rows: list[dict[str, Any]] = []
    findings: list[Finding] = []
    min_total = int(config["minimum_total_degree_for_published"])
    min_incoming = int(config["minimum_incoming_links_for_published"])

    for article in articles:
        slug = article["slug"]
        out_count = len(outgoing.get(slug, set()))
        in_count = len(incoming.get(slug, set()))
        total = out_count + in_count
        role = "hub" if total >= 8 else "bridge" if total >= 5 else "connector" if total >= 3 else "thinly linked" if total >= 1 else "orphaned"

        rows.append({
            "slug": slug,
            "title": article["title"],
            "cluster": article["cluster"],
            "status": article["status"],
            "article_type": article["article_type"],
            "incoming_links": in_count,
            "outgoing_links": out_count,
            "total_link_degree": total,
            "network_role": role,
            "meets_total_degree_threshold": total >= min_total,
            "meets_incoming_threshold": in_count >= min_incoming,
        })

        if article["status"] == "published" and total < min_total:
            findings.append(Finding("medium", "link_degree", slug, f"Published article has total link degree {total}, below threshold {min_total}.", "Add relevant series, cluster, method, governance, or bridge links."))
        if article["status"] == "published" and in_count < min_incoming:
            findings.append(Finding("high", "orphaned_content", slug, f"Published article has {in_count} incoming links.", "Add incoming links from article map, hub, or related pages."))

    return rows, findings


def shortest_paths_from_hubs(articles: list[dict[str, str]], outgoing: dict[str, set[str]], config: dict[str, Any]):
    slugs = {row["slug"] for row in articles}
    hubs = [hub for hub in config["hub_slugs"] if hub in slugs or hub in outgoing]
    max_depth = int(config["maximum_recommended_link_depth_from_hub"])
    distances: dict[str, int | None] = {slug: None for slug in slugs}
    queue: deque[tuple[str, int]] = deque((hub, 0) for hub in hubs)
    seen = set(hubs)

    for hub in hubs:
        if hub in distances:
            distances[hub] = 0

    while queue:
        current, depth = queue.popleft()
        for neighbor in outgoing.get(current, set()):
            if neighbor in seen:
                continue
            seen.add(neighbor)
            if neighbor in distances:
                distances[neighbor] = depth + 1
            queue.append((neighbor, depth + 1))

    findings: list[Finding] = []
    article_by_slug = {row["slug"]: row for row in articles}
    rows: list[dict[str, Any]] = []

    for slug in sorted(slugs):
        depth = distances[slug]
        reachable = depth is not None
        status = article_by_slug[slug]["status"]
        rows.append({
            "slug": slug,
            "title": article_by_slug[slug]["title"],
            "status": status,
            "minimum_link_depth_from_hub": depth if depth is not None else "unreachable",
            "reachable_from_configured_hub": reachable,
            "within_recommended_depth": reachable and depth <= max_depth,
        })
        if status == "published" and (not reachable or (depth is not None and depth > max_depth)):
            findings.append(Finding("medium", "link_depth", slug, f"Published article is not within recommended hub depth {max_depth}.", "Add or revise links from article maps, pillar pages, or cluster hubs."))

    return rows, findings


def cluster_coherence(articles: list[dict[str, str]], links: list[dict[str, str]]) -> list[dict[str, Any]]:
    cluster_by_slug = {row["slug"]: row["cluster"] for row in articles}
    total_by_cluster: Counter[str] = Counter()
    internal_by_cluster: Counter[str] = Counter()
    bridge_by_cluster: Counter[str] = Counter()

    for link in links:
        source_cluster = cluster_by_slug.get(link["source_slug"], "unknown")
        target_cluster = cluster_by_slug.get(link["target_slug"], "unknown")
        total_by_cluster[source_cluster] += 1
        if source_cluster == target_cluster:
            internal_by_cluster[source_cluster] += 1
        else:
            bridge_by_cluster[source_cluster] += 1

    rows: list[dict[str, Any]] = []
    for cluster in sorted(set(total_by_cluster) | set(internal_by_cluster) | set(bridge_by_cluster)):
        total = total_by_cluster[cluster]
        internal = internal_by_cluster[cluster]
        bridge = bridge_by_cluster[cluster]
        rows.append({
            "cluster": cluster,
            "total_outgoing_links": total,
            "within_cluster_links": internal,
            "bridge_links": bridge,
            "cluster_coherence": round(internal / total, 4) if total else 0,
            "bridge_rate": round(bridge / total, 4) if total else 0,
            "interpretation": "cohesive" if total and internal / total >= 0.5 else "bridge-heavy or underdeveloped",
        })
    return rows


def relationship_type_summary(links: list[dict[str, str]]) -> list[dict[str, Any]]:
    counts = Counter(row["relationship_type"] for row in links)
    return [{"relationship_type": rel, "link_count": count} for rel, count in sorted(counts.items())]


def connected_components(articles: list[dict[str, str]], outgoing: dict[str, set[str]]) -> list[dict[str, Any]]:
    graph: dict[str, set[str]] = {row["slug"]: set() for row in articles}
    for source, targets in outgoing.items():
        for target in targets:
            graph.setdefault(source, set()).add(target)
            graph.setdefault(target, set()).add(source)

    seen: set[str] = set()
    rows: list[dict[str, Any]] = []
    component_id = 1
    for node in sorted(graph):
        if node in seen:
            continue
        queue = deque([node])
        seen.add(node)
        component: list[str] = []
        while queue:
            current = queue.popleft()
            component.append(current)
            for neighbor in graph.get(current, set()):
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)
        rows.append({"component_id": component_id, "node_count": len(component), "slugs": "; ".join(sorted(component))})
        component_id += 1
    return rows


def link_recommendations(articles: list[dict[str, str]], links: list[dict[str, str]], degree_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    existing = {(link["source_slug"], link["target_slug"]) for link in links}
    by_cluster: dict[str, list[dict[str, str]]] = defaultdict(list)
    for article in articles:
        by_cluster[article["cluster"]].append(article)
    degree_by_slug = {row["slug"]: row for row in degree_rows}
    recommendations: list[dict[str, Any]] = []

    for cluster, cluster_articles in by_cluster.items():
        published = [article for article in cluster_articles if article["status"] == "published"]
        hubs = [article for article in published if article["article_type"] in {"pillar_map", "method", "foundational"}]
        for source in hubs:
            for target in published:
                if source["slug"] == target["slug"] or (source["slug"], target["slug"]) in existing:
                    continue
                target_degree = degree_by_slug.get(target["slug"], {}).get("total_link_degree", 0)
                recommendations.append({
                    "source_slug": source["slug"],
                    "target_slug": target["slug"],
                    "cluster": cluster,
                    "recommendation_type": "same-cluster support link",
                    "recommended_relationship_type": "topic_cluster",
                    "priority": "high" if target_degree < 3 else "medium",
                })
    return recommendations[:50] or [{"source_slug": "none", "target_slug": "none", "cluster": "none", "recommendation_type": "none", "recommended_relationship_type": "none", "priority": "none"}]


def build_catalog_export(articles: list[dict[str, str]], degree_rows: list[dict[str, Any]], depth_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    degree_by_slug = {row["slug"]: row for row in degree_rows}
    depth_by_slug = {row["slug"]: row for row in depth_rows}
    rows: list[dict[str, Any]] = []
    for article in articles:
        slug = article["slug"]
        degree = degree_by_slug.get(slug, {})
        depth = depth_by_slug.get(slug, {})
        rows.append({
            "catalog_product": "Catalyst Canvas",
            "series": "Content Frameworks",
            "slug": slug,
            "title": article["title"],
            "cluster": article["cluster"],
            "status": article["status"],
            "article_type": article["article_type"],
            "incoming_links": degree.get("incoming_links", 0),
            "outgoing_links": degree.get("outgoing_links", 0),
            "total_link_degree": degree.get("total_link_degree", 0),
            "network_role": degree.get("network_role", "unknown"),
            "minimum_link_depth_from_hub": depth.get("minimum_link_depth_from_hub", "unknown"),
            "github_path": f"articles/{slug}/",
        })
    return rows


def build_governance_queue(existing_queue: list[dict[str, str]], findings: list[Finding]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in existing_queue:
        rows.append({"source": "editorial_review_queue", "severity": item["severity"], "category": item["issue_type"], "identifier": item["identifier"], "message": item["review_note"], "recommended_action": "Resolve through editorial governance workflow."})
    for finding in findings:
        rows.append({"source": "automated_audit", "severity": finding.severity, "category": finding.category, "identifier": finding.identifier, "message": finding.message, "recommended_action": finding.recommended_action})
    rows.sort(key=lambda row: (severity_rank(row["severity"]), row["category"], row["identifier"]))
    return rows or [{"source": "none", "severity": "info", "category": "none", "identifier": "none", "message": "No findings.", "recommended_action": "No action."}]


def markdown_summary(report: dict[str, Any]) -> str:
    lines = [
        "# Internal Linking as Framework Infrastructure Audit",
        "",
        f"Generated: {report['generated_at']}",
        "",
        "## Counts",
        "",
        f"- Articles: {report['counts']['articles']}",
        f"- Links: {report['counts']['links']}",
        f"- Findings: {report['counts']['findings']}",
        f"- Governance queue items: {report['counts']['governance_queue']}",
        "",
        "## High and Medium Governance Items",
        "",
    ]
    important = [item for item in report["governance_queue"] if item["severity"] in {"critical", "high", "medium"}]
    if not important:
        lines.append("- No high or medium governance items.")
    else:
        for item in important[:30]:
            lines.append(f"- **{item['severity'].upper()}** `{item['identifier']}` — {item['message']}")
    lines.append("")
    lines.append("This report uses synthetic data and demonstrates Catalyst Canvas-style internal-link infrastructure diagnostics.")
    return "\n".join(lines) + "\n"


def main() -> None:
    ensure_dirs()
    config = read_json(CONFIG_PATH)
    articles = read_csv(DATA / "article_inventory.csv")
    links = read_csv(DATA / "internal_links.csv")
    existing_queue = read_csv(DATA / "editorial_review_queue.csv")

    findings: list[Finding] = []
    findings.extend(validate_columns(articles, config["required_article_fields"], "article_inventory"))
    findings.extend(validate_columns(links, config["required_link_fields"], "internal_links"))
    outgoing, incoming, graph_findings = build_graph(articles, links, config)
    findings.extend(graph_findings)
    anchor_rows, anchor_findings = anchor_text_quality(links, config)
    findings.extend(anchor_findings)
    degree_rows, degree_findings = link_degree_report(articles, outgoing, incoming, config)
    findings.extend(degree_findings)
    depth_rows, depth_findings = shortest_paths_from_hubs(articles, outgoing, config)
    findings.extend(depth_findings)

    coherence_rows = cluster_coherence(articles, links)
    relationship_rows = relationship_type_summary(links)
    component_rows = connected_components(articles, outgoing)
    recommendation_rows = link_recommendations(articles, links, degree_rows)
    catalog_rows = build_catalog_export(articles, degree_rows, depth_rows)
    governance_rows = build_governance_queue(existing_queue, findings)

    write_csv(TABLES / "internal_link_degree_report.csv", degree_rows)
    write_csv(TABLES / "link_depth_from_hub_report.csv", depth_rows)
    write_csv(TABLES / "cluster_coherence_report.csv", coherence_rows)
    write_csv(TABLES / "relationship_type_summary.csv", relationship_rows)
    write_csv(TABLES / "anchor_text_quality_report.csv", anchor_rows)
    write_csv(TABLES / "connected_components_report.csv", component_rows)
    write_csv(TABLES / "internal_link_recommendations.csv", recommendation_rows)
    write_csv(TABLES / "governance_review_queue.csv", governance_rows)
    write_csv(CATALOG_EXPORTS / "catalyst_canvas_internal_link_catalog.csv", catalog_rows)

    report = {
        "article": "Internal Linking as Framework Infrastructure",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "counts": {"articles": len(articles), "links": len(links), "findings": len(findings), "governance_queue": len(governance_rows), "connected_components": len(component_rows)},
        "degree_report": degree_rows,
        "link_depth_report": depth_rows,
        "cluster_coherence": coherence_rows,
        "relationship_type_summary": relationship_rows,
        "anchor_text_quality": anchor_rows,
        "connected_components": component_rows,
        "recommendations": recommendation_rows,
        "governance_queue": governance_rows,
        "catalog_export_preview": catalog_rows[:5],
    }

    write_json(REPORTS / "catalyst_canvas_internal_link_audit.json", report)
    write_json(AUDIT_LOGS / "internal_link_findings.json", [asdict(finding) for finding in findings])
    (REPORTS / "catalyst_canvas_internal_link_audit.md").write_text(markdown_summary(report), encoding="utf-8")
    print("Catalyst Canvas internal-link audit complete.")


if __name__ == "__main__":
    main()
