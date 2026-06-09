"""Tests for the Framework Limits Catalyst Canvas module."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

TEST_DIR = Path(__file__).resolve().parent
PYTHON_DIR = TEST_DIR.parent

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from framework_limits_canvas.models import FrameworkLimitItem  # noqa: E402
from framework_limits_canvas.scoring import distortion_risk, review_priority_score, usefulness_score, score_item  # noqa: E402
from framework_limits_canvas.validation import validate_rows  # noqa: E402


def sample_item() -> FrameworkLimitItem:
    return FrameworkLimitItem(
        item="Test framework limits item",
        framework_type="content framework",
        description="A test framework limits item for scoring.",
        clarity=0.80,
        fit=0.76,
        evidence_alignment=0.74,
        assumption_transparency=0.72,
        governance_readiness=0.70,
        oversimplification_risk=0.34,
        false_precision_risk=0.28,
        context_loss=0.32,
        audience_burden=0.30,
        value_opacity=0.26,
        owner="test",
        status="active",
        review_date="2026-06-08",
    )


class FrameworkLimitsCanvasTests(unittest.TestCase):
    def test_usefulness_score_range(self) -> None:
        value = usefulness_score(sample_item())
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_distortion_risk_range(self) -> None:
        value = distortion_risk(sample_item())
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_review_priority_score_range(self) -> None:
        value = review_priority_score(sample_item())
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_score_item_ranges(self) -> None:
        result = score_item(sample_item())

        for field in [
            "usefulness_score",
            "distortion_risk",
            "review_priority_score",
        ]:
            value = getattr(result, field)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_validation_catches_duplicate_items(self) -> None:
        row = {
            "item": "Duplicate",
            "framework_type": "content framework",
            "description": "A useful description",
            "clarity": "0.8",
            "fit": "0.7",
            "evidence_alignment": "0.7",
            "assumption_transparency": "0.7",
            "governance_readiness": "0.7",
            "oversimplification_risk": "0.3",
            "false_precision_risk": "0.3",
            "context_loss": "0.3",
            "audience_burden": "0.3",
            "value_opacity": "0.3",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row, dict(row)])
        self.assertTrue(any("duplicate item" in error for error in errors))

    def test_validation_catches_bad_numeric_range(self) -> None:
        row = {
            "item": "Bad range",
            "framework_type": "content framework",
            "description": "A useful description",
            "clarity": "1.2",
            "fit": "0.7",
            "evidence_alignment": "0.7",
            "assumption_transparency": "0.7",
            "governance_readiness": "0.7",
            "oversimplification_risk": "0.3",
            "false_precision_risk": "0.3",
            "context_loss": "0.3",
            "audience_burden": "0.3",
            "value_opacity": "0.3",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row])
        self.assertTrue(any("clarity" in error and "between 0 and 1" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
