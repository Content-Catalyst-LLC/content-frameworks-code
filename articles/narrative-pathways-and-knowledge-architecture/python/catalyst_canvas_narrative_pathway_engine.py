#!/usr/bin/env python3
"""
Catalyst Canvas Narrative Pathway Engine

Professional-grade, dependency-free audit workflow for:
"Narrative Pathways and Knowledge Architecture"

This workflow audits:
- narrative pathway article inventory
- reader states and pathway roles
- internal-link graph structure
- prerequisite and next-step coverage
- transition coverage
- pathway readiness
- metadata completeness
- orientation and bridge quality
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
CONFIG = ROOT / "config" / "narrative_pathways_config.json"
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


def build_graph(links: list[dict[str, str]]) -> tuple[dict[str, set[str]], dict[str, set[str]], dict[tuple[str, str], str]]:
    outgoing: dict[str, set[str]] = defaultdict(set)
    incoming: dict[str, set[str]] = defaultdict(set)
    edge_type: dict[tuple[str, str], str] = {}

    for link in links:
        source = link["source_slug"]
        target = link["target_slug"]
        outgoing[source].add(target)
        incoming[target].add(source)
        edge_type[(source, target)] = link["relationship_type"]

    return outgoing, incoming, edge_type


def reachable(outgoing: dict[str, set[str]], start: str, target: str, max_depth: int = 4) -> bool:
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
    required_metadata = config["required_metadata_fields"]
    minimum_metadata = float(config["minimum_metadata_completion"])
    minimum_degree = int(config["minimum_link_degree"])

    outgoing, incoming, _ = build_graph(links)
    metadata_by_slug = {row["slug"]: row for row in metadata}
    rows: list[dict[str, Any]] = []
    findings: list[AuditFinding] = []

    for article in articles:
        slug = article["slug"]
        meta = metadata_by_slug.get(slug, {})
        metadata_rate, missing_metadata = metadata_completion(meta, required_metadata) if meta else (0.0, required_metadata)

        outgoing_count = len(outgoing.get(slug, set()))
        incoming_count = len(incoming.get(slug, set()))
        total_degree = outgoing_count + incoming_count

        orientation_ready = yes(article["has_series_context"]) and yes(article["links_to_article_map"])
        bridge_ready = yes(article["has_transition_links"]) and yes(article["has_next_step"])

        readiness = "ready"
        if article["status"] == "planned":
            readiness = "planned"
        elif metadata_rate < minimum_metadata:
            readiness = "metadata review required"
        elif not orientation_ready:
            readiness = "orientation review required"
        elif not bridge_ready:
            readiness = "bridge review required"
        elif total_degree < minimum_degree:
            readiness = "link review required"

        rows.append({
            "slug": slug,
            "title": article["title"],
            "cluster": article["cluster"],
            "status": article["status"],
            "article_role": article["article_role"],
            "pathway_role": article["pathway_role"],
            "reader_state": article["reader_state"],
            "review_owner": article["review_owner"],
            "incoming_links": incoming_count,
            "outgoing_links": outgoing_count,
            "total_link_degree": total_degree,
            "metadata_completion": metadata_rate,
            "missing_metadata": "; ".join(missing_metadata) if missing_metadata else "none",
            "orientation_ready": orientation_ready,
            "bridge_ready": bridge_ready,
            "readiness": readiness
        })

        if article["status"] == "published" and metadata_rate < minimum_metadata:
            findings.append(
                AuditFinding(
                    "medium",
                    "metadata",
                    slug,
                    f"Published article metadata completion is {metadata_rate:.0%}.",
                    "Complete required metadata before the next pathway review."
                )
            )

        if article["status"] == "published" and not orientation_ready:
            findings.append(
                AuditFinding(
                    "medium",
                    "orientation",
                    slug,
                    "Published article lacks complete orientation signals.",
                    "Add series context and a link to the article map or pillar page."
                )
            )

        if article["status"] == "published" and not bridge_ready:
            findings.append(
                AuditFinding(
                    "medium",
                    "bridge_quality",
                    slug,
                    "Published article lacks transition links or next-step guidance.",
                    "Add meaningful bridge links and next-step context."
                )
            )

        if article["status"] == "published" and total_degree < minimum_degree:
            findings.append(
                AuditFinding(
                    "low",
                    "link_degree",
                    slug,
                    f"Published article has link degree {total_degree}.",
                    "Add meaningful internal links that support reader movement."
                )
            )

    return rows, findings


def pathway_audit(
    articles: list[dict[str, str]],
    links: list[dict[str, str]],
    pathways: list[dict[str, str]],
    config: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[AuditFinding]]:
    article_by_slug = {row["slug"]: row for row in articles}
    outgoing, _, _ = build_graph(links)
    minimum_readiness = float(config["minimum_pathway_readiness"])
    minimum_transition = float(config["minimum_transition_coverage"])

    rows: list[dict[str, Any]] = []
    findings: list[AuditFinding] = []

    for pathway in pathways:
        required_slugs = [item.strip() for item in pathway["required_article_slugs"].split("|") if item.strip()]
        published_required = [
            slug for slug in required_slugs
            if slug in article_by_slug and article_by_slug[slug]["status"] == "published"
        ]
        planned_required = [
            slug for slug in required_slugs
            if slug in article_by_slug and article_by_slug[slug]["status"] == "planned"
        ]
        missing_required = [slug for slug in required_slugs if slug not in article_by_slug]

        readiness = round(len(published_required) / len(required_slugs), 4) if required_slugs else 0.0

        sequential_edges_present = 0
        sequential_edges_possible = max(len(required_slugs) - 1, 0)

        for source, target in zip(required_slugs, required_slugs[1:]):
            if target in outgoing.get(source, set()) or reachable(outgoing, source, target, max_depth=2):
                sequential_edges_present += 1

        transition_coverage = round(sequential_edges_present / sequential_edges_possible, 4) if sequential_edges_possible else 1.0

        pathway_status = "ready"
        if readiness < minimum_readiness:
            pathway_status = "coverage review required"
        elif transition_coverage < minimum_transition:
            pathway_status = "transition review required"

        rows.append({
            "pathway_id": pathway["pathway_id"],
            "pathway_name": pathway["pathway_name"],
            "pathway_type": pathway["pathway_type"],
            "reader_state": pathway["reader_state"],
            "pathway_goal": pathway["pathway_goal"],
            "review_owner": pathway["review_owner"],
            "required_article_count": len(required_slugs),
            "published_required_count": len(published_required),
            "planned_required_count": len(planned_required),
            "missing_required_count": len(missing_required),
            "pathway_readiness": readiness,
            "transition_coverage": transition_coverage,
            "pathway_status": pathway_status,
            "planned_required_articles": "; ".join(planned_required) if planned_required else "none",
            "missing_required_articles": "; ".join(missing_required) if missing_required else "none"
        })

        if pathway_status != "ready":
            findings.append(
                AuditFinding(
                    "medium",
                    "pathway_readiness",
                    pathway["pathway_id"],
                    f"{pathway['pathway_name']} status: {pathway_status}.",
                    "Review missing articles, planned articles, and transition links."
                )
            )

    return rows, findings


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
            "source": "narrative_pathway_audit",
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


def catalog_export(article_rows: list[dict[str, Any]], pathway_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pathway_counts = Counter(row["reader_state"] for row in pathway_rows)

    return [
        {
            "catalog_product": "Catalyst Canvas",
            "series": "Content Frameworks",
            "slug": row["slug"],
            "title": row["title"],
            "cluster": row["cluster"],
            "status": row["status"],
            "article_role": row["article_role"],
            "pathway_role": row["pathway_role"],
            "reader_state": row["reader_state"],
            "reader_state_pathway_count": pathway_counts[row["reader_state"]],
            "metadata_completion": row["metadata_completion"],
            "readiness": row["readiness"],
            "github_path": f"articles/{row['slug']}/"
        }
        for row in article_rows
    ]


def markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Catalyst Canvas Narrative Pathway Audit",
        "",
        f"Article: {report['article']}",
        f"Generated: {report['generated_at']}",
        "",
        "## Key Counts",
        "",
        f"- Articles reviewed: {report['counts']['articles']}",
        f"- Internal links reviewed: {report['counts']['links']}",
        f"- Pathways reviewed: {report['counts']['pathways']}",
        f"- Governance queue items: {report['counts']['governance_queue']}",
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

    lines.extend(["", "## Pathways Requiring Review", ""])

    pathway_items = [row for row in report["pathway_readiness"] if row["pathway_status"] != "ready"]

    if not pathway_items:
        lines.append("- No pathways require review.")
    else:
        for row in pathway_items:
            lines.append(f"- `{row['pathway_id']}` **{row['pathway_name']}** — {row['pathway_status']}")

    return "\n".join(lines) + "\n"


def main() -> None:
    ensure_dirs()

    config = read_json(CONFIG)
    articles = read_csv(DATA / "pathway_article_inventory.csv")
    links = read_csv(DATA / "internal_links.csv")
    pathways = read_csv(DATA / "narrative_pathway_definitions.csv")
    metadata = read_csv(DATA / "metadata_inventory.csv")
    rules = read_csv(DATA / "pathway_quality_rules.csv")

    findings: list[AuditFinding] = []
    findings.extend(validate_columns(articles, ["slug", "title", "cluster", "status", "article_role", "pathway_role", "reader_state"], "pathway_article_inventory"))
    findings.extend(validate_columns(links, ["source_slug", "target_slug", "relationship_type"], "internal_links"))
    findings.extend(validate_columns(pathways, ["pathway_id", "pathway_name", "pathway_type", "required_article_slugs"], "narrative_pathway_definitions"))
    findings.extend(validate_columns(metadata, ["slug", "title", "status"], "metadata_inventory"))

    article_rows, article_findings = article_audit(articles, links, metadata, config)
    pathway_rows, pathway_findings = pathway_audit(articles, links, pathways, config)
    rule_rows = quality_rule_audit(rules)

    findings.extend(article_findings)
    findings.extend(pathway_findings)

    governance_rows = governance_queue(findings)
    catalog_rows = catalog_export(article_rows, pathway_rows)

    reader_state_summary = Counter(row["reader_state"] for row in articles)
    pathway_type_summary = Counter(row["pathway_type"] for row in pathways)
    article_role_summary = Counter(row["article_role"] for row in articles)

    write_csv(TABLES / "narrative_pathway_article_audit.csv", article_rows)
    write_csv(TABLES / "narrative_pathway_readiness.csv", pathway_rows)
    write_csv(TABLES / "narrative_pathway_quality_rules.csv", rule_rows)
    write_csv(TABLES / "narrative_pathway_governance_queue.csv", governance_rows)
    write_csv(CATALOG_EXPORTS / "catalyst_canvas_narrative_pathway_catalog.csv", catalog_rows)

    summary_rows = []
    for category, counter in [
        ("reader_state", reader_state_summary),
        ("pathway_type", pathway_type_summary),
        ("article_role", article_role_summary)
    ]:
        for name, count in sorted(counter.items()):
            summary_rows.append({"summary_type": category, "name": name, "count": count})

    write_csv(TABLES / "narrative_pathway_summary_counts.csv", summary_rows)

    generated_at = datetime.now(timezone.utc).isoformat()

    report = {
        "article": "Narrative Pathways and Knowledge Architecture",
        "generated_at": generated_at,
        "config": config,
        "counts": {
            "articles": len(articles),
            "links": len(links),
            "pathways": len(pathways),
            "governance_queue": len(governance_rows)
        },
        "reader_state_summary": dict(reader_state_summary),
        "pathway_type_summary": dict(pathway_type_summary),
        "article_role_summary": dict(article_role_summary),
        "article_audit": article_rows,
        "pathway_readiness": pathway_rows,
        "quality_rules": rule_rows,
        "governance_queue": governance_rows
    }

    write_json(REPORTS / "catalyst_canvas_narrative_pathway_audit.json", report)
    write_json(AUDIT_LOGS / "audit_findings.json", [asdict(finding) for finding in findings])
    (REPORTS / "catalyst_canvas_narrative_pathway_audit.md").write_text(markdown_report(report), encoding="utf-8")

    print("Catalyst Canvas narrative pathway audit complete.")
    print(TABLES / "narrative_pathway_article_audit.csv")
    print(TABLES / "narrative_pathway_readiness.csv")
    print(TABLES / "narrative_pathway_governance_queue.csv")
    print(REPORTS / "catalyst_canvas_narrative_pathway_audit.json")
    print(CATALOG_EXPORTS / "catalyst_canvas_narrative_pathway_catalog.csv")


if __name__ == "__main__":
    main()
