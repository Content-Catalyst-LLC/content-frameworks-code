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

READINESS_THRESHOLD = 0.78
WEIGHTS = {
    "claim_support": 0.28,
    "method_clarity": 0.18,
    "uncertainty_visibility": 0.22,
    "audience_context": 0.17,
    "visual_accessibility": 0.15
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

def claim_support_report(claims, sources):
    source_by_id = {source["source_id"]: source for source in sources}
    rows = []
    findings = []

    for claim in claims:
        source = source_by_id.get(claim["source_id"], {})
        authority = source.get("authority_level", "missing")

        if authority == "high":
            support_score = 1.0
        elif authority == "medium":
            support_score = 0.75
        elif authority == "low":
            support_score = 0.50
        else:
            support_score = 0.0

        if not yes(claim["claim_supported"]):
            support_score = min(support_score, 0.35)

        rows.append({
            "claim_id": claim["claim_id"],
            "article_slug": claim["article_slug"],
            "claim_type": claim["claim_type"],
            "claim_strength": claim["claim_strength"],
            "source_id": claim["source_id"],
            "source_present": claim["source_id"] in source_by_id,
            "authority_level": authority,
            "source_review_status": source.get("review_status", "missing"),
            "claim_support_score": round(support_score, 4)
        })

        if claim["claim_strength"] in {"strong", "causal"} and support_score < 0.75:
            findings.append(Finding(
                "high",
                "claim_support",
                claim["claim_id"],
                "Strong or causal claim has insufficient source support.",
                "Review claim language, source quality, and evidence strength."
            ))

    return rows, findings

def article_readiness(articles, claim_rows):
    claims_by_article = defaultdict(list)
    for row in claim_rows:
        claims_by_article[row["article_slug"]].append(row)

    rows = []
    findings = []

    for article in articles:
        slug = article["article_slug"]
        scores = [float(row["claim_support_score"]) for row in claims_by_article.get(slug, [])]
        claim_support = sum(scores) / len(scores) if scores else 0.0

        method_clarity = 1.0 if yes(article["method_explained"]) else 0.0
        uncertainty = (
            int(yes(article["limitations_visible"])) +
            int(yes(article["uncertainty_visible"])) +
            int(yes(article["assumptions_visible"])) +
            int(yes(article["confidence_language_present"]))
        ) / 4

        audience = (
            int(yes(article["audience_defined"])) +
            int(yes(article["prior_knowledge_supported"])) +
            int(yes(article["plain_language_summary"])) +
            int(yes(article["implications_bounded"]))
        ) / 4

        visual = (
            int(yes(article["visuals_accessible"])) +
            int(yes(article["tables_explained"])) +
            int(yes(article["alt_text_present"]))
        ) / 3

        readiness = (
            WEIGHTS["claim_support"] * claim_support +
            WEIGHTS["method_clarity"] * method_clarity +
            WEIGHTS["uncertainty_visibility"] * uncertainty +
            WEIGHTS["audience_context"] * audience +
            WEIGHTS["visual_accessibility"] * visual
        )

        status = "ready" if readiness >= READINESS_THRESHOLD else "governance review"

        rows.append({
            "article_slug": slug,
            "title": article["title"],
            "status": article["status"],
            "research_domain": article["research_domain"],
            "audience": article["audience"],
            "claim_support_score": round(claim_support, 4),
            "method_clarity_score": round(method_clarity, 4),
            "uncertainty_visibility_score": round(uncertainty, 4),
            "audience_context_score": round(audience, 4),
            "visual_accessibility_score": round(visual, 4),
            "research_communication_readiness": round(readiness, 4),
            "readiness_status": status
        })

        if article["status"] == "published" and status != "ready":
            findings.append(Finding(
                "medium",
                "research_communication_readiness",
                slug,
                f"Research communication readiness is {readiness:.2f}.",
                "Review claim support, methods, uncertainty, audience context, and visual accessibility."
            ))

    return rows, findings

def main():
    for d in [TABLES, REPORTS, AUDIT_LOGS, CATALOG]:
        d.mkdir(parents=True, exist_ok=True)

    articles = read_csv(DATA / "research_communication_inventory.csv")
    claims = read_csv(DATA / "claim_inventory.csv")
    sources = read_csv(DATA / "source_inventory.csv")
    manual_queue = read_csv(DATA / "editorial_review_queue.csv")

    claim_rows, claim_findings = claim_support_report(claims, sources)
    readiness_rows, readiness_findings = article_readiness(articles, claim_rows)
    findings = claim_findings + readiness_findings

    source_summary = [{"summary_type": "source_type", "value": k, "count": v} for k, v in sorted(Counter(s["source_type"] for s in sources).items())]
    authority_summary = [{"summary_type": "authority_level", "value": k, "count": v} for k, v in sorted(Counter(s["authority_level"] for s in sources).items())]
    summary_rows = source_summary + authority_summary

    queue_rows = [
        {
            "source": "manual_review_queue",
            "severity": row["severity"],
            "category": row["issue_type"],
            "identifier": row["record_id"],
            "message": row["review_note"],
            "recommended_action": "Resolve through editorial research-communication review."
        }
        for row in manual_queue
    ] + [asdict(f) for f in findings]

    catalog_rows = [{
        "series": "Content Frameworks",
        "article_slug": row["article_slug"],
        "title": row["title"],
        "research_domain": row["research_domain"],
        "audience": row["audience"],
        "readiness_score": row["research_communication_readiness"],
        "readiness_status": row["readiness_status"],
        "github_path": f"articles/{row['article_slug']}/"
    } for row in readiness_rows]

    write_csv(TABLES / "claim_support_report.csv", claim_rows)
    write_csv(TABLES / "research_communication_readiness_report.csv", readiness_rows)
    write_csv(TABLES / "source_summary_report.csv", summary_rows)
    write_csv(TABLES / "research_communication_governance_queue.csv", queue_rows)
    write_csv(CATALOG / "research_communication_catalog_export.csv", catalog_rows)

    report = {
        "article": "Frameworks for Research Communication",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "articles": len(articles),
            "claims": len(claims),
            "sources": len(sources),
            "findings": len(findings),
            "governance_queue": len(queue_rows)
        },
        "readiness": readiness_rows,
        "governance_queue": queue_rows
    }

    write_json(REPORTS / "research_communication_audit.json", report)
    write_json(AUDIT_LOGS / "research_communication_findings.json", [asdict(f) for f in findings])
    (REPORTS / "research_communication_audit.md").write_text("# Frameworks for Research Communication Audit\n\nGenerated outputs are available in `outputs/`.\n", encoding="utf-8")

    print("Research communication audit complete.")
    print(TABLES / "research_communication_readiness_report.csv")
    print(TABLES / "research_communication_governance_queue.csv")
    print(REPORTS / "research_communication_audit.json")

if __name__ == "__main__":
    main()
