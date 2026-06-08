"""CLI for generic Content Frameworks Catalyst Canvas readiness audits."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

from .exporters import export_all
from .models import CanvasRecord
from .scoring import score_record
from .validation import validate_rows


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a Catalyst Canvas readiness audit for a Content Frameworks article."
    )
    parser.add_argument(
        "--article-root",
        type=Path,
        default=Path.cwd(),
        help="Article directory root. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Input CSV. Defaults to data/article_canvas_inputs.csv under article root.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    article_root = args.article_root.resolve()
    input_path = args.input.resolve() if args.input else article_root / "data" / "article_canvas_inputs.csv"

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

    records = [CanvasRecord.from_row(row) for row in rows]
    results = [score_record(record) for record in records]
    results = sorted(results, key=lambda item: item.readiness_score, reverse=True)

    export_all(article_root, results)

    print("Catalyst Canvas article-readiness audit complete.")
    print(article_root / "outputs" / "tables" / "article_canvas_audit.csv")
    print(article_root / "canvas" / "canvas_cards.json")
    print(article_root / "canvas" / "governance_queue.json")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
