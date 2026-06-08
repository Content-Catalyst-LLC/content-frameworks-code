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
    "attention": 0.18,
    "interest": 0.20,
    "desire": 0.22,
    "action": 0.20,
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

def stage_balance(values):
    mean = average(values)
    if mean == 0:
        return 0.0
    variance = average([(value - mean) ** 2 for value in values])
    sd = math.sqrt(variance)
    return max(0.0, min(1.0, 1 - min(sd / mean, 1)))

def score_message(row):
    attention = (
        int(yes(row["headline_relevant"])) +
        int(yes(row["opening_problem_clear"])) +
        int(yes(row["attention_claim_supported"]))
    ) / 3

    interest = (
        int(yes(row["audience_relevance_visible"])) +
        int(yes(row["context_provided"])) +
        int(yes(row["evidence_or_example_present"]))
    ) / 3

    desire = (
        int(yes(row["value_proposition_clear"])) +
        int(yes(row["benefit_claim_supported"])) +
        int(yes(row["fit_and_limits_visible"]))
    ) / 3

    action = (
        int(yes(row["cta_clear"])) +
        int(yes(row["cta_feasible"])) +
        int(yes(row["commitment_transparent"]))
    ) / 3

    ethics = (
        int(not yes(row["uses_false_urgency"])) +
        int(not yes(row["uses_exaggerated_claims"])) +
        int(not yes(row["uses_hidden_cost_or_condition"])) +
        int(yes(row["audience_agency_preserved"]))
    ) / 4

    readiness = (
        WEIGHTS["attention"] * attention +
        WEIGHTS["interest"] * interest +
        WEIGHTS["desire"] * desire +
        WEIGHTS["action"] * action +
        WEIGHTS["ethical_review"] * ethics
    )

    return {
        "attention_score": round(attention, 4),
        "interest_score": round(interest, 4),
        "desire_score": round(desire, 4),
        "action_score": round(action, 4),
        "ethical_review_score": round(ethics, 4),
        "stage_balance_score": round(stage_balance([attention, interest, desire, action]), 4),
        "aida_readiness_score": round(readiness, 4)
    }

def audit_messages(messages):
    rows, findings = [], []

    for message in messages:
        scores = score_message(message)
        status = "ready" if scores["aida_readiness_score"] >= THRESHOLD and scores["ethical_review_score"] >= ETHICAL_MINIMUM else "governance review"

        row = {
            "message_id": message["message_id"],
            "asset_name": message["asset_name"],
            "asset_type": message["asset_type"],
            "audience": message["audience"],
            **scores,
            "aida_status": status
        }
        rows.append(row)

        if scores["attention_score"] < 0.67:
            findings.append(Finding(
                "medium",
                "attention",
                message["message_id"],
                "Attention stage is weak or poorly supported.",
                "Clarify relevance, opening problem, and attention claim support."
            ))

        if scores["desire_score"] < 0.67:
            findings.append(Finding(
                "medium",
                "desire",
                message["message_id"],
                "Desire stage is underdeveloped.",
                "Strengthen value proposition, benefit support, and fit/limit language."
            ))

        if scores["action_score"] < 0.67:
            findings.append(Finding(
                "high",
                "action",
                message["message_id"],
                "Call to action is unclear, infeasible, or insufficiently transparent.",
                "Clarify next step, commitment level, and action expectations."
            ))

        if scores["ethical_review_score"] < ETHICAL_MINIMUM:
            findings.append(Finding(
                "high",
                "ethical_review",
                message["message_id"],
                "Ethical review score is below the minimum threshold.",
                "Remove false urgency, exaggerated claims, hidden conditions, or agency-reducing language."
            ))

        if status != "ready":
            findings.append(Finding(
                "medium",
                "aida_readiness",
                message["message_id"],
                f"AIDA readiness is {scores['aida_readiness_score']:.2f}.",
                "Review AIDA stage coverage and ethical-risk flags."
            ))

    return rows, findings

def stage_summary(rows):
    fields = ["attention_score", "interest_score", "desire_score", "action_score", "ethical_review_score", "stage_balance_score"]
    return [{"stage_or_metric": field, "average_score": round(average([float(row[field]) for row in rows]), 4)} for field in fields]

def audience_summary(rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["audience"]].append(float(row["aida_readiness_score"]))
    return [{"audience": audience, "asset_count": len(values), "average_aida_readiness": round(average(values), 4)} for audience, values in sorted(grouped.items())]

def main():
    for d in [TABLES, REPORTS, AUDIT_LOGS, CATALOG]:
        d.mkdir(parents=True, exist_ok=True)

    messages = read_csv(DATA / "aida_message_inventory.csv")
    manual_queue = read_csv(DATA / "editorial_review_queue.csv")

    readiness_rows, findings = audit_messages(messages)
    summary_rows = stage_summary(readiness_rows)
    audience_rows = audience_summary(readiness_rows)

    queue_rows = [
        {
            "source": "manual_review_queue",
            "severity": row["severity"],
            "category": row["issue_type"],
            "identifier": row["record_id"],
            "message": row["review_note"],
            "recommended_action": "Resolve through AIDA sequence governance."
        }
        for row in manual_queue
    ] + [asdict(finding) for finding in findings]

    catalog_rows = [{
        "series": "Content Frameworks",
        "article_slug": "aida-and-the-logic-of-persuasive-sequence",
        "message_id": row["message_id"],
        "asset_name": row["asset_name"],
        "asset_type": row["asset_type"],
        "audience": row["audience"],
        "aida_readiness_score": row["aida_readiness_score"],
        "aida_status": row["aida_status"],
        "github_path": "articles/aida-and-the-logic-of-persuasive-sequence/"
    } for row in readiness_rows]

    write_csv(TABLES / "aida_sequence_readiness_report.csv", readiness_rows)
    write_csv(TABLES / "aida_stage_summary_report.csv", summary_rows)
    write_csv(TABLES / "aida_audience_summary_report.csv", audience_rows)
    write_csv(TABLES / "aida_governance_queue.csv", queue_rows)
    write_csv(CATALOG / "aida_sequence_catalog_export.csv", catalog_rows)

    report = {
        "article": "AIDA and the Logic of Persuasive Sequence",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "messages": len(messages),
            "findings": len(findings),
            "governance_queue": len(queue_rows)
        },
        "stage_summary": summary_rows,
        "readiness": readiness_rows,
        "governance_queue": queue_rows
    }

    write_json(REPORTS / "aida_sequence_audit.json", report)
    write_json(AUDIT_LOGS / "aida_sequence_findings.json", [asdict(finding) for finding in findings])
    (REPORTS / "aida_sequence_audit.md").write_text("# AIDA Sequence Audit\n\nGenerated outputs are available in `outputs/`.\n", encoding="utf-8")

    print("AIDA sequence audit complete.")
    print(TABLES / "aida_sequence_readiness_report.csv")
    print(TABLES / "aida_governance_queue.csv")
    print(REPORTS / "aida_sequence_audit.json")

if __name__ == "__main__":
    main()
