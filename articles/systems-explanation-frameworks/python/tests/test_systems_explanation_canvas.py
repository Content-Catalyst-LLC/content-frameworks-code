"""Tests for the Systems Explanation Catalyst Canvas module."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

TEST_DIR = Path(__file__).resolve().parent
PYTHON_DIR = TEST_DIR.parent

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from systems_explanation_canvas.models import SystemsExplanationItem  # noqa: E402
from systems_explanation_canvas.scoring import quality_score, review_priority_score, score_item, systems_ambiguity  # noqa: E402
from systems_explanation_canvas.validation import validate_rows  # noqa: E402


def sample_item() -> SystemsExplanationItem:
    return SystemsExplanationItem(
        item="Test systems item",
        explanation_type="feedback",
        description="A test systems explanation item for scoring.",
        boundary_clarity=0.80,
        actor_coverage=0.76,
        relationship_clarity=0.78,
        feedback_visibility=0.74,
        delay_visibility=0.70,
        stock_flow_clarity=0.66,
        stakeholder_visibility=0.68,
        evidence_strength=0.72,
        leverage_readiness=0.64,
        owner="test",
        status="active",
        review_date="2026-06-08",
    )


class SystemsExplanationCanvasTests(unittest.TestCase):
    def test_quality_score_range(self) -> None:
        value = quality_score(sample_item())
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_systems_ambiguity_range(self) -> None:
        value = systems_ambiguity(sample_item())
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
            "systems_ambiguity",
            "review_priority_score",
        ]:
            value = getattr(result, field)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_validation_catches_duplicate_items(self) -> None:
        row = {
            "item": "Duplicate",
            "explanation_type": "feedback",
            "description": "A useful description",
            "boundary_clarity": "0.8",
            "actor_coverage": "0.7",
            "relationship_clarity": "0.7",
            "feedback_visibility": "0.7",
            "delay_visibility": "0.7",
            "stock_flow_clarity": "0.7",
            "stakeholder_visibility": "0.7",
            "evidence_strength": "0.7",
            "leverage_readiness": "0.7",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row, dict(row)])
        self.assertTrue(any("duplicate item" in error for error in errors))

    def test_validation_catches_bad_numeric_range(self) -> None:
        row = {
            "item": "Bad range",
            "explanation_type": "feedback",
            "description": "A useful description",
            "boundary_clarity": "1.2",
            "actor_coverage": "0.7",
            "relationship_clarity": "0.7",
            "feedback_visibility": "0.7",
            "delay_visibility": "0.7",
            "stock_flow_clarity": "0.7",
            "stakeholder_visibility": "0.7",
            "evidence_strength": "0.7",
            "leverage_readiness": "0.7",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row])
        self.assertTrue(any("boundary_clarity" in error and "between 0 and 1" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
