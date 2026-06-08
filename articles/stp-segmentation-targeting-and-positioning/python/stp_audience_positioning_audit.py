#!/usr/bin/env python3
"""
STP audience and positioning audit.

This dependency-light workflow evaluates:
- segment target priority
- weighted targeting score
- positioning strength
- positioning gaps
- stereotype and exclusion review flags

It uses only the Python standard library.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
from statistics import mean


ARTICLE_ROOT = Path(__file__).resolve().parents[1]
DATA = ARTICLE_ROOT / "data"
TABLES = ARTICLE_ROOT / "outputs" / "tables"


@dataclass
class SegmentProfile:
    segment: str
    need_intensity: float
    strategic_fit: float
    reachability: float
    evidence_fit: float
    ethical_responsibility: float
    category_clarity: float
    audience_relevance: float
    differentiation: float
    credibility: float
    stereotype_risk: float
    exclusion_risk: float

    def target_score(self) -> float:
        return mean([
            self.need_intensity,
            self.strategic_fit,
            self.reachability,
            self.evidence_fit,
            self.ethical_responsibility,
        ])

    def weighted_target_score(self) -> float:
        return (
            self.need_intensity * 0.25
            + self.strategic_fit * 0.20
            + self.reachability * 0.15
            + self.evidence_fit * 0.20
            + self.ethical_responsibility * 0.20
        )

    def positioning_score(self) -> float:
        return mean([
            self.category_clarity,
            self.audience_relevance,
            self.differentiation,
            self.evidence_fit,
            self.credibility,
        ])

    def positioning_gap(self) -> float:
        return max(0.0, self.need_intensity - self.positioning_score())

    def ethical_review_flag(self) -> str:
        if self.stereotype_risk >= 0.70 or self.exclusion_risk >= 0.70:
            return "high ethical review"
        if self.stereotype_risk >= 0.50 or self.exclusion_risk >= 0.50:
            return "moderate ethical review"
        return "standard review"


def classify_priority(score: float) -> str:
    if score >= 0.85:
        return "primary target candidate"
    if score >= 0.70:
        return "strong secondary target"
    if score >= 0.55:
        return "monitor or support with lighter pathway"
    return "low current fit"


def read_segments(path: Path) -> list[SegmentProfile]:
    profiles: list[SegmentProfile] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            profiles.append(
                SegmentProfile(
                    segment=row["segment"],
                    need_intensity=float(row["need_intensity"]),
                    strategic_fit=float(row["strategic_fit"]),
                    reachability=float(row["reachability"]),
                    evidence_fit=float(row["evidence_fit"]),
                    ethical_responsibility=float(row["ethical_responsibility"]),
                    category_clarity=float(row["category_clarity"]),
                    audience_relevance=float(row["audience_relevance"]),
                    differentiation=float(row["differentiation"]),
                    credibility=float(row["credibility"]),
                    stereotype_risk=float(row["stereotype_risk"]),
                    exclusion_risk=float(row["exclusion_risk"]),
                )
            )
    return profiles


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"No rows to write: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    profiles = read_segments(DATA / "stp_segments.csv")
    rows: list[dict[str, object]] = []

    for profile in profiles:
        target = profile.target_score()
        weighted = profile.weighted_target_score()
        positioning = profile.positioning_score()
        gap = profile.positioning_gap()

        rows.append({
            "segment": profile.segment,
            "need_intensity": profile.need_intensity,
            "strategic_fit": profile.strategic_fit,
            "reachability": profile.reachability,
            "evidence_fit": profile.evidence_fit,
            "ethical_responsibility": profile.ethical_responsibility,
            "target_score": round(target, 3),
            "weighted_target_score": round(weighted, 3),
            "target_classification": classify_priority(weighted),
            "category_clarity": profile.category_clarity,
            "audience_relevance": profile.audience_relevance,
            "differentiation": profile.differentiation,
            "credibility": profile.credibility,
            "positioning_score": round(positioning, 3),
            "positioning_gap": round(gap, 3),
            "stereotype_risk": profile.stereotype_risk,
            "exclusion_risk": profile.exclusion_risk,
            "ethical_review_flag": profile.ethical_review_flag(),
        })

    rows = sorted(rows, key=lambda row: row["weighted_target_score"], reverse=True)

    write_csv(TABLES / "stp_segment_targeting_audit.csv", rows)

    revision_rows = [
        row for row in rows
        if float(row["positioning_gap"]) >= 0.15 or row["ethical_review_flag"] != "standard review"
    ]
    write_csv(TABLES / "stp_positioning_revision_queue.csv", revision_rows)

    print("STP audience and positioning audit complete.")
    print(TABLES / "stp_segment_targeting_audit.csv")
    print(TABLES / "stp_positioning_revision_queue.csv")


if __name__ == "__main__":
    main()
