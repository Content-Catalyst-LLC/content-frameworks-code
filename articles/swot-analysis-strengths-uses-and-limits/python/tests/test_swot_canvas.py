"""Tests for the SWOT Analysis Catalyst Canvas module."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

TEST_DIR = Path(__file__).resolve().parent
PYTHON_DIR = TEST_DIR.parent

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from swot_canvas.models import SWOTItem  # noqa: E402
from swot_canvas.scoring import PRIORITY_WEIGHTS, evidence_gap, score_item  # noqa: E402
from swot_canvas.validation import validate_rows, validate_weights  # noqa: E402


def sample_item() -> SWOTItem:
    return SWOTItem(
        item="Test item",
        quadrant="strength",
        orientation="internal",
        description="A test SWOT item for scoring.",
        impact=0.80,
        confidence=0.78,
        urgency=0.76,
        feasibility=0.74,
        strategic_fit=0.82,
        evidence_strength=0.70,
        claim_strength=0.78,
        owner="test",
        status="active",
        review_date="2026-06-08",
    )


class SWOTCanvasTests(unittest.TestCase):
    def test_weights_sum_to_one(self) -> None:
        validate_weights(PRIORITY_WEIGHTS)

    def test_evidence_gap(self) -> None:
        self.assertAlmostEqual(evidence_gap(sample_item()), 0.08)

    def test_score_item_ranges(self) -> None:
        result = score_item(sample_item())

        for field in [
            "priority_score",
            "weighted_priority",
            "evidence_gap",
            "governance_priority",
        ]:
            value = getattr(result, field)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_validation_catches_duplicate_items(self) -> None:
        row = {
            "item": "Duplicate",
            "quadrant": "strength",
            "orientation": "internal",
            "description": "A useful description",
            "impact": "0.8",
            "confidence": "0.7",
            "urgency": "0.7",
            "feasibility": "0.7",
            "strategic_fit": "0.8",
            "evidence_strength": "0.7",
            "claim_strength": "0.8",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row, dict(row)])
        self.assertTrue(any("duplicate item" in error for error in errors))

    def test_validation_catches_orientation_mismatch(self) -> None:
        row = {
            "item": "Mismatch",
            "quadrant": "threat",
            "orientation": "internal",
            "description": "A useful description",
            "impact": "0.8",
            "confidence": "0.7",
            "urgency": "0.7",
            "feasibility": "0.7",
            "strategic_fit": "0.8",
            "evidence_strength": "0.7",
            "claim_strength": "0.8",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row])
        self.assertTrue(any("should use orientation" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
