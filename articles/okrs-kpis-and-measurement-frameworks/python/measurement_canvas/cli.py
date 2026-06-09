"""Command-line interface for the Measurement Frameworks Catalyst Canvas module."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

from .exporters import export_all
from .models import MeasurementItem
from .scoring import score_item
from .validation import validate_rows


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run OKRs KPIs Measurement Frameworks Catalyst Canvas diagnostics."
    )
    parser.add_argument(
        "--article-root",
        type=Path,
        default=Path.cwd(),
        help="Article directory root. Defaults to the current working directory."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Input CSV. Defaults to data/measurement_items.csv under article root."
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    article_root = args.article_root.resolve()
    input_path = args.input.resolve() if args.input else article_root / "data" / "measurement_items.csv"

    if not input_path.exists():
        print(f"Input file not found: {input_path}", file=sys.stderr)
        return 2

    rows = read_csv_rows(input_path)
    errors = validate_rows(rows)

    if errors:
        print("Input validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 2

    items = [MeasurementItem.from_row(row) for row in rows]
    results = [score_item(item) for item in items]
    results = sorted(results, key=lambda item: item.governance_priority, reverse=True)

    export_all(article_root, results)

    print("OKRs KPIs Measurement Frameworks Catalyst Canvas audit complete.")
    print(article_root / "outputs" / "tables" / "measurement_canvas_audit.csv")
    print(article_root / "canvas" / "canvas_cards.json")
    print(article_root / "canvas" / "governance_queue.json")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
