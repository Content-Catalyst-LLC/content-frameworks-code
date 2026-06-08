#!/usr/bin/env python3
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import defaultdict
from datetime import datetime, timezone
import csv, json

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
TABLES = ROOT / "outputs" / "tables"
REPORTS = ROOT / "outputs" / "reports"
AUDIT_LOGS = ROOT / "outputs" / "audit_logs"
CATALOG = ROOT / "outputs" / "catalog_exports"

JOB_DIMENSIONS = ["functional", "emotional", "social", "strategic", "learning"]
READINESS_THRESHOLD = 0.78
EVIDENCE_MINIMUM = 0.70
CONTENT_FIT_MINIMUM = 0.70

WEIGHTS = {
    "job_clarity": 0.24,
    "content_fit": 0.22,
    "evidence_support": 0.20,
    "outcome_support": 0.14,
    "agency": 0.10,
    "governance": 0.10
}

@dataclass(frozen=True)
class Finding:
    severity: str
    category: str
    identifier: str
    message: str
    recommended_action: str

def yes(value):
    return str(value).strip().lower() in {"yes", "true", "1", "present", "complete", "ready"}

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

def score_asset(asset):
    job_clarity = (
        int(yes(asset["situation_defined"])) +
        int(yes(asset["motivation_defined"])) +
        int(yes(asset["desired_outcome_defined"])) +
        int(yes(asset["constraint_defined"]))
    ) / 4

    job_dimension_support = average([
        int(yes(asset[f"{dimension}_job_supported"]))
        for dimension in JOB_DIMENSIONS
    ])

    content_fit = (
        int(yes(asset["format_matches_job"])) +
        int(yes(asset["examples_match_job"])) +
        int(yes(asset["sections_match_job"])) +
        int(yes(asset["next_step_matches_job"]))
    ) / 4

    total_assumptions = max(int(asset["total_job_assumptions"]), 1)
    supported_assumptions = int(asset["supported_job_assumptions"])
    evidence_support = min(supported_assumptions / total_assumptions, 1.0)

    outcome_support = (
        int(yes(asset["success_criteria_defined"])) +
        int(yes(asset["measurement_matches_job"])) +
        int(yes(asset["content_supports_progress"]))
    ) / 3

    agency = (
        int(yes(asset["audience_choice_preserved"])) +
        int(yes(asset["alternatives_visible"])) +
        int(yes(asset["claims_bounded"]))
    ) / 3

    governance = (
        int(yes(asset["review_owner_present"])) +
        int(yes(asset["last_review_date_present"])) +
        int(yes(asset["revision_queue_checked"])) +
        int(yes(asset["job_assumption_reviewed"]))
    ) / 4

    readiness = (
        WEIGHTS["job_clarity"] * job_clarity +
        WEIGHTS["content_fit"] * content_fit +
        WEIGHTS["evidence_support"] * evidence_support +
        WEIGHTS["outcome_support"] * outcome_support +
        WEIGHTS["agency"] * agency +
        WEIGHTS["governance"] * governance
    )

    return {
        "job_clarity_score": round(job_clarity, 4),
        "job_dimension_support_score": round(job_dimension_support, 4),
        "content_fit_score": round(content_fit, 4),
        "evidence_support_score": round(evidence_support, 4),
        "outcome_support_score": round(outcome_support, 4),
        "agency_score": round(agency, 4),
        "governance_score": round(governance, 4),
        "jtbd_readiness_score": round(readiness, 4)
    }

def audit_assets(assets):
    rows, findings = [], []

    for asset in assets:
        scores = score_asset(asset)

        unsupported_dimensions = [
            dimension
            for dimension in JOB_DIMENSIONS
            if not yes(asset[f"{dimension}_job_supported"])
        ]

        status = (
            "ready"
            if scores["jtbd_readiness_score"] >= READINESS_THRESHOLD
            and scores["evidence_support_score"] >= EVIDENCE_MINIMUM
            and scores["content_fit_score"] >= CONTENT_FIT_MINIMUM
            else "governance review"
        )

        row = {
            "asset_id": asset["asset_id"],
            "asset_name": asset["asset_name"],
            "asset_type": asset["asset_type"],
            "primary_job": asset["primary_job"],
            "audience": asset["audience"],
            **scores,
            "unsupported_job_dimensions": ";".join(unsupported_dimensions),
            "jtbd_status": status
        }
        rows.append(row)

        if scores["job_clarity_score"] < 0.75:
            findings.append(Finding(
                "medium",
                "job_clarity",
                asset["asset_id"],
                "Job statement is incomplete.",
                "Define situation, motivation, desired outcome, and constraint."
            ))

        if scores["evidence_support_score"] < EVIDENCE_MINIMUM:
            findings.append(Finding(
                "high",
                "evidence_support",
                asset["asset_id"],
                "Audience-job assumptions lack sufficient evidence.",
                "Add interviews, feedback, analytics, search evidence, or observation."
            ))

        if scores["content_fit_score"] < CONTENT_FIT_MINIMUM:
            findings.append(Finding(
                "high",
                "content_fit",
                asset["asset_id"],
                "Content format does not adequately match the audience job.",
                "Revise format, examples, section structure, or next step."
            ))

        if scores["agency_score"] < 0.67:
            findings.append(Finding(
                "medium",
                "agency",
                asset["asset_id"],
                "Audience agency support is weak.",
                "Show alternatives, bound claims, and preserve choice."
            ))

        if status != "ready":
            findings.append(Finding(
                "medium",
                "jtbd_readiness",
                asset["asset_id"],
                f"JTBD readiness is {scores['jtbd_readiness_score']:.2f}.",
                "Review job clarity, evidence support, content fit, outcome support, agency, and governance."
            ))

    return rows, findings

