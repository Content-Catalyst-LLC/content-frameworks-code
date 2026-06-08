#!/usr/bin/env python3
"""
Value Proposition Canvas relevance audit.

This workflow scores audience-job alignment, pain-relief alignment, gain-creation
alignment, evidence strength, communication clarity, and ethical fit. Scores are
editorial diagnostics, not objective proof.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "value_relevance_inventory.csv"
CONFIG = ROOT / "config" / "value_relevance_config.json"
OUT_TABLES = ROOT / "outputs" / "tables"
OUT_REPORTS = ROOT / "outputs" / "reports"
OUT_LOGS = ROOT / "outputs" / "audit_logs"
OUT_EXPORTS = ROOT / "outputs" / "catalog_exports"


@dataclass
class ValueRelevanceItem:
    item_id: str
    title: str
    audience_segment: str
    status: str
    job_alignment: float
    pain_relief_alignment: float
    gain_creation_alignment: float
    evidence_strength: float
    communication_clarity: float
    ethical_fit: float
    primary_risk: str

    def score(self) -> float:
        return mean([
            self.job_alignment,
            self.pain_relief_alignment,
            self.gain_creation_alignment,
            self.evidence_strength,
            self.communication_clarity,
            self.ethical_fit,
        ])

    def weakest_dimension(self) -> str:
        dimensions = {
            "job_alignment": self.job_alignment,
            "pain_relief_alignment": self.pain_relief_alignment,
            "gain_creation_alignment": self.gain_creation_alignment,
            "evidence_strength": self.evidence_strength,
            "communication_clarity": self.communication_clarity,
            "ethical_fit": self.ethical_fit,
        }
        return min(dimensions, key=dimensions.get)


def classify(score: float, threshold: float) -> str:
    if score >= 0.88:
        return "strong relevance"
    if score >= threshold:
        return "publishable with review"
    if score >= 0.60:
        return "revise before publication"
    return "major relevance gap"


def load_items() -> list[ValueRelevanceItem]:
    with DATA.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [
            ValueRelevanceItem(
                item_id=row["item_id"],
                title=row["title"],
                audience_segment=row["audience_segment"],
                status=row["status"],
                job_alignment=float(row["job_alignment"]),
                pain_relief_alignment=float(row["pain_relief_alignment"]),
                gain_creation_alignment=float(row["gain_creation_alignment"]),
                evidence_strength=float(row["evidence_strength"]),
                communication_clarity=float(row["communication_clarity"]),
                ethical_fit=float(row["ethical_fit"]),
                primary_risk=row["primary_risk"],
            )
            for row in reader
        ]


def main() -> None:
    for directory in (OUT_TABLES, OUT_REPORTS, OUT_LOGS, OUT_EXPORTS):
        directory.mkdir(parents=True, exist_ok=True)

    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    threshold = float(config["readiness_threshold"])
    items = load_items()

    scored_rows = []
    for item in items:
        score = item.score()
        scored_rows.append({
            "item_id": item.item_id,
            "title": item.title,
            "audience_segment": item.audience_segment,
            "status": item.status,
            "relevance_score": f"{score:.3f}",
            "classification": classify(score, threshold),
            "weakest_dimension": item.weakest_dimension(),
            "primary_risk": item.primary_risk,
        })

    report_path = OUT_TABLES / "python_value_relevance_scores.csv"
    with report_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(scored_rows[0].keys()))
        writer.writeheader()
        writer.writerows(scored_rows)

    summary = {
        "article": config["article"],
        "items_reviewed": len(items),
        "average_relevance_score": round(mean(item.score() for item in items), 3),
        "items_below_threshold": [item.item_id for item in items if item.score() < threshold],
        "highest_risk_items": [item.item_id for item in items if item.primary_risk != "none"],
    }

    (OUT_REPORTS / "python_value_relevance_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    log_lines = ["Value Proposition Canvas relevance audit", "=" * 60]
    for row in scored_rows:
        log_lines.append(
            f"{row['item_id']} | {row['classification']} | "
            f"score={row['relevance_score']} | weakest={row['weakest_dimension']}"
        )
    (OUT_LOGS / "python_value_relevance_audit.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    catalog = [
        {
            "slug": "value-proposition-canvas-and-the-communication-of-relevance",
            "series": "Content Frameworks",
            "workflow": "value-relevance-audit",
            "output": str(report_path.relative_to(ROOT)),
        }
    ]
    (OUT_EXPORTS / "value_relevance_catalog.json").write_text(json.dumps(catalog, indent=2), encoding="utf-8")

    print(f"Wrote {report_path}")
    print(f"Average relevance score: {summary['average_relevance_score']}")


if __name__ == "__main__":
    main()
