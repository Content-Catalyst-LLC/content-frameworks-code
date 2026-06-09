"""Command-line interface for the Audience Journey Catalyst Canvas module."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

from .exporters import export_all
from .models import JourneyStage
from .scoring import score_stage
from .validation import validate_rows


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run Audience Journey Catalyst Canvas diagnostics."
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
        help="Input CSV. Defaults to data/audience_journey_stages.csv under article root."
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    article_root = args.article_root.resolve()
    input_path = args.input.resolve() if args.input else article_root / "data" / "audience_journey_stages.csv"

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

    stages = [JourneyStage.from_row(row) for row in rows]
    results = [score_stage(stage) for stage in stages]
    results = sorted(results, key=lambda item: item.weighted_readiness, reverse=True)

    export_all(article_root, results)

    print("Audience Journey Catalyst Canvas audit complete.")
    print(article_root / "outputs" / "tables" / "audience_journey_canvas_audit.csv")
    print(article_root / "canvas" / "canvas_cards.json")
    print(article_root / "canvas" / "governance_queue.json")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