def summary_by_job(rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["primary_job"]].append(float(row["jtbd_readiness_score"]))
    return [{
        "primary_job": job,
        "asset_count": len(scores),
        "average_jtbd_readiness": round(average(scores), 4)
    } for job, scores in sorted(grouped.items())]

def summary_by_audience(rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["audience"]].append(float(row["jtbd_readiness_score"]))
    return [{
        "audience": audience,
        "asset_count": len(scores),
        "average_jtbd_readiness": round(average(scores), 4)
    } for audience, scores in sorted(grouped.items())]

def dimension_summary(assets):
    return [{
        "job_dimension": dimension,
        "assets_supporting_dimension": sum(1 for asset in assets if yes(asset[f"{dimension}_job_supported"])),
        "support_rate": round(sum(1 for asset in assets if yes(asset[f"{dimension}_job_supported"])) / len(assets), 4) if assets else 0
    } for dimension in JOB_DIMENSIONS]

def main():
    for directory in [TABLES, REPORTS, AUDIT_LOGS, CATALOG]:
        directory.mkdir(parents=True, exist_ok=True)

    assets = read_csv(DATA / "jtbd_content_inventory.csv")
    manual_queue = read_csv(DATA / "editorial_review_queue.csv")

    readiness_rows, findings = audit_assets(assets)
    job_rows = summary_by_job(readiness_rows)
    audience_rows = summary_by_audience(readiness_rows)
    dimension_rows = dimension_summary(assets)

    queue_rows = [
        {
            "source": "manual_review_queue",
            "severity": row["severity"],
            "category": row["issue_type"],
            "identifier": row["record_id"],
            "message": row["review_note"],
            "recommended_action": "Resolve through JTBD content governance."
        }
        for row in manual_queue
    ] + [asdict(finding) for finding in findings]

    catalog_rows = [{
        "series": "Content Frameworks",
        "article_slug": "jobs-to-be-done-and-the-problem-of-audience-need",
        "asset_id": row["asset_id"],
        "asset_name": row["asset_name"],
        "asset_type": row["asset_type"],
        "primary_job": row["primary_job"],
        "audience": row["audience"],
        "jtbd_readiness_score": row["jtbd_readiness_score"],
        "jtbd_status": row["jtbd_status"],
        "github_path": "articles/jobs-to-be-done-and-the-problem-of-audience-need/"
    } for row in readiness_rows]

    write_csv(TABLES / "jtbd_content_readiness_report.csv", readiness_rows)
    write_csv(TABLES / "jtbd_job_summary_report.csv", job_rows)
    write_csv(TABLES / "jtbd_audience_summary_report.csv", audience_rows)
    write_csv(TABLES / "jtbd_dimension_summary_report.csv", dimension_rows)
    write_csv(TABLES / "jtbd_governance_queue.csv", queue_rows)
    write_csv(CATALOG / "jtbd_catalog_export.csv", catalog_rows)

    report = {
        "article": "Jobs to Be Done and the Problem of Audience Need",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "assets": len(assets),
            "findings": len(findings),
            "governance_queue": len(queue_rows)
        },
        "job_summary": job_rows,
        "audience_summary": audience_rows,
        "dimension_summary": dimension_rows,
        "readiness": readiness_rows,
        "governance_queue": queue_rows
    }

    write_json(REPORTS / "jtbd_content_audit.json", report)
    write_json(AUDIT_LOGS / "jtbd_findings.json", [asdict(finding) for finding in findings])
    (REPORTS / "jtbd_content_audit.md").write_text("# JTBD Content Audit\n\nGenerated outputs are available in `outputs/`.\n", encoding="utf-8")

    print("JTBD content audit complete.")
    print(TABLES / "jtbd_content_readiness_report.csv")
    print(TABLES / "jtbd_governance_queue.csv")
    print(REPORTS / "jtbd_content_audit.json")

if __name__ == "__main__":
    main()
