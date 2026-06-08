#!/usr/bin/env python3
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timezone
import csv, json

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "outputs"
TABLES = OUT / "tables"
REPORTS = OUT / "reports"
AUDIT_LOGS = OUT / "audit_logs"
CATALOG = OUT / "catalog_exports"

REQUIRED = {
    "linear": {"communicator", "message", "channel", "audience", "noise"},
    "interactional": {"communicator", "message", "channel", "audience", "noise", "feedback"},
    "transactional": {"communicator", "message", "audience", "context", "feedback", "interpretation"},
    "systems": {"communicator", "message", "audience", "context", "feedback", "institutions", "power", "platform"},
    "evidence": {"claim", "evidence", "method", "uncertainty", "limitation", "implication", "audience"},
    "learning": {"orientation", "sequence", "prerequisites", "examples", "feedback", "transfer"},
}

def yes(x):
    return str(x).strip().lower() in {"yes", "true", "1", "ready", "complete"}

def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

def main():
    for d in [TABLES, REPORTS, AUDIT_LOGS, CATALOG]:
        d.mkdir(parents=True, exist_ok=True)

    models = read_csv(DATA / "communication_model_inventory.csv")
    elements = read_csv(DATA / "model_elements.csv")
    relationships = read_csv(DATA / "model_relationships.csv")
    review_queue = read_csv(DATA / "editorial_review_queue.csv")

    present = defaultdict(set)
    for e in elements:
        if yes(e["present"]):
            present[e["model_id"]].add(e["element"])

    relationship_count = Counter(r["model_id"] for r in relationships if yes(r["active"]))

    rows = []
    findings = []

    for m in models:
        model_id = m["model_id"]
        required = REQUIRED.get(m["model_type"], set())
        element_score = len(required & present[model_id]) / len(required) if required else 1.0

        rc = relationship_count[model_id]
        relationship_score = 1.0 if rc >= 5 else 0.75 if rc >= 3 else 0.45 if rc >= 1 else 0.0

        audience_score = (
            int(yes(m["audience_visible"])) +
            int(yes(m["context_visible"])) +
            int(yes(m["interpretation_visible"])) +
            int(yes(m["power_visible"]))
        ) / 4

        feedback_score = 1.0 if yes(m["feedback_visible"]) else 0.0

        evidence_score = (
            int(yes(m["evidence_visible"])) +
            int(yes(m["limitations_visible"])) +
            int(yes(m["assumptions_visible"]))
        ) / 3

        domain_score = 1.0 if m["domain_fit"] == "high" else 0.65 if m["domain_fit"] == "medium" else 0.30
        penalty = 0.25 if m["abstraction_risk"] == "high" else 0.10 if m["abstraction_risk"] == "medium" else 0.0

        readiness = max(0, min(1, (
            0.25 * element_score +
            0.15 * relationship_score +
            0.20 * audience_score +
            0.15 * feedback_score +
            0.15 * evidence_score +
            0.10 * domain_score -
            penalty
        )))

        status = "ready" if readiness >= 0.78 else "governance review"

        row = {
            "model_id": model_id,
            "model_name": m["model_name"],
            "model_type": m["model_type"],
            "status": m["status"],
            "primary_domain": m["primary_domain"],
            "element_score": round(element_score, 4),
            "relationship_score": round(relationship_score, 4),
            "audience_context_score": round(audience_score, 4),
            "feedback_score": round(feedback_score, 4),
            "evidence_limitations_score": round(evidence_score, 4),
            "domain_fit_score": round(domain_score, 4),
            "risk_penalty": round(penalty, 4),
            "model_readiness_score": round(readiness, 4),
            "model_readiness_status": status
        }
        rows.append(row)

        if m["status"] == "published" and status != "ready":
            findings.append({
                "severity": "medium",
                "category": "model_readiness",
                "identifier": model_id,
                "message": f"{m['model_name']} needs governance review.",
                "recommended_action": "Review elements, relationships, audience/context, feedback, evidence, limitations, domain fit, and abstraction risk."
            })

    type_summary = [{"model_type": k, "model_count": v} for k, v in sorted(Counter(m["model_type"] for m in models).items())]
    risk_summary = [{"abstraction_risk": k, "model_count": v} for k, v in sorted(Counter(m["abstraction_risk"] for m in models).items())]
    queue = [
        {
            "source": "manual_review_queue",
            "severity": q["severity"],
            "category": q["issue_type"],
            "identifier": q["model_id"],
            "message": q["review_note"]
        }
        for q in review_queue
    ] + findings

    catalog = [
        {
            "series": "Content Frameworks",
            "article": "Conceptual Models in Communication",
            "model_id": r["model_id"],
            "model_name": r["model_name"],
            "model_type": r["model_type"],
            "model_readiness_score": r["model_readiness_score"],
            "model_readiness_status": r["model_readiness_status"],
            "github_path": "articles/conceptual-models-in-communication/"
        }
        for r in rows
    ]

    write_csv(TABLES / "model_readiness_report.csv", rows)
    write_csv(TABLES / "model_type_summary.csv", type_summary)
    write_csv(TABLES / "abstraction_risk_summary.csv", risk_summary)
    write_csv(TABLES / "communication_model_governance_queue.csv", queue)
    write_csv(CATALOG / "conceptual_models_communication_catalog_export.csv", catalog)

    report = {
        "article": "Conceptual Models in Communication",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "counts": {"models": len(models), "findings": len(findings), "queue_items": len(queue)},
        "model_readiness": rows,
        "governance_queue": queue
    }
    write_json(REPORTS / "communication_model_audit.json", report)
    write_json(AUDIT_LOGS / "communication_model_audit_findings.json", findings)
    (REPORTS / "communication_model_audit.md").write_text("# Conceptual Models in Communication Audit\n\nGenerated outputs are available in `outputs/`.\n", encoding="utf-8")

    print("Communication model audit complete.")
    print(TABLES / "model_readiness_report.csv")
    print(TABLES / "communication_model_governance_queue.csv")
    print(REPORTS / "communication_model_audit.json")

if __name__ == "__main__":
    main()
