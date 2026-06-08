#!/usr/bin/env python3
from pathlib import Path
import csv
import json
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
TABLES = ROOT / "outputs" / "tables"
REPORTS = ROOT / "outputs" / "reports"

def read_csv(name):
    with (DATA / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

def main():
    article_map = read_csv("content_framework_article_map.csv")
    metadata = read_csv("metadata_inventory.csv")
    frameworks = read_csv("framework_library.csv")

    grouped = defaultdict(Counter)
    for row in article_map:
        grouped[row["cluster"]][row["status"]] += 1

    coverage = []
    for cluster in sorted(grouped):
        published = grouped[cluster]["published"]
        planned = grouped[cluster]["planned"]
        total = published + planned
        coverage.append({
            "cluster": cluster,
            "published": published,
            "planned": planned,
            "total": total,
            "coverage_rate": round(published / total, 4) if total else 0
        })

    fields = ["excerpt", "tags", "github_url", "image_alt", "references", "last_reviewed"]
    metadata_report = []
    for row in metadata:
        complete = sum(1 for field in fields if row[field] == "yes")
        metadata_report.append({
            "slug": row["slug"],
            "title": row["title"],
            "status": row["status"],
            "complete_fields": complete,
            "required_fields": len(fields),
            "completion_rate": round(complete / len(fields), 4)
        })

    framework_domains = Counter(row["domain"] for row in frameworks)
    domain_report = [{"domain": domain, "framework_count": count} for domain, count in sorted(framework_domains.items())]

    write_csv(TABLES / "article_map_coverage_summary.csv", coverage)
    write_csv(TABLES / "metadata_completeness_report.csv", metadata_report)
    write_csv(TABLES / "framework_domain_summary.csv", domain_report)

    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "content_frameworks_audit_report.json").write_text(
        json.dumps({
            "article": "What Are Content Frameworks?",
            "coverage_summary": coverage,
            "metadata_summary": metadata_report,
            "framework_domain_summary": domain_report
        }, indent=2),
        encoding="utf-8"
    )

    print("Content-framework audit complete.")

if __name__ == "__main__":
    main()
