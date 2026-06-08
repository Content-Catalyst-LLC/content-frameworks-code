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

QUESTIONS = ["who", "what", "when", "where", "why", "how"]
THRESHOLD = 0.78
WEIGHTS = {
    "coverage": 0.24,
    "evidence_support": 0.26,
    "balance": 0.16,
    "audience_fit": 0.16,
    "governance": 0.18
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
    coverage_values = [int(yes(asset[f"{q}_answered"])) for q in QUESTIONS]
    support_values = [
        int(yes(asset[f"{q}_supported"]))
        for q in QUESTIONS
        if yes(asset[f"{q}_answered"])
    ]

    coverage = sum(coverage_values) / len(QUESTIONS)
    support = average(support_values) if support_values else 0.0
    balance = balance_score(coverage_values)

    audience_fit = (
        int(yes(asset["audience_context_present"])) +
        int(yes(asset["scope_note_present"])) +
        int(yes(asset["plain_language_summary_present"]))
    ) / 3

    governance = (
        int(yes(asset["review_owner_present"])) +
        int(yes(asset["last_review_date_present"])) +
        int(yes(asset["freshness_checked"])) +
        int(yes(asset["revision_queue_checked"]))
    ) / 4

    readiness = (
        WEIGHTS["coverage"] * coverage +
        WEIGHTS["evidence_support"] * support +
        WEIGHTS["balance"] * balance +
        WEIGHTS["audience_fit"] * audience_fit +
        WEIGHTS["governance"] * governance
    )

    return {
        "coverage_score": round(coverage, 4),
        "evidence_support_score": round(support, 4),
        "balance_score": round(balance, 4),
        "audience_fit_score": round(audience_fit, 4),
        "governance_score": round(governance, 4),
        "explanatory_readiness_score": round(readiness, 4)
    }

def audit_assets(assets):
    rows, findings = [], []

    for asset in assets:
        scores = score_asset(asset)
        status = "ready" if scores["explanatory_readiness_score"] >= THRESHOLD else "governance review"

        missing = [q for q in QUESTIONS if not yes(asset[f"{q}_answered"])]
        unsupported = [q for q in QUESTIONS if yes(asset[f"{q}_answered"]) and not yes(asset[f"{q}_supported"])]

        row = {
            "asset_id": asset["asset_id"],
            "asset_name": asset["asset_name"],
            "asset_type": asset["asset_type"],
            "audience": asset["audience"],
            **scores,
            "missing_questions": ";".join(missing),
            "unsupported_questions": ";".join(unsupported),
            "explanatory_status": status
        }
        rows.append(row)

        if missing:
            findings.append(Finding(
                "medium",
                "coverage",
                asset["asset_id"],
                f"Missing 5W1H questions: {', '.join(missing)}.",
                "Add answers or explicit scope notes for missing questions."
            ))

        if unsupported:
            findings.append(Finding(
                "high",
                "evidence_support",
                asset["asset_id"],
                f"Answered questions lack support: {', '.join(unsupported)}.",
                "Add evidence, examples, source records, or method notes."
            ))

        if scores["audience_fit_score"] < 0.67:
            findings.append(Finding(
                "medium",
                "audience_fit",
                asset["asset_id"],
                "Audience support is weak.",
                "Add audience context, scope note, or plain-language summary."
            ))

        if scores["governance_score"] < 0.75:
            findings.append(Finding(
                "medium",
                "governance",
                asset["asset_id"],
                "Governance readiness is incomplete.",
                "Add review owner, review date, freshness check, and revision queue status."
            ))

    return rows, findings

def question_coverage_summary(assets):
    rows = []
    for q in QUESTIONS:
        answered = sum(1 for asset in assets if yes(asset[f"{q}_answered"]))
        supported = sum(1 for asset in assets if yes(asset[f"{q}_answered"]) and yes(asset[f"{q}_supported"]))
        rows.append({
            "question": q,
            "assets_answered": answered,
            "assets_supported": supported,
            "answer_rate": round(answered / len(assets), 4) if assets else 0,
            "support_rate": round(supported / answered, 4) if answered else 0
        })
    return rows

def audience_summary(rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["audience"]].append(float(row["explanatory_readiness_score"]))
    return [{"audience": audience, "asset_count": len(values), "average_explanatory_readiness": round(average(values), 4)} for audience, values in sorted(grouped.items())]

def main():
    for d in [TABLES, REPORTS, AUDIT_LOGS, CATALOG]:
        d.mkdir(parents=True, exist_ok=True)

    assets = read_csv(DATA / "five_w_one_h_content_inventory.csv")
    manual_queue = read_csv(DATA / "editorial_review_queue.csv")

    readiness_rows, findings = audit_assets(assets)
    coverage_rows = question_coverage_summary(assets)
    audience_rows = audience_summary(readiness_rows)

    queue_rows = [
        {
            "source": "manual_review_queue",
            "severity": row["severity"],
            "category": row["issue_type"],
            "identifier": row["record_id"],
            "message": row["review_note"],
            "recommended_action": "Resolve through 5W1H explanatory-completeness governance."
        }
        for row in manual_queue
    ] + [asdict(finding) for finding in findings]

    catalog_rows = [{
        "series": "Content Frameworks",
        "article_slug": "5w1h-and-the-architecture-of-explanatory-completeness",
        "asset_id": row["asset_id"],
        "asset_name": row["asset_name"],
        "asset_type": row["asset_type"],
        "audience": row["audience"],
        "explanatory_readiness_score": row["explanatory_readiness_score"],
        "explanatory_status": row["explanatory_status"],
        "github_path": "articles/5w1h-and-the-architecture-of-explanatory-completeness/"
    } for row in readiness_rows]

    write_csv(TABLES / "five_w_one_h_readiness_report.csv", readiness_rows)
    write_csv(TABLES / "five_w_one_h_question_coverage_report.csv", coverage_rows)
    write_csv(TABLES / "five_w_one_h_audience_summary_report.csv", audience_rows)
    write_csv(TABLES / "five_w_one_h_governance_queue.csv", queue_rows)
    write_csv(CATALOG / "five_w_one_h_catalog_export.csv", catalog_rows)

    report = {
        "article": "5W1H and the Architecture of Explanatory Completeness",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "assets": len(assets),
            "findings": len(findings),
            "governance_queue": len(queue_rows)
        },
        "question_coverage": coverage_rows,
        "readiness": readiness_rows,
        "governance_queue": queue_rows
    }

    write_json(REPORTS / "five_w_one_h_completeness_audit.json", report)
    write_json(AUDIT_LOGS / "five_w_one_h_findings.json", [asdict(finding) for finding in findings])
    (REPORTS / "five_w_one_h_completeness_audit.md").write_text("# 5W1H Completeness Audit\n\nGenerated outputs are available in `outputs/`.\n", encoding="utf-8")

    print("5W1H completeness audit complete.")
    print(TABLES / "five_w_one_h_readiness_report.csv")
    print(TABLES / "five_w_one_h_governance_queue.csv")
    print(REPORTS / "five_w_one_h_completeness_audit.json")

if __name__ == "__main__":
    main()
