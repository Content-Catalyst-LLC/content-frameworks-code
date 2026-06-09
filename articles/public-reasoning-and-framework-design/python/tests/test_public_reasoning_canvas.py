"""Tests for the Public Reasoning Catalyst Canvas module."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

TEST_DIR = Path(__file__).resolve().parent
PYTHON_DIR = TEST_DIR.parent

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from public_reasoning_canvas.models import PublicReasoningItem  # noqa: E402
from public_reasoning_canvas.scoring import legitimacy_risk, quality_score, review_priority_score, score_item  # noqa: E402
from public_reasoning_canvas.validation import validate_rows  # noqa: E402


def sample_item() -> PublicReasoningItem:
    return PublicReasoningItem(
        item="Test public reasoning item",
        reasoning_type="policy reasoning",
        description="A test public reasoning framework for scoring.",
        claim_clarity=0.80,
        evidence_visibility=0.76,
        value_transparency=0.74,
        tradeoff_clarity=0.72,
        stakeholder_inclusion=0.70,
        uncertainty_disclosure=0.68,
        participation_fit=0.66,
        accountability=0.64,
        transparency=0.78,
        owner="test",
        status="active",
        review_date="2026-06-08",
    )


class PublicReasoningCanvasTests(unittest.TestCase):
    def test_quality_score_range(self) -> None:
        value = quality_score(sample_item())
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_legitimacy_risk_range(self) -> None:
        value = legitimacy_risk(sample_item())
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
            "legitimacy_risk",
            "review_priority_score",
        ]:
            value = getattr(result, field)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_validation_catches_duplicate_items(self) -> None:
        row = {
            "item": "Duplicate",
            "reasoning_type": "policy reasoning",
            "description": "A useful description",
            "claim_clarity": "0.8",
            "evidence_visibility": "0.7",
            "value_transparency": "0.7",
            "tradeoff_clarity": "0.7",
            "stakeholder_inclusion": "0.7",
            "uncertainty_disclosure": "0.7",
            "participation_fit": "0.7",
            "accountability": "0.7",
            "transparency": "0.7",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row, dict(row)])
        self.assertTrue(any("duplicate item" in error for error in errors))

    def test_validation_catches_bad_numeric_range(self) -> None:
        row = {
            "item": "Bad range",
            "reasoning_type": "policy reasoning",
            "description": "A useful description",
            "claim_clarity": "1.2",
            "evidence_visibility": "0.7",
            "value_transparency": "0.7",
            "tradeoff_clarity": "0.7",
            "stakeholder_inclusion": "0.7",
            "uncertainty_disclosure": "0.7",
            "participation_fit": "0.7",
            "accountability": "0.7",
            "transparency": "0.7",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row])
        self.assertTrue(any("claim_clarity" in error and "between 0 and 1" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
