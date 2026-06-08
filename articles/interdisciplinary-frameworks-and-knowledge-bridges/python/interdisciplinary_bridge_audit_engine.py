#!/usr/bin/env python3
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import Counter, defaultdict
from datetime import datetime, timezone
import csv, json

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
TABLES = ROOT / "outputs" / "tables"
REPORTS = ROOT / "outputs" / "reports"
AUDIT_LOGS = ROOT / "outputs" / "audit_logs"
CATALOG = ROOT / "outputs" / "catalog_exports"

THRESHOLD = 0.78
WEIGHTS = {
    "translation_alignment": 0.22,
    "evidence_compatibility": 0.24,
    "method_transparency": 0.18,
    "audience_support": 0.18,
    "governance_readiness": 0.18
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

def bridge_translation_report(bridges, vocabulary):
    vocab_by_bridge = defaultdict(list)
    for term in vocabulary:
        vocab_by_bridge[term["bridge_id"]].append(term)

    rows, findings = [], []
    for bridge in bridges:
        bridge_id = bridge["bridge_id"]
        terms = vocab_by_bridge.get(bridge_id, [])
        shared = [term for term in terms if yes(term["shared_term"])]
        aligned = [
            term for term in shared
            if yes(term["source_definition_present"]) and yes(term["target_definition_present"]) and yes(term["translation_note_present"])
        ]
        score = len(aligned) / len(shared) if shared else 1.0

        rows.append({
            "bridge_id": bridge_id,
            "bridge_title": bridge["bridge_title"],
            "source_domain": bridge["source_domain"],
            "target_domain": bridge["target_domain"],
            "shared_terms": len(shared),
            "aligned_terms": len(aligned),
            "translation_alignment_score": round(score, 4)
        })

        if score < 0.75:
            findings.append(Finding(
                "medium",
                "translation_alignment",
                bridge_id,
                f"Translation alignment is {score:.0%}.",
                "Add source definitions, target definitions, and translation notes."
            ))
    return rows, findings

def evidence_compatibility_report(bridges, evidence_links):
    links_by_bridge = defaultdict(list)
    for link in evidence_links:
        links_by_bridge[link["bridge_id"]].append(link)

    rows, findings = [], []
    for bridge in bridges:
        bridge_id = bridge["bridge_id"]
        links = links_by_bridge.get(bridge_id, [])
        compatible = [
            link for link in links
            if yes(link["evidence_type_classified"]) and yes(link["method_fit_explained"]) and yes(link["limitation_visible"])
        ]
        score = len(compatible) / len(links) if links else 0.0

        rows.append({
            "bridge_id": bridge_id,
            "bridge_title": bridge["bridge_title"],
            "evidence_links": len(links),
            "compatible_evidence_links": len(compatible),
            "evidence_compatibility_score": round(score, 4)
        })

        if score < 0.75:
            findings.append(Finding(
                "high",
                "evidence_compatibility",
                bridge_id,
                f"Evidence compatibility is {score:.0%}.",
                "Classify evidence type, explain method fit, and add limitation notes."
            ))
    return rows, findings

def bridge_readiness(bridges, translation_rows, evidence_rows):
    translation = {row["bridge_id"]: row for row in translation_rows}
    evidence = {row["bridge_id"]: row for row in evidence_rows}

    rows, findings = [], []
    for bridge in bridges:
        bridge_id = bridge["bridge_id"]
        translation_score = float(translation[bridge_id]["translation_alignment_score"])
        evidence_score = float(evidence[bridge_id]["evidence_compatibility_score"])

        method = (
            int(yes(bridge["source_method_visible"])) +
            int(yes(bridge["target_method_visible"])) +
            int(yes(bridge["assumptions_visible"]))
        ) / 3

        audience = (
            int(yes(bridge["audience_context_present"])) +
            int(yes(bridge["plain_language_bridge_summary"])) +
            int(yes(bridge["example_present"])) +
            int(yes(bridge["misuse_warning_present"]))
        ) / 4

        governance = (
            int(yes(bridge["review_owner_present"])) +
            int(yes(bridge["last_review_date_present"])) +
            int(yes(bridge["revision_queue_checked"]))
        ) / 3

        readiness = (
            WEIGHTS["translation_alignment"] * translation_score +
            WEIGHTS["evidence_compatibility"] * evidence_score +
            WEIGHTS["method_transparency"] * method +
            WEIGHTS["audience_support"] * audience +
            WEIGHTS["governance_readiness"] * governance
        )

        status = "ready" if readiness >= THRESHOLD else "governance review"

        rows.append({
            "bridge_id": bridge_id,
            "bridge_title": bridge["bridge_title"],
            "bridge_type": bridge["bridge_type"],
            "source_domain": bridge["source_domain"],
            "target_domain": bridge["target_domain"],
            "translation_alignment_score": round(translation_score, 4),
            "evidence_compatibility_score": round(evidence_score, 4),
            "method_transparency_score": round(method, 4),
            "audience_support_score": round(audience, 4),
            "governance_readiness_score": round(governance, 4),
            "interdisciplinary_bridge_readiness": round(readiness, 4),
            "bridge_status": status
        })

        if status != "ready":
            findings.append(Finding(
                "medium",
                "bridge_readiness",
                bridge_id,
                f"Interdisciplinary bridge readiness is {readiness:.2f}.",
                "Review translation, evidence compatibility, method transparency, audience support, and governance."
            ))
    return rows, findings

def domain_balance(bridges):
    counts = Counter()
    for bridge in bridges:
        counts[bridge["source_domain"]] += 1
        counts[bridge["target_domain"]] += 1
    return [{"domain": domain, "bridge_count": count} for domain, count in sorted(counts.items())]

def main():
    for d in [TABLES, REPORTS, AUDIT_LOGS, CATALOG]:
        d.mkdir(parents=True, exist_ok=True)

    bridges = read_csv(DATA / "knowledge_bridge_inventory.csv")
    vocabulary = read_csv(DATA / "vocabulary_alignment.csv")
    evidence_links = read_csv(DATA / "evidence_compatibility.csv")
    manual_queue = read_csv(DATA / "editorial_review_queue.csv")

    translation_rows, translation_findings = bridge_translation_report(bridges, vocabulary)
    evidence_rows, evidence_findings = evidence_compatibility_report(bridges, evidence_links)
    readiness_rows, readiness_findings = bridge_readiness(bridges, translation_rows, evidence_rows)
    domain_rows = domain_balance(bridges)

    findings = translation_findings + evidence_findings + readiness_findings

    queue_rows = [
        {
            "source": "manual_review_queue",
            "severity": row["severity"],
            "category": row["issue_type"],
            "identifier": row["record_id"],
            "message": row["review_note"],
            "recommended_action": "Resolve through interdisciplinary bridge governance."
        }
        for row in manual_queue
    ] + [asdict(finding) for finding in findings]

    catalog_rows = [{
        "series": "Content Frameworks",
        "bridge_id": row["bridge_id"],
        "bridge_title": row["bridge_title"],
        "source_domain": row["source_domain"],
        "target_domain": row["target_domain"],
        "interdisciplinary_bridge_readiness": row["interdisciplinary_bridge_readiness"],
        "bridge_status": row["bridge_status"],
        "article_slug": "interdisciplinary-frameworks-and-knowledge-bridges",
        "github_path": "articles/interdisciplinary-frameworks-and-knowledge-bridges/"
    } for row in readiness_rows]

    write_csv(TABLES / "translation_alignment_report.csv", translation_rows)
    write_csv(TABLES / "evidence_compatibility_report.csv", evidence_rows)
    write_csv(TABLES / "interdisciplinary_bridge_readiness_report.csv", readiness_rows)
    write_csv(TABLES / "domain_balance_report.csv", domain_rows)
    write_csv(TABLES / "interdisciplinary_governance_queue.csv", queue_rows)
    write_csv(CATALOG / "interdisciplinary_bridge_catalog_export.csv", catalog_rows)

    report = {
        "article": "Interdisciplinary Frameworks and Knowledge Bridges",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "bridges": len(bridges),
            "vocabulary_records": len(vocabulary),
            "evidence_links": len(evidence_links),
            "findings": len(findings),
            "governance_queue": len(queue_rows)
        },
        "readiness": readiness_rows,
        "governance_queue": queue_rows
    }

    write_json(REPORTS / "interdisciplinary_bridge_audit.json", report)
    write_json(AUDIT_LOGS / "interdisciplinary_bridge_findings.json", [asdict(finding) for finding in findings])
    (REPORTS / "interdisciplinary_bridge_audit.md").write_text("# Interdisciplinary Bridge Audit\n\nGenerated outputs are available in `outputs/`.\n", encoding="utf-8")

    print("Interdisciplinary bridge audit complete.")
    print(TABLES / "interdisciplinary_bridge_readiness_report.csv")
    print(TABLES / "interdisciplinary_governance_queue.csv")
    print(REPORTS / "interdisciplinary_bridge_audit.json")

if __name__ == "__main__":
    main()
