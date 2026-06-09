"""Tests for the Strategic Foresight Catalyst Canvas module."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

TEST_DIR = Path(__file__).resolve().parent
PYTHON_DIR = TEST_DIR.parent

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from strategic_foresight_canvas.models import ForesightItem  # noqa: E402
from strategic_foresight_canvas.scoring import assumption_risk, quality_score, review_priority_score, score_item  # noqa: E402
from strategic_foresight_canvas.validation import validate_rows  # noqa: E402


def sample_item() -> ForesightItem:
    return ForesightItem(
        item="Test foresight item",
        foresight_type="scenario",
        description="A test strategic foresight item for scoring.",
        driver_clarity=0.80,
        uncertainty_logic=0.76,
        scenario_logic=0.74,
        assumption_transparency=0.72,
        option_relevance=0.70,
        indicator_coverage=0.68,
        evidence_strength=0.66,
        stakeholder_visibility=0.64,
        importance=0.82,
        uncertainty=0.78,
        owner="test",
        status="active",
        review_date="2026-06-08",
    )


class StrategicForesightCanvasTests(unittest.TestCase):
    def test_quality_score_range(self) -> None:
        value = quality_score(sample_item())
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_assumption_risk_range(self) -> None:
        value = assumption_risk(sample_item())
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_review_priority_score_range(self) -> None:
        value = review_priority_score(sample_item())
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_score_item_ranges(self) -> None:
        result = score_item(sample_item())

        for field in [
            "quality_score",
            "assumption_risk",
            "review_priority_score",
        ]:
            value = getattr(result, field)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_validation_catches_duplicate_items(self) -> None:
        row = {
            "item": "Duplicate",
            "foresight_type": "scenario",
            "description": "A useful description",
            "driver_clarity": "0.8",
            "uncertainty_logic": "0.7",
            "scenario_logic": "0.7",
            "assumption_transparency": "0.7",
            "option_relevance": "0.7",
            "indicator_coverage": "0.7",
            "evidence_strength": "0.7",
            "stakeholder_visibility": "0.7",
            "importance": "0.8",
            "uncertainty": "0.7",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row, dict(row)])
        self.assertTrue(any("duplicate item" in error for error in errors))

    def test_validation_catches_bad_numeric_range(self) -> None:
        row = {
            "item": "Bad range",
            "foresight_type": "scenario",
            "description": "A useful description",
            "driver_clarity": "1.2",
            "uncertainty_logic": "0.7",
            "scenario_logic": "0.7",
            "assumption_transparency": "0.7",
            "option_relevance": "0.7",
            "indicator_coverage": "0.7",
            "evidence_strength": "0.7",
            "stakeholder_visibility": "0.7",
            "importance": "0.8",
            "uncertainty": "0.7",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row])
        self.assertTrue(any("driver_clarity" in error and "between 0 and 1" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
