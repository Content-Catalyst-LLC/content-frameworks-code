#!/usr/bin/env python3
"""Simple STP segment-priority model."""

from __future__ import annotations

from pathlib import Path
import csv

ARTICLE_ROOT = Path(__file__).resolve().parents[1]
SOURCE = ARTICLE_ROOT / "outputs" / "tables" / "stp_segment_targeting_audit.csv"
OUT = ARTICLE_ROOT / "outputs" / "tables" / "stp_primary_targets.csv"

with SOURCE.open("r", encoding="utf-8", newline="") as handle:
    rows = list(csv.DictReader(handle))

primary = [
    row for row in rows
    if float(row["weighted_target_score"]) >= 0.70
]

OUT.parent.mkdir(parents=True, exist_ok=True)

with OUT.open("w", encoding="utf-8", newline="") as handle:
    if primary:
        writer = csv.DictWriter(handle, fieldnames=list(primary[0].keys()))
        writer.writeheader()
        writer.writerows(primary)
    else:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()

print(f"Wrote {OUT}")
