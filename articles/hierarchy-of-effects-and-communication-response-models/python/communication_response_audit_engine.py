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

STAGES = ["awareness", "knowledge", "liking", "preference", "conviction", "action", "follow_through"]
THRESHOLD = 0.78
GOVERNANCE_MINIMUM = 0.70
WEIGHTS = {
    "stage_coverage": 0.22,
    "evidence_support": 0.22,
    "stage_balance": 0.16,
    "audience_fit": 0.16,
    "governance": 0.14,
    "ethical_review": 0.10
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
    stage_values = [int(yes(asset[f"{stage}_supported"])) for stage in STAGES]
    evidence_values = [
        int(yes(asset[f"{stage}_evidence_present"]))
        for stage in STAGES
        if yes(asset[f"{stage}_supported"])
    ]

    stage_coverage = sum(stage_values) / len(STAGES)
    evidence_support = average(evidence_values) if evidence_values else 0.0
    stage_balance = balance_score(stage_values)

    audience_fit = (
        int(yes(asset["audience_context_present"])) +
        int(yes(asset["audience_readiness_defined"])) +
        int(yes(asset["next_step_matches_stage"]))
    ) / 3

    governance = (
        int(yes(asset["measurement_aligned"])) +
        int(yes(asset["review_owner_present"])) +
        int(yes(asset["last_review_date_present"])) +
        int(yes(asset["revision_queue_checked"]))
    ) / 4

    ethical_review = (
        int(not yes(asset["uses_false_urgency"])) +
        int(not yes(asset["overclaims_response"])) +
        int(not yes(asset["uses_pressure_cta"])) +
        int(yes(asset["audience_agency_preserved"]))
    ) / 4

    readiness = (
        WEIGHTS["stage_coverage"] * stage_coverage +
        WEIGHTS["evidence_support"] * evidence_support +
        WEIGHTS["stage_balance"] * stage_balance +
        WEIGHTS["audience_fit"] * audience_fit +
        WEIGHTS["governance"] * governance +
        WEIGHTS["ethical_review"] * ethical_review
    )

    return {
        "stage_coverage_score": round(stage_coverage, 4),
        "evidence_support_score": round(evidence_support, 4),
        "stage_balance_score": round(stage_balance, 4),
        "audience_fit_score": round(audience_fit, 4),
        "governance_score": round(governance, 4),
        "ethical_review_score": round(ethical_review, 4),
        "response_readiness_score": round(readiness, 4)
    }

def audit_assets(assets):
    rows, findings = [], []

    for asset in assets:
        scores = score_asset(asset)
        status = "ready" if scores["response_readiness_score"] >= THRESHOLD and scores["governance_score"] >= GOVERNANCE_MINIMUM else "governance review"

        unsupported = [stage for stage in STAGES if yes(asset[f"{stage}_supported"]) and not yes(asset[f"{stage}_evidence_present"])]
        missing = [stage for stage in STAGES if not yes(asset[f"{stage}_supported"])]

        row = {
            "asset_id": asset["asset_id"],
            "asset_name": asset["asset_name"],
            "asset_type": asset["asset_type"],
            "primary_response_stage": asset["primary_response_stage"],
            "audience": asset["audience"],
            **scores,
            "missing_stage_support": ";".join(missing),
            "unsupported_stage_claims": ";".join(unsupported),
            "response_status": status
        }
        rows.append(row)

        if scores["stage_coverage_score"] < 0.50:
            findings.append(Finding(
                "medium",
                "stage_coverage",
                asset["asset_id"],
                "Response-stage coverage is narrow.",
                "Confirm that narrow stage coverage is intentional or add supporting assets."
            ))

        if unsupported:
            findings.append(Finding(
                "high",
                "evidence_support",
                asset["asset_id"],
                f"Supported response stages lack evidence: {', '.join(unsupported)}.",
                "Add evidence, examples, measurement notes, or limitation language."
            ))

        if scores["audience_fit_score"] < 0.67:
            findings.append(Finding(
                "medium",
                "audience_fit",
                asset["asset_id"],
                "Audience readiness support is weak.",
                "Define audience context, readiness level, and next-step fit."
            ))

        if scores["ethical_review_score"] < 0.75:
            findings.append(Finding(
                "high",
                "ethical_review",
                asset["asset_id"],
                "Ethical review score is below standard.",
                "Remove false urgency, pressure CTAs, overclaiming, or agency-reducing language."
            ))

        if status != "ready":
            findings.append(Finding(
                "medium",
                "response_readiness",
                asset["asset_id"],
                f"Response readiness is {scores['response_readiness_score']:.2f}.",
                "Review stage support, evidence support, audience fit, governance, and ethical-risk flags."
            ))

    return rows, findings

def stage_summary(assets):
    rows = []
    for stage in STAGES:
        supported = sum(1 for asset in assets if yes(asset[f"{stage}_supported"]))
        evidence = sum(1 for asset in assets if yes(asset[f"{stage}_supported"]) and yes(asset[f"{stage}_evidence_present"]))
        rows.append({
            "response_stage": stage,
            "assets_supporting_stage": supported,
            "assets_with_evidence": evidence,
            "support_rate": round(supported / len(assets), 4) if assets else 0,
            "evidence_rate": round(evidence / supported, 4) if supported else 0
        })
    return rows

def audience_summary(rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["audience"]].append(float(row["response_readiness_score"]))
    return [{"audience": audience, "asset_count": len(values), "average_response_readiness": round(average(values), 4)} for audience, values in sorted(grouped.items())]

def main():
    for d in [TABLES, REPORTS, AUDIT_LOGS, CATALOG]:
        d.mkdir(parents=True, exist_ok=True)

    assets = read_csv(DATA / "communication_response_inventory.csv")
    manual_queue = read_csv(DATA / "editorial_review_queue.csv")

    readiness_rows, findings = audit_assets(assets)
    stage_rows = stage_summary(assets)
    audience_rows = audience_summary(readiness_rows)

    queue_rows = [
        {
            "source": "manual_review_queue",
            "severity": row["severity"],
            "category": row["issue_type"],
            "identifier": row["record_id"],
            "message": row["review_note"],
            "recommended_action": "Resolve through communication response governance."
        }
        for row in manual_queue
    ] + [asdict(finding) for finding in findings]

    catalog_rows = [{
        "series": "Content Frameworks",
        "article_slug": "hierarchy-of-effects-and-communication-response-models",
        "asset_id": row["asset_id"],
        "asset_name": row["asset_name"],
        "asset_type": row["asset_type"],
        "primary_response_stage": row["primary_response_stage"],
        "audience": row["audience"],
        "response_readiness_score": row["response_readiness_score"],
        "response_status": row["response_status"],
        "github_path": "articles/hierarchy-of-effects-and-communication-response-models/"
    } for row in readiness_rows]

    write_csv(TABLES / "communication_response_readiness_report.csv", readiness_rows)
    write_csv(TABLES / "communication_response_stage_summary_report.csv", stage_rows)
    write_csv(TABLES / "communication_response_audience_summary_report.csv", audience_rows)
    write_csv(TABLES / "communication_response_governance_queue.csv", queue_rows)
    write_csv(CATALOG / "communication_response_catalog_export.csv", catalog_rows)

    report = {
        "article": "Hierarchy of Effects and Communication Response Models",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "assets": len(assets),
            "findings": len(findings),
            "governance_queue": len(queue_rows)
        },
        "stage_summary": stage_rows,
        "readiness": readiness_rows,
        "governance_queue": queue_rows
    }

    write_json(REPORTS / "communication_response_audit.json", report)
    write_json(AUDIT_LOGS / "communication_response_findings.json", [asdict(finding) for finding in findings])
    (REPORTS / "communication_response_audit.md").write_text("# Communication Response Audit\n\nGenerated outputs are available in `outputs/`.\n", encoding="utf-8")

    print("Communication response audit complete.")
    print(TABLES / "communication_response_readiness_report.csv")
    print(TABLES / "communication_response_governance_queue.csv")
    print(REPORTS / "communication_response_audit.json")

if __name__ == "__main__":
    main()
