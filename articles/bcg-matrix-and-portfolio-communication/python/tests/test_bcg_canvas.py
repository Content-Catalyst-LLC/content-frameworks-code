"""Tests for the BCG Matrix Catalyst Canvas module."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

TEST_DIR = Path(__file__).resolve().parent
PYTHON_DIR = TEST_DIR.parent

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from bcg_canvas.models import PortfolioItem  # noqa: E402
from bcg_canvas.scoring import evidence_gap, portfolio_priority, quadrant, score_item  # noqa: E402
from bcg_canvas.validation import validate_rows  # noqa: E402


def sample_item() -> PortfolioItem:
    return PortfolioItem(
        item="Test portfolio item",
        portfolio_area="test area",
        description="A test portfolio item for scoring.",
        growth_score=0.80,
        relative_share_score=0.70,
        evidence_strength=0.68,
        strategic_fit=0.82,
        maintenance_burden=0.60,
        claim_strength=0.78,
        owner="test",
        status="active",
        review_date="2026-06-08",
    )


class BCGCanvasTests(unittest.TestCase):
    def test_quadrant_star(self) -> None:
        self.assertEqual(quadrant(sample_item()), "star")

    def test_evidence_gap(self) -> None:
        self.assertAlmostEqual(evidence_gap(sample_item()), 0.10)

    def test_portfolio_priority_range(self) -> None:
        value = portfolio_priority(sample_item())
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_score_item_ranges(self) -> None:
        result = score_item(sample_item())

        for field in [
            "growth_score",
            "relative_share_score",
            "evidence_gap",
            "portfolio_priority",
        ]:
            value = getattr(result, field)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_validation_catches_duplicate_items(self) -> None:
        row = {
            "item": "Duplicate",
            "portfolio_area": "test",
            "description": "A useful description",
            "growth_score": "0.8",
            "relative_share_score": "0.7",
            "evidence_strength": "0.7",
            "strategic_fit": "0.8",
            "maintenance_burden": "0.6",
            "claim_strength": "0.8",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row, dict(row)])
        self.assertTrue(any("duplicate item" in error for error in errors))

    def test_validation_catches_bad_numeric_range(self) -> None:
        row = {
            "item": "Bad range",
            "portfolio_area": "test",
            "description": "A useful description",
            "growth_score": "1.2",
            "relative_share_score": "0.7",
            "evidence_strength": "0.7",
            "strategic_fit": "0.8",
            "maintenance_burden": "0.6",
            "claim_strength": "0.8",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row])
        self.assertTrue(any("growth_score" in error and "between 0 and 1" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
