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

THRESHOLD = 0.78
ETHICAL_MINIMUM = 0.70
WEIGHTS = {
    "current_state": 0.20,
    "stakes": 0.20,
    "transformation": 0.20,
    "bridge": 0.20,
    "ethical_review": 0.20
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

def sequence_balance(values):
    mean = average(values)
    if mean == 0:
        return 0.0
    variance = average([(value - mean) ** 2 for value in values])
    sd = math.sqrt(variance)
    return max(0.0, min(1.0, 1 - min(sd / mean, 1)))

def score_message(row):
    current_state = (
        int(yes(row["problem_clear"])) +
        int(yes(row["before_state_specific"])) +
        int(yes(row["audience_context_present"]))
    ) / 3

    stakes = (
        int(yes(row["stakes_visible"])) +
        int(yes(row["agitation_proportionate"])) +
        int(yes(row["consequence_supported"]))
    ) / 3

    transformation = (
        int(yes(row["after_state_credible"])) +
        int(yes(row["transformation_bounded"])) +
        int(yes(row["benefit_claim_supported"]))
    ) / 3

    bridge = (
        int(yes(row["solution_fit_clear"])) +
        int(yes(row["bridge_mechanism_visible"])) +
        int(yes(row["commitment_transparent"]))
    ) / 3

    ethics = (
        int(not yes(row["uses_invented_pain"])) +
        int(not yes(row["uses_fear_escalation"])) +
        int(not yes(row["uses_false_urgency"])) +
        int(yes(row["audience_agency_preserved"]))
    ) / 4

    readiness = (
        WEIGHTS["current_state"] * current_state +
        WEIGHTS["stakes"] * stakes +
        WEIGHTS["transformation"] * transformation +
        WEIGHTS["bridge"] * bridge +
        WEIGHTS["ethical_review"] * ethics
    )

    return {
        "current_state_score": round(current_state, 4),
        "stakes_score": round(stakes, 4),
        "transformation_score": round(transformation, 4),
        "bridge_score": round(bridge, 4),
        "ethical_review_score": round(ethics, 4),
        "sequence_balance_score": round(sequence_balance([current_state, stakes, transformation, bridge]), 4),
        "pas_bab_readiness_score": round(readiness, 4)
    }

def audit_messages(messages):
    rows, findings = [], []

    for message in messages:
        scores = score_message(message)
        status = "ready" if scores["pas_bab_readiness_score"] >= THRESHOLD and scores["ethical_review_score"] >= ETHICAL_MINIMUM else "governance review"

        row = {
            "message_id": message["message_id"],
            "asset_name": message["asset_name"],
            "asset_type": message["asset_type"],
            "framework_used": message["framework_used"],
            "audience": message["audience"],
            **scores,
            "pas_bab_status": status
        }
        rows.append(row)

        if scores["current_state_score"] < 0.67:
            findings.append(Finding(
                "medium",
                "current_state",
                message["message_id"],
                "Problem or before state is weakly defined.",
                "Clarify the current state, audience context, and real friction."
            ))

        if scores["stakes_score"] < 0.67:
            findings.append(Finding(
                "medium",
                "stakes",
                message["message_id"],
                "Stakes or agitation are underdeveloped or poorly supported.",
                "Clarify consequences with proportional evidence and context."
            ))

        if scores["transformation_score"] < 0.67:
            findings.append(Finding(
                "medium",
                "transformation",
                message["message_id"],
                "After state or transformation claim is weak.",
                "Bound the transformation claim and support benefit language."
            ))

        if scores["bridge_score"] < 0.67:
            findings.append(Finding(
                "high",
                "bridge",
                message["message_id"],
                "Solution or bridge mechanism is unclear.",
                "Explain solution fit, bridge mechanism, effort, cost, and conditions."
            ))

        if scores["ethical_review_score"] < ETHICAL_MINIMUM:
            findings.append(Finding(
                "high",
                "ethical_review",
                message["message_id"],
                "Ethical review score is below the minimum threshold.",
                "Remove invented pain, fear escalation, false urgency, or agency-reducing pressure."
            ))

        if status != "ready":
            findings.append(Finding(
                "medium",
                "pas_bab_readiness",
                message["message_id"],
                f"PAS/BAB readiness is {scores['pas_bab_readiness_score']:.2f}.",
                "Review current state, stakes, transformation, bridge clarity, and ethical-risk flags."
            ))

    return rows, findings

def summary_by_framework(rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["framework_used"]].append(float(row["pas_bab_readiness_score"]))
    return [{
        "framework_used": framework,
        "asset_count": len(values),
        "average_pas_bab_readiness": round(average(values), 4)
    } for framework, values in sorted(grouped.items())]

def stage_summary(rows):
    fields = ["current_state_score", "stakes_score", "transformation_score", "bridge_score", "ethical_review_score", "sequence_balance_score"]
    return [{"stage_or_metric": field, "average_score": round(average([float(row[field]) for row in rows]), 4)} for field in fields]

def main():
    for d in [TABLES, REPORTS, AUDIT_LOGS, CATALOG]:
        d.mkdir(parents=True, exist_ok=True)

    messages = read_csv(DATA / "pas_bab_message_inventory.csv")
    manual_queue = read_csv(DATA / "editorial_review_queue.csv")

    readiness_rows, findings = audit_messages(messages)
    framework_rows = summary_by_framework(readiness_rows)
    summary_rows = stage_summary(readiness_rows)

    queue_rows = [
        {
            "source": "manual_review_queue",
            "severity": row["severity"],
            "category": row["issue_type"],
            "identifier": row["record_id"],
            "message": row["review_note"],
            "recommended_action": "Resolve through PAS/BAB sequence governance."
        }
        for row in manual_queue
    ] + [asdict(finding) for finding in findings]

    catalog_rows = [{
        "series": "Content Frameworks",
        "article_slug": "pas-bab-and-the-structure-of-tension-and-transformation",
        "message_id": row["message_id"],
        "asset_name": row["asset_name"],
        "asset_type": row["asset_type"],
        "framework_used": row["framework_used"],
        "audience": row["audience"],
        "pas_bab_readiness_score": row["pas_bab_readiness_score"],
        "pas_bab_status": row["pas_bab_status"],
        "github_path": "articles/pas-bab-and-the-structure-of-tension-and-transformation/"
    } for row in readiness_rows]

    write_csv(TABLES / "pas_bab_sequence_readiness_report.csv", readiness_rows)
    write_csv(TABLES / "pas_bab_framework_summary_report.csv", framework_rows)
    write_csv(TABLES / "pas_bab_stage_summary_report.csv", summary_rows)
    write_csv(TABLES / "pas_bab_governance_queue.csv", queue_rows)
    write_csv(CATALOG / "pas_bab_sequence_catalog_export.csv", catalog_rows)

    report = {
        "article": "PAS, BAB, and the Structure of Tension and Transformation",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "messages": len(messages),
            "findings": len(findings),
            "governance_queue": len(queue_rows)
        },
        "framework_summary": framework_rows,
        "stage_summary": summary_rows,
        "readiness": readiness_rows,
        "governance_queue": queue_rows
    }

    write_json(REPORTS / "pas_bab_sequence_audit.json", report)
    write_json(AUDIT_LOGS / "pas_bab_sequence_findings.json", [asdict(finding) for finding in findings])
    (REPORTS / "pas_bab_sequence_audit.md").write_text("# PAS/BAB Sequence Audit\n\nGenerated outputs are available in `outputs/`.\n", encoding="utf-8")

    print("PAS/BAB sequence audit complete.")
    print(TABLES / "pas_bab_sequence_readiness_report.csv")
    print(TABLES / "pas_bab_governance_queue.csv")
    print(REPORTS / "pas_bab_sequence_audit.json")

if __name__ == "__main__":
    main()
