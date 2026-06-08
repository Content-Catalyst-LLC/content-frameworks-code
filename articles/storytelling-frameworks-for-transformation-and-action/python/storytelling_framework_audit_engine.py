#!/usr/bin/env python3
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import defaultdict
from datetime import datetime, timezone
import csv, json, math

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
TABLES = ROOT / "outputs" / "tables"
REPORTS = ROOT / "outputs" / "reports"
AUDIT_LOGS = ROOT / "outputs" / "audit_logs"
CATALOG = ROOT / "outputs" / "catalog_exports"

DIMENSIONS = ["context", "actors", "tension", "sequence", "transformation", "action"]
THRESHOLD = 0.78
EVIDENCE_MINIMUM = 0.70
GOVERNANCE_MINIMUM = 0.70

WEIGHTS = {
    "narrative_completeness": 0.24,
    "evidence_support": 0.22,
    "agency_score": 0.18,
    "transformation_credibility": 0.16,
    "governance_score": 0.12,
    "ethical_review": 0.08
}

@dataclass(frozen=True)
class Finding:
    severity: str
    category: str
    identifier: str
    message: str
    recommended_action: str

def yes(value):
    return str(value).strip().lower() in {"yes", "true", "1", "ready", "complete"}

def read_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))

def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

def average(values):
    return sum(values) / len(values) if values else 0.0

def balance_score(values):
    mean = average(values)
    if mean == 0:
        return 0.0
    variance = average([(value - mean) ** 2 for value in values])
    sd = math.sqrt(variance)
    return max(0.0, min(1.0, 1 - min(sd / mean, 1)))

def score_asset(asset):
    dimension_values = [int(yes(asset[f"{dimension}_present"])) for dimension in DIMENSIONS]
    support_values = [
        int(yes(asset[f"{dimension}_supported"]))
        for dimension in DIMENSIONS
        if yes(asset[f"{dimension}_present"])
    ]

    completeness = sum(dimension_values) / len(DIMENSIONS)
    evidence = average(support_values) if support_values else 0.0
    balance = balance_score(dimension_values)

    agency = (
        int(yes(asset["affected_people_have_agency"])) +
        int(yes(asset["institutional_responsibility_visible"])) +
        int(yes(asset["audience_agency_preserved"]))
    ) / 3

    transformation = (
        int(yes(asset["transformation_bounded"])) +
        int(yes(asset["mechanism_visible"])) +
        int(yes(asset["limitations_present"]))
    ) / 3

    governance = (
        int(yes(asset["review_owner_present"])) +
        int(yes(asset["consent_or_source_context_present"])) +
        int(yes(asset["last_review_date_present"])) +
        int(yes(asset["revision_queue_checked"]))
    ) / 4

    ethics = (
        int(not yes(asset["uses_savior_framing"])) +
        int(not yes(asset["overdramatizes_tension"])) +
        int(not yes(asset["uses_unsupported_anecdote"])) +
        int(not yes(asset["uses_pressure_cta"]))
    ) / 4

    readiness = (
        WEIGHTS["narrative_completeness"] * completeness +
        WEIGHTS["evidence_support"] * evidence +
        WEIGHTS["agency_score"] * agency +
        WEIGHTS["transformation_credibility"] * transformation +
        WEIGHTS["governance_score"] * governance +
        WEIGHTS["ethical_review"] * ethics
    )

    return {
        "narrative_completeness_score": round(completeness, 4),
        "evidence_support_score": round(evidence, 4),
        "narrative_balance_score": round(balance, 4),
        "agency_score": round(agency, 4),
        "transformation_credibility_score": round(transformation, 4),
        "governance_score": round(governance, 4),
        "ethical_review_score": round(ethics, 4),
        "storytelling_readiness_score": round(readiness, 4)
    }

