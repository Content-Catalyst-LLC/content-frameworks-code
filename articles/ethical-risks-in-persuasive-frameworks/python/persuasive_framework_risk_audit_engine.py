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

AGENCY_FIELDS = ["clear_claim", "refusal_visible", "decision_support_present", "commitment_transparent"]
PRESSURE_FIELDS = ["uses_false_urgency", "uses_false_scarcity", "uses_fear_escalation", "uses_shame_pressure"]
GOVERNANCE_FIELDS = ["review_owner_present", "evidence_reviewed", "accessibility_reviewed", "revision_queue_checked"]
DARK_PATTERN_FIELDS = ["hidden_terms", "cancellation_friction", "preselected_consent", "disguised_ad"]

READINESS_THRESHOLD = 0.78
PRESSURE_MAXIMUM = 0.25
EVIDENCE_MINIMUM = 0.70

@dataclass(frozen=True)
class Finding:
    severity: str
    category: str
    identifier: str
    message: str
    recommended_action: str

def yes(value):
    return str(value).strip().lower() in {"yes", "true", "1", "present", "complete"}

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
    agency = average([int(yes(asset[field])) for field in AGENCY_FIELDS])
    pressure = average([int(yes(asset[field])) for field in PRESSURE_FIELDS])
    governance = average([int(yes(asset[field])) for field in GOVERNANCE_FIELDS])
    dark_pattern_risk = average([int(yes(asset[field])) for field in DARK_PATTERN_FIELDS])

    total_claims = max(int(asset["total_persuasive_claims"]), 1)
    supported_claims = int(asset["supported_persuasive_claims"])
    evidence = min(supported_claims / total_claims, 1.0)

    accessibility = (
        int(yes(asset["plain_language_present"])) +
        int(yes(asset["keyboard_path_clear"])) +
        int(yes(asset["contrast_and_readability_checked"])) +
        int(yes(asset["terms_accessible_before_action"]))
    ) / 4

    vulnerability_risk = (
        int(yes(asset["high_stakes_context"])) +
        int(yes(asset["financial_or_health_pressure"])) +
        int(yes(asset["audience_dependency_present"])) +
        int(yes(asset["time_pressure_present"]))
    ) / 4

    responsible_score = (
        0.24 * agency +
        0.24 * evidence +
        0.18 * governance +
        0.14 * accessibility -
        0.12 * pressure -
        0.08 * vulnerability_risk -
        0.10 * dark_pattern_risk
    )

    responsible_score = max(0.0, min(responsible_score, 1.0))

    return {
        "agency_score": round(agency, 4),
        "pressure_score": round(pressure, 4),
        "evidence_support_score": round(evidence, 4),
        "governance_score": round(governance, 4),
        "accessibility_score": round(accessibility, 4),
        "vulnerability_risk_score": round(vulnerability_risk, 4),
        "dark_pattern_risk_score": round(dark_pattern_risk, 4),
        "responsible_persuasion_score": round(responsible_score, 4)
    }

def audit_assets(assets):
    rows, findings = [], []

    for asset in assets:
        scores = score_asset(asset)

        status = (
            "ready"
            if scores["responsible_persuasion_score"] >= READINESS_THRESHOLD
            and scores["pressure_score"] <= PRESSURE_MAXIMUM
            and scores["evidence_support_score"] >= EVIDENCE_MINIMUM
            and scores["dark_pattern_risk_score"] == 0
            else "governance review"
        )

        row = {
            "asset_id": asset["asset_id"],
            "asset_name": asset["asset_name"],
            "asset_type": asset["asset_type"],
            "framework_used": asset["framework_used"],
            "audience": asset["audience"],
            "requested_action": asset["requested_action"],
            **scores,
            "ethical_status": status
        }
        rows.append(row)

        if scores["agency_score"] < 0.75:
            findings.append(Finding(
                "high",
                "agency",
                asset["asset_id"],
                "Audience agency support is weak.",
                "Improve claim clarity, refusal visibility, decision support, and commitment transparency."
            ))

        if scores["pressure_score"] > PRESSURE_MAXIMUM:
            findings.append(Finding(
                "high",
                "pressure",
                asset["asset_id"],
                "Pressure cues exceed threshold.",
                "Remove false urgency, false scarcity, fear escalation, or shame pressure."
            ))

        if scores["evidence_support_score"] < EVIDENCE_MINIMUM:
            findings.append(Finding(
                "high",
                "evidence",
                asset["asset_id"],
                "Persuasive claims lack sufficient support.",
                "Add evidence, examples, source support, limitations, or reduce claim strength."
            ))

        if scores["dark_pattern_risk_score"] > 0:
            findings.append(Finding(
                "critical",
                "dark_pattern",
                asset["asset_id"],
                "Dark-pattern risk is present.",
                "Remove hidden terms, cancellation friction, preselected consent, or disguised advertising."
            ))

        if scores["vulnerability_risk_score"] > 0.50:
            findings.append(Finding(
                "medium",
                "vulnerability",
                asset["asset_id"],
                "Audience vulnerability risk is elevated.",
                "Increase transparency, reduce pressure, and add decision support."
            ))

        if status != "ready":
            findings.append(Finding(
                "medium",
                "ethical_readiness",
                asset["asset_id"],
                f"Responsible persuasion score is {scores['responsible_persuasion_score']:.2f}.",
                "Review agency, evidence, pressure, accessibility, vulnerability, dark-pattern risk, and governance."
            ))

    return rows, findings

