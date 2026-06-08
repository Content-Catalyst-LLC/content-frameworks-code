#!/usr/bin/env python3
"""
Educational Scaffolding and Learning-System Audit Engine

Professional-grade, dependency-free workflow for:
"Educational Scaffolding and the Design of Learning Systems."

This script audits:
- learning-path inventory
- prerequisite relationships
- article sequence and learning stages
- concept coverage
- orientation support
- worked-example coverage
- feedback prompts
- transfer support
- cognitive-load risk
- accessibility scaffold indicators
- scaffold-readiness scoring
- governance queues
- catalog exports

Uses only the Python standard library.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from collections import Counter, defaultdict, deque
from datetime import datetime, timezone
from typing import Any, Iterable
import csv
import json

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "educational_scaffolding_config.json"
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


def yes(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"yes", "true", "1", "complete", "ready"}


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


def build_prerequisite_graph(prerequisites: list[dict[str, str]]) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    requires: dict[str, set[str]] = defaultdict(set)
    supports: dict[str, set[str]] = defaultdict(set)

    for row in prerequisites:
        article = row["article_slug"]
        prereq = row["prerequisite_slug"]
        requires[article].add(prereq)
        supports[prereq].add(article)

    return requires, supports


def prerequisite_audit(
    articles: list[dict[str, str]],
    prerequisites: list[dict[str, str]],
    config: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[Finding]]:
    article_by_slug = {row["slug"]: row for row in articles}
    requires, supports = build_prerequisite_graph(prerequisites)
    threshold = float(config["thresholds"]["prerequisite_readiness_minimum"])
    findings: list[Finding] = []
    rows: list[dict[str, Any]] = []

    for article in articles:
        slug = article["slug"]
        required = requires.get(slug, set())
        available = [prereq for prereq in required if prereq in article_by_slug]
        published_available = [
            prereq for prereq in available
            if article_by_slug[prereq]["status"] == "published"
        ]

        readiness = len(published_available) / len(required) if required else 1.0

        rows.append(
            {
                "slug": slug,
                "title": article["title"],
                "learning_stage": article["learning_stage"],
                "status": article["status"],
                "required_prerequisites": len(required),
                "known_prerequisites": len(available),
                "published_prerequisites": len(published_available),
                "prerequisite_readiness": round(readiness, 4),
                "supports_downstream_articles": len(supports.get(slug, set())),
                "prerequisite_status": "ready" if readiness >= threshold else "needs prerequisite support",
            }
        )

        if article["status"] == "published" and readiness < threshold:
            findings.append(
                Finding(
                    "medium",
                    "prerequisites",
                    slug,
                    f"Prerequisite readiness is {readiness:.0%}.",
                    "Add, publish, or link prerequisite articles before promoting advanced learning content.",
                )
            )

    return rows, findings


def sequence_audit(articles: list[dict[str, str]], config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[Finding]]:
    ordered = sorted(articles, key=lambda row: int(row["article_order"]))
    stage_order = {
        "orientation": 1,
        "foundation": 2,
        "method": 3,
        "guided_practice": 4,
        "application": 5,
        "critique": 6,
        "transfer": 7,
    }

    valid_stages = set(config["valid_learning_stages"])
    findings: list[Finding] = []
    rows: list[dict[str, Any]] = []
    previous_stage_rank = 0

    for article in ordered:
        stage = article["learning_stage"]
        rank = stage_order.get(stage, 99)
        invalid_stage = stage not in valid_stages
        regression = rank < previous_stage_rank and article["status"] == "published"

        rows.append(
            {
                "article_order": article["article_order"],
                "slug": article["slug"],
                "title": article["title"],
                "learning_stage": stage,
                "stage_rank": rank,
                "stage_valid": not invalid_stage,
                "sequence_regression": regression,
            }
        )

        if invalid_stage:
            findings.append(
                Finding(
                    "high",
                    "learning_stage",
                    article["slug"],
                    f"Invalid learning stage: {stage}",
                    "Map the article to the approved learning-stage vocabulary.",
                )
            )

        if regression:
            findings.append(
                Finding(
                    "low",
                    "sequence",
                    article["slug"],
                    "Learning stage appears earlier than the preceding published stage.",
                    "Review whether article-map order supports the intended learning pathway.",
                )
            )

        previous_stage_rank = max(previous_stage_rank, rank)

    return rows, findings


def scaffold_features_audit(
    articles: list[dict[str, str]],
    config: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[Finding]]:
    findings: list[Finding] = []
    rows: list[dict[str, Any]] = []
    penalties = config["cognitive_load_penalties"]
    accessibility_threshold = float(config["thresholds"]["accessibility_readiness_minimum"])

    for article in articles:
        orientation = 1.0 if yes(article["orientation_support"]) else 0.0
        examples = 1.0 if yes(article["worked_examples"]) else 0.0
        feedback = 1.0 if yes(article["feedback_prompts"]) else 0.0
        transfer = 1.0 if yes(article["transfer_support"]) else 0.0
        accessibility = (
            int(yes(article["alt_text"]))
            + int(yes(article["clear_headings"]))
            + int(yes(article["descriptive_links"]))
            + int(yes(article["summary_support"]))
        ) / 4

        cognitive_load_risk = article["cognitive_load_risk"].lower()
        load_penalty = float(penalties.get(cognitive_load_risk, 0.10))

        rows.append(
            {
                "slug": article["slug"],
                "title": article["title"],
                "learning_stage": article["learning_stage"],
                "orientation_score": orientation,
                "example_score": examples,
                "feedback_score": feedback,
                "transfer_score": transfer,
                "accessibility_score": round(accessibility, 4),
                "cognitive_load_risk": cognitive_load_risk,
                "load_penalty": load_penalty,
            }
        )

        if article["status"] == "published" and cognitive_load_risk == "high":
            findings.append(
                Finding(
                    "medium",
                    "cognitive_load",
                    article["slug"],
                    "Published article has high cognitive-load risk.",
                    "Add summaries, examples, prerequisite links, tables, staged explanation, or stronger orientation support.",
                )
            )

        if article["status"] == "published" and accessibility < accessibility_threshold:
            findings.append(
                Finding(
                    "medium",
                    "accessibility",
                    article["slug"],
                    f"Accessibility scaffold score is {accessibility:.0%}.",
                    "Review alt text, heading structure, descriptive links, and summary support.",
                )
            )

    return rows, findings


def scaffold_readiness(
    articles: list[dict[str, str]],
    prerequisite_rows: list[dict[str, Any]],
    feature_rows: list[dict[str, Any]],
    config: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[Finding]]:
    prereq_by_slug = {row["slug"]: row for row in prerequisite_rows}
    feature_by_slug = {row["slug"]: row for row in feature_rows}
    weights = config["scaffold_weights"]
    threshold = float(config["thresholds"]["scaffold_readiness_minimum"])
    findings: list[Finding] = []
    rows: list[dict[str, Any]] = []

    for article in articles:
        slug = article["slug"]
        prereq_score = float(prereq_by_slug[slug]["prerequisite_readiness"])
        features = feature_by_slug[slug]

        score = (
            weights["orientation"] * float(features["orientation_score"])
            + weights["prerequisites"] * prereq_score
            + weights["examples"] * float(features["example_score"])
            + weights["feedback"] * float(features["feedback_score"])
            + weights["transfer"] * float(features["transfer_score"])
            + weights["accessibility"] * float(features["accessibility_score"])
            - float(features["load_penalty"])
        )

        score = max(0.0, min(1.0, score))
        status = "ready" if score >= threshold else "governance review"

        rows.append(
            {
                "slug": slug,
                "title": article["title"],
                "status": article["status"],
                "concept_cluster": article["concept_cluster"],
                "learning_stage": article["learning_stage"],
                "orientation_score": features["orientation_score"],
                "prerequisite_score": round(prereq_score, 4),
                "example_score": features["example_score"],
                "feedback_score": features["feedback_score"],
                "transfer_score": features["transfer_score"],
                "accessibility_score": features["accessibility_score"],
                "load_penalty": features["load_penalty"],
                "scaffold_readiness_score": round(score, 4),
                "scaffold_status": status,
            }
        )

        if article["status"] == "published" and score < threshold:
            findings.append(
                Finding(
                    "medium",
                    "scaffold_readiness",
                    slug,
                    f"Scaffold-readiness score is {score:.2f}, below threshold {threshold:.2f}.",
                    "Review orientation, prerequisites, examples, feedback, transfer support, accessibility, and cognitive-load risk.",
                )
            )

    return rows, findings


def learning_path_depth(
    articles: list[dict[str, str]],
    prerequisites: list[dict[str, str]],
) -> list[dict[str, Any]]:
    article_by_slug = {row["slug"]: row for row in articles}
    _, supports = build_prerequisite_graph(prerequisites)

    roots = [
        row["slug"]
        for row in articles
        if row["learning_stage"] in {"orientation", "foundation"}
    ]

    distance: dict[str, int | None] = {slug: None for slug in article_by_slug}
    queue: deque[tuple[str, int]] = deque()

    for root in roots:
        distance[root] = 0
        queue.append((root, 0))

    while queue:
        current, depth = queue.popleft()
        for target in supports.get(current, set()):
            if target in distance and distance[target] is None:
                distance[target] = depth + 1
                queue.append((target, depth + 1))

    rows: list[dict[str, Any]] = []
    for slug, article in article_by_slug.items():
        rows.append(
            {
                "slug": slug,
                "title": article["title"],
                "learning_stage": article["learning_stage"],
                "path_depth_from_foundation": distance[slug] if distance[slug] is not None else "unreachable",
                "reachable_from_foundation": distance[slug] is not None,
            }
        )

    return sorted(rows, key=lambda row: (str(row["path_depth_from_foundation"]), row["slug"]))


def concept_coverage(
    articles: list[dict[str, str]],
    config: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[Finding]]:
    grouped: dict[str, Counter[str]] = defaultdict(Counter)
    threshold = float(config["thresholds"]["concept_coverage_minimum"])
    findings: list[Finding] = []

    for article in articles:
        grouped[article["concept_cluster"]][article["status"]] += 1

    rows: list[dict[str, Any]] = []
    for cluster in sorted(grouped):
        total = sum(grouped[cluster].values())
        published = grouped[cluster]["published"]
        planned = grouped[cluster]["planned"]
        coverage = published / total if total else 0.0

        rows.append(
            {
                "concept_cluster": cluster,
                "published": published,
                "planned": planned,
                "total": total,
                "published_coverage_rate": round(coverage, 4),
                "coverage_status": "healthy" if coverage >= threshold else "needs development",
            }
        )

        if coverage < threshold:
            findings.append(
                Finding(
                    "medium",
                    "concept_coverage",
                    cluster,
                    f"Published coverage rate is {coverage:.0%}.",
                    "Prioritize planned learning-path articles in this concept cluster.",
                )
            )

    return rows, findings


def relationship_type_summary(prerequisites: list[dict[str, str]]) -> list[dict[str, Any]]:
    counts = Counter(row["relationship_type"] for row in prerequisites)
    importance = Counter(row["importance"] for row in prerequisites)

    rows: list[dict[str, Any]] = []
    for relationship_type, count in sorted(counts.items()):
        rows.append(
            {
                "relationship_type": relationship_type,
                "relationship_count": count,
            }
        )

    for level, count in sorted(importance.items()):
        rows.append(
            {
                "relationship_type": f"importance:{level}",
                "relationship_count": count,
            }
        )

    return rows


def governance_queue(manual_queue: list[dict[str, str]], findings: list[Finding]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for item in manual_queue:
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
                "source": "automated_scaffold_audit",
                "severity": finding.severity,
                "category": finding.category,
                "identifier": finding.identifier,
                "message": finding.message,
                "recommended_action": finding.recommended_action,
            }
        )

    rows.sort(key=lambda row: (severity_rank(row["severity"]), row["category"], row["identifier"]))
    return rows


def catalog_export(readiness_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "series": "Content Frameworks",
            "slug": row["slug"],
            "title": row["title"],
            "status": row["status"],
            "concept_cluster": row["concept_cluster"],
            "learning_stage": row["learning_stage"],
            "scaffold_readiness_score": row["scaffold_readiness_score"],
            "scaffold_status": row["scaffold_status"],
            "github_path": f"articles/{row['slug']}/",
        }
        for row in readiness_rows
    ]


def markdown_summary(report: dict[str, Any]) -> str:
    lines = [
        "# Educational Scaffolding and Learning-System Audit",
        "",
        f"Generated: {report['generated_at']}",
        "",
        "## Counts",
        "",
        f"- Learning-path records: {report['counts']['articles']}",
        f"- Prerequisite relationships: {report['counts']['prerequisite_relationships']}",
        f"- Findings: {report['counts']['findings']}",
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
    lines.append("This report uses synthetic data and demonstrates educational scaffolding and learning-system diagnostics.")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    ensure_dirs()
    config = read_json(CONFIG_PATH)
    articles = read_csv(DATA / "learning_path_inventory.csv")
    prerequisites = read_csv(DATA / "prerequisite_relationships.csv")
    feature_catalog = read_csv(DATA / "scaffold_feature_catalog.csv")
    manual_queue = read_csv(DATA / "editorial_review_queue.csv")

    findings: list[Finding] = []
    findings.extend(
        validate_columns(
            articles,
            ["article_order", "slug", "title", "status", "concept_cluster", "learning_stage"],
            "learning_path_inventory",
        )
    )
    findings.extend(
        validate_columns(
            prerequisites,
            ["article_slug", "prerequisite_slug", "relationship_type", "importance"],
            "prerequisite_relationships",
        )
    )

    prerequisite_rows, prerequisite_findings = prerequisite_audit(articles, prerequisites, config)
    sequence_rows, sequence_findings = sequence_audit(articles, config)
    feature_rows, feature_findings = scaffold_features_audit(articles, config)
    readiness_rows, readiness_findings = scaffold_readiness(articles, prerequisite_rows, feature_rows, config)
    depth_rows = learning_path_depth(articles, prerequisites)
    coverage_rows, coverage_findings = concept_coverage(articles, config)
    relationship_rows = relationship_type_summary(prerequisites)

    findings.extend(prerequisite_findings)
    findings.extend(sequence_findings)
    findings.extend(feature_findings)
    findings.extend(readiness_findings)
    findings.extend(coverage_findings)

    queue_rows = governance_queue(manual_queue, findings)
    catalog_rows = catalog_export(readiness_rows)

    write_csv(TABLES / "prerequisite_readiness_report.csv", prerequisite_rows)
    write_csv(TABLES / "learning_sequence_report.csv", sequence_rows)
    write_csv(TABLES / "scaffold_feature_report.csv", feature_rows)
    write_csv(TABLES / "scaffold_readiness_report.csv", readiness_rows)
    write_csv(TABLES / "learning_path_depth_report.csv", depth_rows)
    write_csv(TABLES / "concept_coverage_report.csv", coverage_rows)
    write_csv(TABLES / "relationship_type_summary.csv", relationship_rows)
    write_csv(TABLES / "scaffold_feature_catalog.csv", feature_catalog)
    write_csv(TABLES / "learning_system_governance_queue.csv", queue_rows)
    write_csv(CATALOG_EXPORTS / "educational_scaffolding_catalog_export.csv", catalog_rows)

    report = {
        "article": "Educational Scaffolding and the Design of Learning Systems",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "articles": len(articles),
            "prerequisite_relationships": len(prerequisites),
            "scaffold_features": len(feature_catalog),
            "findings": len(findings),
            "governance_queue": len(queue_rows),
        },
        "prerequisite_readiness": prerequisite_rows,
        "sequence": sequence_rows,
        "scaffold_features": feature_rows,
        "scaffold_readiness": readiness_rows,
        "learning_path_depth": depth_rows,
        "concept_coverage": coverage_rows,
        "relationship_type_summary": relationship_rows,
        "governance_queue": queue_rows,
        "catalog_export_preview": catalog_rows[:5],
    }

    write_json(REPORTS / "educational_scaffolding_audit.json", report)
    write_json(AUDIT_LOGS / "scaffolding_audit_findings.json", [asdict(finding) for finding in findings])
    (REPORTS / "educational_scaffolding_audit.md").write_text(markdown_summary(report), encoding="utf-8")

    print("Educational scaffolding audit complete.")
    print(TABLES / "scaffold_readiness_report.csv")
    print(TABLES / "learning_path_depth_report.csv")
    print(TABLES / "learning_system_governance_queue.csv")
    print(REPORTS / "educational_scaffolding_audit.json")
    print(CATALOG_EXPORTS / "educational_scaffolding_catalog_export.csv")


if __name__ == "__main__":
    main()
