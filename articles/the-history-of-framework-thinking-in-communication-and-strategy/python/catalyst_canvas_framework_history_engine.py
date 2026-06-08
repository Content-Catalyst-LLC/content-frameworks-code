#!/usr/bin/env python3
"""
Catalyst Canvas Framework History Engine

Professional-grade, dependency-free audit workflow for:
"The History of Framework Thinking in Communication and Strategy"

This workflow audits:
- historical framework records
- framework lineages and periods
- influence graph diagnostics
- cross-domain transfer risk
- governance readiness
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
CONFIG = ROOT / "config" / "framework_history_config.json"
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


def governance_score(row: dict[str, str], fields: list[str]) -> tuple[float, list[str]]:
    completed = [field for field in fields if yes(row.get(field, ""))]
    missing = [field for field in fields if field not in completed]
    return round(len(completed) / len(fields), 4), missing


def transfer_status(row: dict[str, str], governance: float, config: dict[str, Any]) -> str:
    minimum = float(config["minimum_governance_score"])

    if row["transferred_across_domains"] == "yes" and not yes(row["use_conditions_documented"]):
        return "transfer review required"

    if row["risk_severity"] == "high":
        return "high risk review required"

    if governance < minimum:
        return "governance incomplete"

    if row["risk_severity"] == "medium":
        return "risk review recommended"

    return "managed use"


def history_audit(frameworks: list[dict[str, str]], config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[AuditFinding]]:
    rows: list[dict[str, Any]] = []
    findings: list[AuditFinding] = []
    governance_fields = config["governance_fields"]

    for row in frameworks:
        score, missing = governance_score(row, governance_fields)
        status = transfer_status(row, score, config)

        audit_row = {
            "framework_id": row["framework_id"],
            "framework_name": row["framework_name"],
            "period": row["period"],
            "lineage": row["lineage"],
            "domain": row["domain"],
            "structure_type": row["structure_type"],
            "primary_function": row["primary_function"],
            "transferred_across_domains": row["transferred_across_domains"],
            "governance_score": score,
            "missing_governance_fields": "; ".join(missing) if missing else "none",
            "transfer_status": status,
            "risk_severity": row["risk_severity"],
            "risk_note": row["risk_note"],
        }
        rows.append(audit_row)

        if status != "managed use":
            findings.append(
                AuditFinding(
                    "high" if row["risk_severity"] == "high" else "medium",
                    "framework_history",
                    row["framework_id"],
                    f"{row['framework_name']} requires review: {status}.",
                    "Review lineage, transfer conditions, limitations, evidence, ethics, and governance before reuse."
                )
            )

    rows.sort(key=lambda item: (item["transfer_status"] == "managed use", -severity_rank(item["risk_severity"]), item["framework_name"]))
    return rows, findings


def influence_graph(frameworks: list[dict[str, str]], influences: list[dict[str, str]]) -> tuple[list[dict[str, Any]], list[AuditFinding]]:
    known = {row["framework_id"] for row in frameworks}
    outgoing = Counter(row["source_framework_id"] for row in influences)
    incoming = Counter(row["target_framework_id"] for row in influences)
    findings: list[AuditFinding] = []

    for edge in influences:
        if edge["source_framework_id"] not in known:
            findings.append(AuditFinding("medium", "influence_graph", edge["source_framework_id"], "Influence source is missing from framework records.", "Add source framework record or correct edge."))
        if edge["target_framework_id"] not in known:
            findings.append(AuditFinding("medium", "influence_graph", edge["target_framework_id"], "Influence target is missing from framework records.", "Add target framework record or correct edge."))

    ids = sorted(known | set(outgoing) | set(incoming))
    rows = []

    for framework_id in ids:
        degree = outgoing[framework_id] + incoming[framework_id]
        role = "bridge" if degree >= 4 else "source" if outgoing[framework_id] > incoming[framework_id] else "receiver" if incoming[framework_id] else "isolated"
        rows.append(
            {
                "framework_id": framework_id,
                "incoming_influences": incoming[framework_id],
                "outgoing_influences": outgoing[framework_id],
                "influence_degree": degree,
                "lineage_role": role,
            }
        )

    return rows, findings


def metadata_audit(metadata: list[dict[str, str]]) -> tuple[list[dict[str, Any]], list[AuditFinding]]:
    fields = ["excerpt", "tags", "github_url", "image_alt", "references", "last_reviewed", "series_context", "footer_navigation"]
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


def review_case_audit(cases: list[dict[str, str]]) -> list[dict[str, Any]]:
    return [
        {
            "case_id": row["case_id"],
            "framework_id": row["framework_id"],
            "reuse_context": row["reuse_context"],
            "historical_question": row["historical_question"],
            "decision": row["decision"],
            "requires_review": "review" in row["decision"],
        }
        for row in cases
    ]


def governance_queue(findings: list[AuditFinding], history_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
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

    for row in history_rows:
        if row["transfer_status"] != "managed use":
            rows.append(
                {
                    "source": "framework_history",
                    "severity": "high" if row["risk_severity"] == "high" else "medium",
                    "category": "historical_lineage_review",
                    "identifier": row["framework_id"],
                    "message": f"{row['framework_name']} status: {row['transfer_status']}.",
                    "recommended_action": "Review lineage, transfer context, limitations, and governance before reuse."
                }
            )

    rows.sort(key=lambda item: (severity_rank(item["severity"]), item["category"], item["identifier"]))
    return rows


def catalog_export(article_map: list[dict[str, str]], metadata_rows: list[dict[str, Any]], history_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    metadata_by_slug = {row["slug"]: row for row in metadata_rows}
    history_review_count = sum(1 for row in history_rows if row["transfer_status"] != "managed use")

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
                "history_review_items": history_review_count if row["slug"] == "the-history-of-framework-thinking-in-communication-and-strategy" else 0,
                "github_path": f"articles/{row['slug']}/",
            }
        )

    return rows


def markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Catalyst Canvas Framework History Audit",
        "",
        f"Article: {report['article']}",
        f"Generated: {report['generated_at']}",
        "",
        "## Key Counts",
        "",
        f"- Framework records: {report['counts']['frameworks']}",
        f"- Influence edges: {report['counts']['influence_edges']}",
        f"- Governance queue items: {report['counts']['governance_queue']}",
        "",
        "## Frameworks Requiring Review",
        "",
    ]

    review_items = [row for row in report["historical_frameworks"] if row["transfer_status"] != "managed use"]

    if not review_items:
        lines.append("- No frameworks require review.")
    else:
        for row in review_items:
            lines.append(f"- `{row['framework_id']}` **{row['framework_name']}** — {row['transfer_status']}")

    return "\n".join(lines) + "\n"


def main() -> None:
    ensure_dirs()

    config = read_json(CONFIG)
    frameworks = read_csv(DATA / "historical_framework_records.csv")
    influences = read_csv(DATA / "framework_influence_edges.csv")
    article_map = read_csv(DATA / "content_framework_article_map.csv")
    metadata = read_csv(DATA / "metadata_inventory.csv")
    links = read_csv(DATA / "internal_links.csv")
    taxonomy = read_csv(DATA / "taxonomy_categories.csv")
    cases = read_csv(DATA / "framework_history_review_cases.csv")

    findings: list[AuditFinding] = []
    findings.extend(validate_columns(frameworks, ["framework_id", "framework_name", "period", "lineage"], "historical_framework_records"))
    findings.extend(validate_columns(influences, ["source_framework_id", "target_framework_id", "influence_type"], "framework_influence_edges"))
    findings.extend(validate_columns(article_map, ["article_order", "title", "status", "cluster", "slug"], "content_framework_article_map"))
    findings.extend(validate_columns(metadata, ["slug", "title", "status"], "metadata_inventory"))

    history_rows, history_findings = history_audit(frameworks, config)
    graph_rows, graph_findings = influence_graph(frameworks, influences)
    metadata_rows, metadata_findings = metadata_audit(metadata)
    coverage_rows = article_map_coverage(article_map)
    link_rows, link_findings = link_diagnostics(article_map, links)
    taxonomy_rows = taxonomy_coverage(article_map, taxonomy)
    case_rows = review_case_audit(cases)

    findings.extend(history_findings)
    findings.extend(graph_findings)
    findings.extend(metadata_findings)
    findings.extend(link_findings)

    governance_rows = governance_queue(findings, history_rows)
    catalog_rows = catalog_export(article_map, metadata_rows, history_rows)

    write_csv(TABLES / "historical_framework_audit.csv", history_rows)
    write_csv(TABLES / "framework_influence_graph_diagnostics.csv", graph_rows)
    write_csv(TABLES / "metadata_history_readiness.csv", metadata_rows)
    write_csv(TABLES / "article_map_coverage_summary.csv", coverage_rows)
    write_csv(TABLES / "internal_link_history_diagnostics.csv", link_rows)
    write_csv(TABLES / "taxonomy_history_coverage.csv", taxonomy_rows)
    write_csv(TABLES / "framework_history_review_cases.csv", case_rows)
    write_csv(TABLES / "framework_history_governance_queue.csv", governance_rows)
    write_csv(CATALOG_EXPORTS / "catalyst_canvas_framework_history_catalog.csv", catalog_rows)

    generated_at = datetime.now(timezone.utc).isoformat()
    lineage_summary = Counter(row["lineage"] for row in frameworks)
    period_summary = Counter(row["period"] for row in frameworks)
    domain_summary = Counter(row["domain"] for row in frameworks)

    report = {
        "article": "The History of Framework Thinking in Communication and Strategy",
        "generated_at": generated_at,
        "config": config,
        "counts": {
            "frameworks": len(frameworks),
            "influence_edges": len(influences),
            "articles": len(article_map),
            "links": len(links),
            "governance_queue": len(governance_rows),
        },
        "summary": {
            "lineage_counts": dict(lineage_summary),
            "period_counts": dict(period_summary),
            "domain_counts": dict(domain_summary),
        },
        "historical_frameworks": history_rows,
        "influence_graph": graph_rows,
        "metadata_readiness": metadata_rows,
        "coverage": coverage_rows,
        "link_diagnostics": link_rows,
        "taxonomy_coverage": taxonomy_rows,
        "review_cases": case_rows,
        "governance_queue": governance_rows,
    }

    write_json(REPORTS / "catalyst_canvas_framework_history_audit.json", report)
    write_json(AUDIT_LOGS / "audit_findings.json", [asdict(finding) for finding in findings])
    (REPORTS / "catalyst_canvas_framework_history_audit.md").write_text(markdown_report(report), encoding="utf-8")

    print("Catalyst Canvas framework history audit complete.")
    print(TABLES / "historical_framework_audit.csv")
    print(TABLES / "framework_influence_graph_diagnostics.csv")
    print(TABLES / "framework_history_governance_queue.csv")
    print(REPORTS / "catalyst_canvas_framework_history_audit.json")


if __name__ == "__main__":
    main()
