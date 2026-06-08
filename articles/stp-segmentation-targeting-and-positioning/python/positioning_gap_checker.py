#!/usr/bin/env python3
"""Identify segments with high positioning gaps."""

from __future__ import annotations

from pathlib import Path
import csv

ARTICLE_ROOT = Path(__file__).resolve().parents[1]
SOURCE = ARTICLE_ROOT / "outputs" / "tables" / "stp_segment_targeting_audit.csv"
OUT = ARTICLE_ROOT / "outputs" / "tables" / "stp_high_positioning_gaps.csv"

with SOURCE.open("r", encoding="utf-8", newline="") as handle:
    rows = list(csv.DictReader(handle))

gaps = [
    row for row in rows
    if float(row["positioning_gap"]) >= 0.10
]

OUT.parent.mkdir(parents=True, exist_ok=True)

with OUT.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(gaps)

print(f"Wrote {OUT}")
