#!/usr/bin/env python3
from pathlib import Path
import csv
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
TABLES = ROOT / "outputs" / "tables"

def main():
    with (DATA / "internal_links.csv").open(newline="", encoding="utf-8") as f:
        links = list(csv.DictReader(f))

    outgoing = Counter(row["source_slug"] for row in links)
    incoming = Counter(row["target_slug"] for row in links)
    slugs = sorted(set(outgoing) | set(incoming))

    rows = [{
        "slug": slug,
        "outgoing_links": outgoing[slug],
        "incoming_links": incoming[slug],
        "total_link_degree": outgoing[slug] + incoming[slug]
    } for slug in slugs]

    TABLES.mkdir(parents=True, exist_ok=True)
    with (TABLES / "internal_link_diagnostics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print("Internal-link diagnostics complete.")

if __name__ == "__main__":
    main()