def audit_assets(assets):
    rows, findings = [], []

    for asset in assets:
        scores = score_asset(asset)

        missing = [dimension for dimension in DIMENSIONS if not yes(asset[f"{dimension}_present"])]
        unsupported = [dimension for dimension in DIMENSIONS if yes(asset[f"{dimension}_present"]) and not yes(asset[f"{dimension}_supported"])]

        status = (
            "ready"
            if scores["storytelling_readiness_score"] >= THRESHOLD
            and scores["evidence_support_score"] >= EVIDENCE_MINIMUM
            and scores["governance_score"] >= GOVERNANCE_MINIMUM
            else "governance review"
        )

        row = {
            "asset_id": asset["asset_id"],
            "asset_name": asset["asset_name"],
            "asset_type": asset["asset_type"],
            "story_purpose": asset["story_purpose"],
            "audience": asset["audience"],
            **scores,
            "missing_dimensions": ";".join(missing),
            "unsupported_dimensions": ";".join(unsupported),
            "storytelling_status": status
        }
        rows.append(row)

        if missing:
            findings.append(Finding(
                "medium",
                "narrative_completeness",
                asset["asset_id"],
                f"Missing narrative dimensions: {', '.join(missing)}.",
                "Add the missing dimensions or mark them intentionally out of scope."
            ))

        if unsupported:
            findings.append(Finding(
                "high",
                "evidence_support",
                asset["asset_id"],
                f"Narrative dimensions lack support: {', '.join(unsupported)}.",
                "Add evidence, examples, source context, method notes, or limitation language."
            ))

        if scores["agency_score"] < 0.67:
            findings.append(Finding(
                "high",
                "agency",
                asset["asset_id"],
                "Agency representation is weak.",
                "Review affected people, institutional responsibility, and audience agency."
            ))

        if scores["ethical_review_score"] < 0.75:
            findings.append(Finding(
                "high",
                "ethical_review",
                asset["asset_id"],
                "Ethical storytelling score is below standard.",
                "Remove savior framing, overdramatization, unsupported anecdote, or pressure CTA."
            ))

        if status != "ready":
            findings.append(Finding(
                "medium",
                "storytelling_readiness",
                asset["asset_id"],
                f"Storytelling readiness is {scores['storytelling_readiness_score']:.2f}.",
                "Review narrative completeness, evidence, agency, transformation credibility, governance, and ethical-risk flags."
            ))

    return rows, findings

def dimension_summary(assets):
    rows = []
    for dimension in DIMENSIONS:
        present = sum(1 for asset in assets if yes(asset[f"{dimension}_present"]))
        supported = sum(1 for asset in assets if yes(asset[f"{dimension}_present"]) and yes(asset[f"{dimension}_supported"]))
        rows.append({
            "narrative_dimension": dimension,
            "assets_with_dimension": present,
            "assets_with_support": supported,
            "presence_rate": round(present / len(assets), 4) if assets else 0,
            "support_rate": round(supported / present, 4) if present else 0
        })
    return rows

def audience_summary(rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["audience"]].append(float(row["storytelling_readiness_score"]))
    return [{"audience": audience, "asset_count": len(values), "average_storytelling_readiness": round(average(values), 4)} for audience, values in sorted(grouped.items())]

def main():
    for d in [TABLES, REPORTS, AUDIT_LOGS, CATALOG]:
        d.mkdir(parents=True, exist_ok=True)

    assets = read_csv(DATA / "storytelling_framework_inventory.csv")
    manual_queue = read_csv(DATA / "editorial_review_queue.csv")

    readiness_rows, findings = audit_assets(assets)
    dimension_rows = dimension_summary(assets)
    audience_rows = audience_summary(readiness_rows)

    queue_rows = [
        {
            "source": "manual_review_queue",
            "severity": row["severity"],
            "category": row["issue_type"],
            "identifier": row["record_id"],
            "message": row["review_note"],
            "recommended_action": "Resolve through storytelling framework governance."
        }
        for row in manual_queue
    ] + [asdict(finding) for finding in findings]

    catalog_rows = [{
        "series": "Content Frameworks",
        "article_slug": "storytelling-frameworks-for-transformation-and-action",
        "asset_id": row["asset_id"],
        "asset_name": row["asset_name"],
        "asset_type": row["asset_type"],
        "story_purpose": row["story_purpose"],
        "audience": row["audience"],
        "storytelling_readiness_score": row["storytelling_readiness_score"],
        "storytelling_status": row["storytelling_status"],
        "github_path": "articles/storytelling-frameworks-for-transformation-and-action/"
    } for row in readiness_rows]

    write_csv(TABLES / "storytelling_readiness_report.csv", readiness_rows)
    write_csv(TABLES / "storytelling_dimension_summary_report.csv", dimension_rows)
    write_csv(TABLES / "storytelling_audience_summary_report.csv", audience_rows)
    write_csv(TABLES / "storytelling_governance_queue.csv", queue_rows)
    write_csv(CATALOG / "storytelling_catalog_export.csv", catalog_rows)

    report = {
        "article": "Storytelling Frameworks for Transformation and Action",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "assets": len(assets),
            "findings": len(findings),
            "governance_queue": len(queue_rows)
        },
        "dimension_summary": dimension_rows,
        "readiness": readiness_rows,
        "governance_queue": queue_rows
    }

    write_json(REPORTS / "storytelling_framework_audit.json", report)
    write_json(AUDIT_LOGS / "storytelling_framework_findings.json", [asdict(finding) for finding in findings])
    (REPORTS / "storytelling_framework_audit.md").write_text("# Storytelling Framework Audit\n\nGenerated outputs are available in `outputs/`.\n", encoding="utf-8")

    print("Storytelling framework audit complete.")
    print(TABLES / "storytelling_readiness_report.csv")
    print(TABLES / "storytelling_governance_queue.csv")
    print(REPORTS / "storytelling_framework_audit.json")

if __name__ == "__main__":
    main()
