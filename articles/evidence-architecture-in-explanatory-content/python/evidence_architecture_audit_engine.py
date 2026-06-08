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
    "claim_support": 0.30,
    "source_quality": 0.20,
    "uncertainty_visibility": 0.20,
    "visual_support": 0.12,
    "review_readiness": 0.18
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

def source_quality(source):
    authority = source.get("authority_level", "missing")
    if authority == "high":
        return 1.0
    if authority == "medium":
        return 0.75
    if authority == "low":
        return 0.45
    return 0.0

def claim_support_audit(claims, sources):
    source_by_id = {source["source_id"]: source for source in sources}
    rows, findings = [], []

    for claim in claims:
        source = source_by_id.get(claim["source_id"])
        quality = source_quality(source or {})
        support_factor = 1.0 if yes(claim["direct_support"]) else 0.45
        score = quality * support_factor if source else 0.0

        row = {
            "claim_id": claim["claim_id"],
            "article_slug": claim["article_slug"],
            "claim_type": claim["claim_type"],
            "claim_strength": claim["claim_strength"],
            "source_id": claim["source_id"],
            "source_present": source is not None,
            "source_type": source["source_type"] if source else "missing",
            "authority_level": source["authority_level"] if source else "missing",
            "direct_support": yes(claim["direct_support"]),
            "claim_support_score": round(score, 4)
        }
        rows.append(row)

        if claim["claim_strength"] in {"strong", "causal"} and score < 0.75:
            findings.append(Finding(
                "high",
                "claim_support",
                claim["claim_id"],
                "Strong or causal claim has insufficient support.",
                "Review claim language, source authority, and evidence type."
            ))

    return rows, findings

def article_readiness(articles, claim_rows, visuals):
    claims_by_article = defaultdict(list)
    visuals_by_article = defaultdict(list)

    for row in claim_rows:
        claims_by_article[row["article_slug"]].append(row)

    for visual in visuals:
        visuals_by_article[visual["article_slug"]].append(visual)

    rows, findings = [], []

    for article in articles:
        slug = article["article_slug"]
        claims = claims_by_article.get(slug, [])
        article_visuals = visuals_by_article.get(slug, [])

        claim_support = sum(float(row["claim_support_score"]) for row in claims) / len(claims) if claims else 0.0

        source_quality_score = sum(
            1.0 if row["authority_level"] == "high" else 0.75 if row["authority_level"] == "medium" else 0.45 if row["authority_level"] == "low" else 0.0
            for row in claims
        ) / len(claims) if claims else 0.0

        uncertainty = (
            int(yes(article["limitations_visible"])) +
            int(yes(article["uncertainty_visible"])) +
            int(yes(article["assumptions_visible"])) +
            int(yes(article["confidence_language_present"]))
        ) / 4

        if article_visuals:
            visual_support = sum(
                (
                    int(yes(visual["source_visible"])) +
                    int(yes(visual["caption_explains_claim"])) +
                    int(yes(visual["alt_text_present"])) +
                    int(yes(visual["visual_limitations_visible"]))
                ) / 4
                for visual in article_visuals
            ) / len(article_visuals)
        else:
            visual_support = 1.0

        review = (
            int(yes(article["source_review_complete"])) +
            int(yes(article["last_review_date_present"])) +
            int(yes(article["revision_queue_checked"]))
        ) / 3

        readiness = (
            WEIGHTS["claim_support"] * claim_support +
            WEIGHTS["source_quality"] * source_quality_score +
            WEIGHTS["uncertainty_visibility"] * uncertainty +
            WEIGHTS["visual_support"] * visual_support +
            WEIGHTS["review_readiness"] * review
        )

        status = "ready" if readiness >= THRESHOLD else "governance review"

        rows.append({
            "article_slug": slug,
            "title": article["title"],
            "status": article["status"],
            "claim_support_score": round(claim_support, 4),
            "source_quality_score": round(source_quality_score, 4),
            "uncertainty_visibility_score": round(uncertainty, 4),
            "visual_support_score": round(visual_support, 4),
            "review_readiness_score": round(review, 4),
            "evidence_architecture_readiness": round(readiness, 4),
            "evidence_architecture_status": status
        })

        if article["status"] == "published" and status != "ready":
            findings.append(Finding(
                "medium",
                "evidence_architecture_readiness",
                slug,
                f"Evidence architecture readiness is {readiness:.2f}.",
                "Review claim support, source quality, uncertainty, visual evidence, and review readiness."
            ))

    return rows, findings

def main():
    for d in [TABLES, REPORTS, AUDIT_LOGS, CATALOG]:
        d.mkdir(parents=True, exist_ok=True)

    articles = read_csv(DATA / "evidence_architecture_inventory.csv")
    claims = read_csv(DATA / "claim_inventory.csv")
    sources = read_csv(DATA / "source_inventory.csv")
    visuals = read_csv(DATA / "visual_evidence_inventory.csv")
    manual_queue = read_csv(DATA / "editorial_review_queue.csv")

    claim_rows, claim_findings = claim_support_audit(claims, sources)
    readiness_rows, readiness_findings = article_readiness(articles, claim_rows, visuals)
    findings = claim_findings + readiness_findings

    summary_rows = (
        [{"summary_type": "source_type", "value": k, "count": v} for k, v in sorted(Counter(s["source_type"] for s in sources).items())] +
        [{"summary_type": "authority_level", "value": k, "count": v} for k, v in sorted(Counter(s["authority_level"] for s in sources).items())]
    )

    queue_rows = [
        {
            "source": "manual_review_queue",
            "severity": row["severity"],
            "category": row["issue_type"],
            "identifier": row["record_id"],
            "message": row["review_note"],
            "recommended_action": "Resolve through evidence architecture governance."
        }
        for row in manual_queue
    ] + [asdict(finding) for finding in findings]

    catalog_rows = [{
        "series": "Content Frameworks",
        "article_slug": row["article_slug"],
        "title": row["title"],
        "evidence_architecture_readiness": row["evidence_architecture_readiness"],
        "evidence_architecture_status": row["evidence_architecture_status"],
        "github_path": f"articles/{row['article_slug']}/"
    } for row in readiness_rows]

    write_csv(TABLES / "claim_support_report.csv", claim_rows)
    write_csv(TABLES / "evidence_architecture_readiness_report.csv", readiness_rows)
    write_csv(TABLES / "evidence_type_summary_report.csv", summary_rows)
    write_csv(TABLES / "evidence_architecture_governance_queue.csv", queue_rows)
    write_csv(CATALOG / "evidence_architecture_catalog_export.csv", catalog_rows)

    report = {
        "article": "Evidence Architecture in Explanatory Content",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "articles": len(articles),
            "claims": len(claims),
            "sources": len(sources),
            "visuals": len(visuals),
            "findings": len(findings),
            "governance_queue": len(queue_rows)
        },
        "readiness": readiness_rows,
        "governance_queue": queue_rows
    }

    write_json(REPORTS / "evidence_architecture_audit.json", report)
    write_json(AUDIT_LOGS / "evidence_architecture_findings.json", [asdict(finding) for finding in findings])
    (REPORTS / "evidence_architecture_audit.md").write_text("# Evidence Architecture Audit\n\nGenerated outputs are available in `outputs/`.\n", encoding="utf-8")

    print("Evidence architecture audit complete.")
    print(TABLES / "evidence_architecture_readiness_report.csv")
    print(TABLES / "evidence_architecture_governance_queue.csv")
    print(REPORTS / "evidence_architecture_audit.json")

if __name__ == "__main__":
    main()
