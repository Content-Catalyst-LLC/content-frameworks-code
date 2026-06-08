#!/usr/bin/env python3
"""
Editorial Metadata and Content-System Audit Engine

Professional-grade, dependency-free workflow for:
"Editorial Metadata and Content Systems."

This script audits:
- required metadata fields
- controlled vocabulary values
- slug, URL, and repository-path consistency
- article-map sequence and footer navigation
- image metadata readiness
- accessibility metadata readiness
- reference metadata readiness
- repository manifest readiness
- review-cycle status
- relationship completeness
- governance review queues
- catalog exports

Uses only the Python standard library.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import date, datetime, timezone
from collections import Counter, defaultdict
from typing import Any, Iterable
import csv
import json

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "editorial_metadata_config.json"
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


def completed(value: str | None) -> bool:
    if value is None:
        return False
    normalized = str(value).strip().lower()
    return normalized not in {"", "no", "false", "0", "none", "null", "pending"}


def parse_iso_date(value: str) -> date | None:
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


def metadata_completeness(records: list[dict[str, str]], config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[Finding]]:
    required = config["required_metadata_fields"]
    threshold = float(config["thresholds"]["metadata_completion_minimum"])
    rows: list[dict[str, Any]] = []
    findings: list[Finding] = []

    for record in records:
        missing = [field for field in required if not completed(record.get(field, ""))]
        completion_rate = (len(required) - len(missing)) / len(required) if required else 1.0

        rows.append(
            {
                "slug": record["slug"],
                "title": record["title"],
                "status": record["status"],
                "cluster": record["cluster"],
                "article_type": record["article_type"],
                "completed_fields": len(required) - len(missing),
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
                    "Complete missing metadata fields before next governance review.",
                )
            )

    return rows, findings


def controlled_vocabulary_check(records: list[dict[str, str]], config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[Finding]]:
    valid_status = set(config["controlled_status_values"])
    valid_types = set(config["controlled_article_types"])
    valid_clusters = set(config["controlled_clusters"])
    rows: list[dict[str, Any]] = []
    findings: list[Finding] = []

    for record in records:
        status_ok = record["status"] in valid_status
        type_ok = record["article_type"] in valid_types
        cluster_ok = record["cluster"] in valid_clusters

        rows.append(
            {
                "slug": record["slug"],
                "status": record["status"],
                "status_valid": status_ok,
                "article_type": record["article_type"],
                "article_type_valid": type_ok,
                "cluster": record["cluster"],
                "cluster_valid": cluster_ok,
            }
        )

        if not status_ok:
            findings.append(
                Finding(
                    "high",
                    "controlled_vocabulary",
                    record["slug"],
                    f"Invalid status value: {record['status']}",
                    "Map status to the controlled editorial lifecycle vocabulary.",
                )
            )
        if not type_ok:
            findings.append(
                Finding(
                    "medium",
                    "controlled_vocabulary",
                    record["slug"],
                    f"Invalid article type: {record['article_type']}",
                    "Map article type to the controlled content-system vocabulary.",
                )
            )
        if not cluster_ok:
            findings.append(
                Finding(
                    "medium",
                    "controlled_vocabulary",
                    record["slug"],
                    f"Invalid cluster value: {record['cluster']}",
                    "Map cluster to the Content Frameworks taxonomy.",
                )
            )

    return rows, findings


def repository_alignment(records: list[dict[str, str]]) -> tuple[list[dict[str, Any]], list[Finding]]:
    rows: list[dict[str, Any]] = []
    findings: list[Finding] = []

    for record in records:
        slug = record["slug"]
        expected_path = f"articles/{slug}/"
        repo_path = record.get("repository_path", "")
        aligned = repo_path == expected_path

        rows.append(
            {
                "slug": slug,
                "repository_url": record.get("repository_url", ""),
                "repository_path": repo_path,
                "expected_repository_path": expected_path,
                "repository_path_aligned": aligned,
            }
        )

        if record["status"] == "published" and not aligned:
            findings.append(
                Finding(
                    "medium",
                    "repository_alignment",
                    slug,
                    "Repository path does not match expected article slug path.",
                    "Update repository metadata or correct folder structure.",
                )
            )

    return rows, findings


def footer_navigation_check(records: list[dict[str, str]], config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[Finding]]:
    ordered = sorted(records, key=lambda row: int(row["article_order"]))
    rows: list[dict[str, Any]] = []
    findings: list[Finding] = []
    required_map_url = config["article_map_url"]

    for index, record in enumerate(ordered):
        previous_record = ordered[index - 1] if index > 0 else None
        next_record = ordered[index + 1] if index < len(ordered) - 1 else None

        expected_previous_title = previous_record["title"] if previous_record else "Series Start"
        expected_previous_url = f"/{previous_record['slug']}/" if previous_record else ""
        expected_next_title = next_record["title"] if next_record else "Series End"
        expected_next_url = f"/{next_record['slug']}/" if next_record else ""

        previous_title_ok = record["previous_title"] == expected_previous_title
        previous_url_ok = record["previous_url"] == expected_previous_url
        next_title_ok = record["next_title"] == expected_next_title
        next_url_ok = record["next_url"] == expected_next_url
        map_ok = record["article_map_url"] == required_map_url

        rows.append(
            {
                "slug": record["slug"],
                "previous_title": record["previous_title"],
                "expected_previous_title": expected_previous_title,
                "previous_title_valid": previous_title_ok,
                "previous_url": record["previous_url"],
                "expected_previous_url": expected_previous_url,
                "previous_url_valid": previous_url_ok,
                "next_title": record["next_title"],
                "expected_next_title": expected_next_title,
                "next_title_valid": next_title_ok,
                "next_url": record["next_url"],
                "expected_next_url": expected_next_url,
                "next_url_valid": next_url_ok,
                "article_map_url": record["article_map_url"],
                "article_map_valid": map_ok,
            }
        )

        if record["status"] == "published" and not all([previous_title_ok, previous_url_ok, next_title_ok, next_url_ok, map_ok]):
            findings.append(
                Finding(
                    "medium",
                    "footer_navigation",
                    record["slug"],
                    "Footer navigation metadata does not fully match article-map sequence.",
                    "Update previous, next, and article-map metadata from the article map.",
                )
            )

    return rows, findings


def image_metadata_check(records: list[dict[str, str]], image_records: list[dict[str, str]], config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[Finding]]:
    image_by_slug = {row["slug"]: row for row in image_records}
    threshold = float(config["thresholds"]["image_metadata_minimum"])
    image_fields = ["image_title", "image_filename", "alt_text", "caption", "image_description"]
    rows: list[dict[str, Any]] = []
    findings: list[Finding] = []

    for record in records:
        slug = record["slug"]
        image = image_by_slug.get(slug, {})
        complete_count = sum(1 for field in image_fields if completed(image.get(field, record.get(field, ""))))
        score = complete_count / len(image_fields)
        status = image.get("review_status", "missing image record")

        rows.append(
            {
                "slug": slug,
                "title": record["title"],
                "image_record_present": bool(image),
                "completed_image_fields": complete_count,
                "required_image_fields": len(image_fields),
                "image_metadata_score": round(score, 4),
                "image_review_status": status,
                "image_metadata_status": "ready" if score >= threshold and status == "ready" else "needs image metadata review",
            }
        )

        if record["status"] == "published" and (score < threshold or status != "ready"):
            findings.append(
                Finding(
                    "medium",
                    "image_metadata",
                    slug,
                    f"Image metadata score is {score:.0%}; review status is {status}.",
                    "Complete image title, filename, alt text, caption, description, and review status.",
                )
            )

    return rows, findings


def reference_metadata_check(records: list[dict[str, str]], reference_records: list[dict[str, str]]) -> tuple[list[dict[str, Any]], list[Finding]]:
    count_by_slug = Counter(row["slug"] for row in reference_records)
    high_authority_by_slug = Counter(row["slug"] for row in reference_records if row["authority_level"] == "high")
    ready_by_slug = Counter(row["slug"] for row in reference_records if row["review_status"] == "ready")
    findings: list[Finding] = []
    rows: list[dict[str, Any]] = []

    for record in records:
        slug = record["slug"]
        source_count = count_by_slug[slug]
        high_authority = high_authority_by_slug[slug]
        ready = ready_by_slug[slug]
        readiness = min(source_count / 3, 1.0) * 0.35 + min(high_authority / 2, 1.0) * 0.35 + (ready / max(source_count, 1) if source_count else 0.0) * 0.30

        rows.append(
            {
                "slug": slug,
                "title": record["title"],
                "reference_records": source_count,
                "high_authority_sources": high_authority,
                "ready_reference_records": ready,
                "reference_readiness_score": round(readiness, 4),
                "reference_status": "ready" if readiness >= 0.67 else "needs reference metadata review",
            }
        )

        if record["status"] == "published" and completed(record.get("references", "")) and readiness < 0.67:
            findings.append(
                Finding(
                    "medium",
                    "reference_metadata",
                    slug,
                    f"Reference metadata readiness score is {readiness:.2f}.",
                    "Review source records, authority level, and claim support.",
                )
            )

    return rows, findings


def repository_manifest_check(records: list[dict[str, str]], repository_manifest: list[dict[str, str]]) -> tuple[list[dict[str, Any]], list[Finding]]:
    manifest_by_slug = {row["slug"]: row for row in repository_manifest}
    fields = ["required_folders_present", "readme_present", "python_workflow_present", "r_workflow_present", "sql_schema_present", "outputs_present"]
    rows: list[dict[str, Any]] = []
    findings: list[Finding] = []

    for record in records:
        slug = record["slug"]
        manifest = manifest_by_slug.get(slug, {})
        complete_count = sum(1 for field in fields if completed(manifest.get(field, "")))
        score = complete_count / len(fields)
        status = manifest.get("manifest_status", "missing manifest")

        rows.append(
            {
                "slug": slug,
                "manifest_present": bool(manifest),
                "repository_manifest_score": round(score, 4),
                "manifest_status": status,
                "repository_workflow_ready": score >= 0.8 and status == "ready",
            }
        )

        if record["status"] == "published" and not (score >= 0.8 and status == "ready"):
            findings.append(
                Finding(
                    "medium",
                    "repository_manifest",
                    slug,
                    f"Repository manifest score is {score:.0%}; status is {status}.",
                    "Review companion repository structure, README, workflows, SQL, and outputs.",
                )
            )

    return rows, findings


def review_cycle_check(records: list[dict[str, str]], config: dict[str, Any], today: date) -> tuple[list[dict[str, Any]], list[Finding]]:
    cycles = config["review_cycles_by_article_type"]
    rows: list[dict[str, Any]] = []
    findings: list[Finding] = []

    for record in records:
        cycle = int(cycles.get(record["article_type"], 365))
        reviewed = parse_iso_date(record.get("last_reviewed", ""))

        if reviewed is None:
            age = "unknown"
            score = 0.0
            freshness = "missing review date"
        else:
            age_days = (today - reviewed).days
            age = age_days
            score = max(0.0, min(1.0, 1 - age_days / max(cycle, 1)))
            freshness = "fresh" if age_days <= cycle else "review overdue"

        rows.append(
            {
                "slug": record["slug"],
                "article_type": record["article_type"],
                "status": record["status"],
                "last_reviewed": record.get("last_reviewed", ""),
                "review_cycle_days": cycle,
                "content_age_days": age,
                "freshness_score": round(score, 4),
                "freshness_status": freshness,
            }
        )

        if record["status"] == "published" and freshness != "fresh":
            findings.append(
                Finding(
                    "medium",
                    "freshness",
                    record["slug"],
                    f"Freshness status is {freshness}.",
                    "Review article and update last-reviewed metadata.",
                )
            )

    return rows, findings


def relationship_completeness(records: list[dict[str, str]], config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[Finding]]:
    relationship_fields = ["previous_title", "previous_url", "article_map_title", "article_map_url", "next_title", "next_url", "repository_url"]
    threshold = float(config["thresholds"]["relationship_completeness_minimum"])
    rows: list[dict[str, Any]] = []
    findings: list[Finding] = []

    for record in records:
        complete_count = sum(1 for field in relationship_fields if completed(record.get(field, "")) or (field in {"previous_url", "next_url"} and record.get(field, "") == ""))
        score = complete_count / len(relationship_fields)

        rows.append(
            {
                "slug": record["slug"],
                "completed_relationship_fields": complete_count,
                "required_relationship_fields": len(relationship_fields),
                "relationship_completeness_score": round(score, 4),
                "relationship_status": "ready" if score >= threshold else "needs relationship review",
            }
        )

        if record["status"] == "published" and score < threshold:
            findings.append(
                Finding(
                    "medium",
                    "relationship_metadata",
                    record["slug"],
                    f"Relationship completeness score is {score:.0%}.",
                    "Review previous, next, article map, and repository relationship fields.",
                )
            )

    return rows, findings


def cluster_readiness(records: list[dict[str, str]], metadata_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    metadata_by_slug = {row["slug"]: row for row in metadata_rows}
    grouped: dict[str, list[float]] = defaultdict(list)
    status_counts: dict[str, Counter[str]] = defaultdict(Counter)

    for record in records:
        grouped[record["cluster"]].append(float(metadata_by_slug[record["slug"]]["metadata_completion_rate"]))
        status_counts[record["cluster"]][record["status"]] += 1

    rows: list[dict[str, Any]] = []
    for cluster in sorted(grouped):
        scores = grouped[cluster]
        total = sum(status_counts[cluster].values())
        published = status_counts[cluster]["published"]
        rows.append(
            {
                "cluster": cluster,
                "article_count": total,
                "published_count": published,
                "average_metadata_completion_rate": round(sum(scores) / len(scores), 4),
                "published_coverage_rate": round(published / total, 4) if total else 0.0,
                "cluster_metadata_status": "ready" if sum(scores) / len(scores) >= 0.9 else "review",
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


def catalog_export(records: list[dict[str, str]], metadata_rows: list[dict[str, Any]], freshness_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    metadata_by_slug = {row["slug"]: row for row in metadata_rows}
    freshness_by_slug = {row["slug"]: row for row in freshness_rows}

    rows: list[dict[str, Any]] = []
    for record in records:
        slug = record["slug"]
        rows.append(
            {
                "series": record["series"],
                "slug": slug,
                "title": record["title"],
                "cluster": record["cluster"],
                "article_type": record["article_type"],
                "status": record["status"],
                "metadata_completion_rate": metadata_by_slug[slug]["metadata_completion_rate"],
                "metadata_status": metadata_by_slug[slug]["metadata_status"],
                "freshness_status": freshness_by_slug[slug]["freshness_status"],
                "repository_path": record["repository_path"],
                "article_map_url": record["article_map_url"],
                "github_path": f"articles/{slug}/",
            }
        )
    return rows


def markdown_summary(report: dict[str, Any]) -> str:
    lines = [
        "# Editorial Metadata and Content-System Audit",
        "",
        f"Generated: {report['generated_at']}",
        "",
        "## Counts",
        "",
        f"- Metadata records: {report['counts']['metadata_records']}",
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
    lines.append("This report uses synthetic data and demonstrates editorial metadata and content-system governance diagnostics.")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    ensure_dirs()
    config = read_json(CONFIG_PATH)
    records = read_csv(DATA / "editorial_metadata_inventory.csv")
    image_records = read_csv(DATA / "image_metadata_inventory.csv")
    reference_records = read_csv(DATA / "reference_metadata.csv")
    repository_manifest = read_csv(DATA / "repository_manifest.csv")
    manual_queue = read_csv(DATA / "editorial_review_queue.csv")

    findings: list[Finding] = []
    findings.extend(validate_columns(records, ["article_order", "title", "slug", "status", "cluster", "article_type"], "editorial_metadata_inventory"))

    metadata_rows, metadata_findings = metadata_completeness(records, config)
    vocabulary_rows, vocabulary_findings = controlled_vocabulary_check(records, config)
    repository_rows, repository_findings = repository_alignment(records)
    footer_rows, footer_findings = footer_navigation_check(records, config)
    image_rows, image_findings = image_metadata_check(records, image_records, config)
    reference_rows, reference_findings = reference_metadata_check(records, reference_records)
    manifest_rows, manifest_findings = repository_manifest_check(records, repository_manifest)
    freshness_rows, freshness_findings = review_cycle_check(records, config, date.today())
    relationship_rows, relationship_findings = relationship_completeness(records, config)
    cluster_rows = cluster_readiness(records, metadata_rows)

    findings.extend(metadata_findings)
    findings.extend(vocabulary_findings)
    findings.extend(repository_findings)
    findings.extend(footer_findings)
    findings.extend(image_findings)
    findings.extend(reference_findings)
    findings.extend(manifest_findings)
    findings.extend(freshness_findings)
    findings.extend(relationship_findings)

    queue_rows = governance_queue(manual_queue, findings)
    catalog_rows = catalog_export(records, metadata_rows, freshness_rows)

    write_csv(TABLES / "metadata_completeness_report.csv", metadata_rows)
    write_csv(TABLES / "controlled_vocabulary_report.csv", vocabulary_rows)
    write_csv(TABLES / "repository_alignment_report.csv", repository_rows)
    write_csv(TABLES / "footer_navigation_validation.csv", footer_rows)
    write_csv(TABLES / "image_metadata_report.csv", image_rows)
    write_csv(TABLES / "reference_metadata_report.csv", reference_rows)
    write_csv(TABLES / "repository_manifest_report.csv", manifest_rows)
    write_csv(TABLES / "review_cycle_report.csv", freshness_rows)
    write_csv(TABLES / "relationship_completeness_report.csv", relationship_rows)
    write_csv(TABLES / "cluster_metadata_readiness.csv", cluster_rows)
    write_csv(TABLES / "metadata_governance_queue.csv", queue_rows)
    write_csv(CATALOG_EXPORTS / "editorial_metadata_catalog_export.csv", catalog_rows)

    report = {
        "article": "Editorial Metadata and Content Systems",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "metadata_records": len(records),
            "image_records": len(image_records),
            "reference_records": len(reference_records),
            "repository_manifest_records": len(repository_manifest),
            "findings": len(findings),
            "governance_queue": len(queue_rows),
        },
        "metadata_completeness": metadata_rows,
        "footer_navigation": footer_rows,
        "repository_alignment": repository_rows,
        "image_metadata": image_rows,
        "reference_metadata": reference_rows,
        "repository_manifest": manifest_rows,
        "freshness": freshness_rows,
        "cluster_readiness": cluster_rows,
        "governance_queue": queue_rows,
        "catalog_export_preview": catalog_rows[:5],
    }

    write_json(REPORTS / "editorial_metadata_content_system_audit.json", report)
    write_json(AUDIT_LOGS / "metadata_audit_findings.json", [asdict(finding) for finding in findings])
    (REPORTS / "editorial_metadata_content_system_audit.md").write_text(markdown_summary(report), encoding="utf-8")

    print("Editorial metadata content-system audit complete.")
    print(TABLES / "metadata_completeness_report.csv")
    print(TABLES / "footer_navigation_validation.csv")
    print(TABLES / "repository_alignment_report.csv")
    print(TABLES / "metadata_governance_queue.csv")
    print(REPORTS / "editorial_metadata_content_system_audit.json")
    print(CATALOG_EXPORTS / "editorial_metadata_catalog_export.csv")


if __name__ == "__main__":
    main()