def summary_by_framework(rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["framework_used"]].append(float(row["responsible_persuasion_score"]))
    return [{
        "framework_used": framework,
        "asset_count": len(scores),
        "average_responsible_persuasion_score": round(average(scores), 4)
    } for framework, scores in sorted(grouped.items())]

def risk_dimension_summary(rows):
    fields = [
        "agency_score",
        "pressure_score",
        "evidence_support_score",
        "governance_score",
        "accessibility_score",
        "vulnerability_risk_score",
        "dark_pattern_risk_score",
        "responsible_persuasion_score"
    ]
    return [{"risk_dimension": field, "average_score": round(average([float(row[field]) for row in rows]), 4)} for field in fields]

def main():
    for directory in [TABLES, REPORTS, AUDIT_LOGS, CATALOG]:
        directory.mkdir(parents=True, exist_ok=True)

    assets = read_csv(DATA / "persuasive_framework_risk_inventory.csv")
    manual_queue = read_csv(DATA / "editorial_review_queue.csv")

    readiness_rows, findings = audit_assets(assets)
    framework_rows = summary_by_framework(readiness_rows)
    risk_rows = risk_dimension_summary(readiness_rows)

    queue_rows = [
        {
            "source": "manual_review_queue",
            "severity": row["severity"],
            "category": row["issue_type"],
            "identifier": row["record_id"],
            "message": row["review_note"],
            "recommended_action": "Resolve through persuasive-framework ethical governance."
        }
        for row in manual_queue
    ] + [asdict(finding) for finding in findings]

    catalog_rows = [{
        "series": "Content Frameworks",
        "article_slug": "ethical-risks-in-persuasive-frameworks",
        "asset_id": row["asset_id"],
        "asset_name": row["asset_name"],
        "asset_type": row["asset_type"],
        "framework_used": row["framework_used"],
        "audience": row["audience"],
        "responsible_persuasion_score": row["responsible_persuasion_score"],
        "ethical_status": row["ethical_status"],
        "github_path": "articles/ethical-risks-in-persuasive-frameworks/"
    } for row in readiness_rows]

    write_csv(TABLES / "persuasive_framework_risk_report.csv", readiness_rows)
    write_csv(TABLES / "persuasive_framework_summary_report.csv", framework_rows)
    write_csv(TABLES / "persuasive_framework_risk_summary_report.csv", risk_rows)
    write_csv(TABLES / "persuasive_framework_governance_queue.csv", queue_rows)
    write_csv(CATALOG / "persuasive_framework_catalog_export.csv", catalog_rows)

    report = {
        "article": "Ethical Risks in Persuasive Frameworks",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "assets": len(assets),
            "findings": len(findings),
            "governance_queue": len(queue_rows)
        },
        "framework_summary": framework_rows,
        "risk_summary": risk_rows,
        "readiness": readiness_rows,
        "governance_queue": queue_rows
    }

    write_json(REPORTS / "persuasive_framework_risk_audit.json", report)
    write_json(AUDIT_LOGS / "persuasive_framework_findings.json", [asdict(finding) for finding in findings])
    (REPORTS / "persuasive_framework_risk_audit.md").write_text("# Persuasive Framework Ethical-Risk Audit\n\nGenerated outputs are available in `outputs/`.\n", encoding="utf-8")

    print("Persuasive framework ethical-risk audit complete.")
    print(TABLES / "persuasive_framework_risk_report.csv")
    print(TABLES / "persuasive_framework_governance_queue.csv")
    print(REPORTS / "persuasive_framework_risk_audit.json")

if __name__ == "__main__":
    main()
