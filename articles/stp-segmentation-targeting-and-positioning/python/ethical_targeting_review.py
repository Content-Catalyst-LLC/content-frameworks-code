#!/usr/bin/env python3
"""Export STP rows needing ethical targeting review."""

from __future__ import annotations

from pathlib import Path
import csv

ARTICLE_ROOT = Path(__file__).resolve().parents[1]
SOURCE = ARTICLE_ROOT / "outputs" / "tables" / "stp_segment_targeting_audit.csv"
OUT = ARTICLE_ROOT / "outputs" / "tables" / "stp_ethical_review_flags.csv"

with SOURCE.open("r", encoding="utf-8", newline="") as handle:
    rows = list(csv.DictReader(handle))

flagged = [
    row for row in rows
    if row["ethical_review_flag"] != "standard review"
]

OUT.parent.mkdir(parents=True, exist_ok=True)

with OUT.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(flagged)

print(f"Wrote {OUT}")
