"""Tests for the Framework Composition Catalyst Canvas module."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

TEST_DIR = Path(__file__).resolve().parent
PYTHON_DIR = TEST_DIR.parent

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from framework_composition_canvas.models import FrameworkCompositionItem  # noqa: E402
from framework_composition_canvas.scoring import confusion_risk, quality_score, review_priority_score, score_item  # noqa: E402
from framework_composition_canvas.validation import validate_rows  # noqa: E402


def sample_item() -> FrameworkCompositionItem:
    return FrameworkCompositionItem(
        item="Test framework composition item",
        composition_type="sequence",
        description="A test framework composition item for scoring.",
        purpose_fit=0.80,
        role_clarity=0.76,
        boundary_clarity=0.74,
        sequence_clarity=0.72,
        translation_quality=0.70,
        evidence_alignment=0.68,
        governance_readiness=0.66,
        audience_burden=0.34,
        conflict_risk=0.24,
        owner="test",
        status="active",
        review_date="2026-06-08",
    )


class FrameworkCompositionCanvasTests(unittest.TestCase):
    def test_quality_score_range(self) -> None:
        value = quality_score(sample_item())
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_confusion_risk_range(self) -> None:
        value = confusion_risk(sample_item())
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
            "confusion_risk",
            "review_priority_score",
        ]:
            value = getattr(result, field)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_validation_catches_duplicate_items(self) -> None:
        row = {
            "item": "Duplicate",
            "composition_type": "sequence",
            "description": "A useful description",
            "purpose_fit": "0.8",
            "role_clarity": "0.7",
            "boundary_clarity": "0.7",
            "sequence_clarity": "0.7",
            "translation_quality": "0.7",
            "evidence_alignment": "0.7",
            "governance_readiness": "0.7",
            "audience_burden": "0.3",
            "conflict_risk": "0.2",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row, dict(row)])
        self.assertTrue(any("duplicate item" in error for error in errors))

    def test_validation_catches_bad_numeric_range(self) -> None:
        row = {
            "item": "Bad range",
            "composition_type": "sequence",
            "description": "A useful description",
            "purpose_fit": "1.2",
            "role_clarity": "0.7",
            "boundary_clarity": "0.7",
            "sequence_clarity": "0.7",
            "translation_quality": "0.7",
            "evidence_alignment": "0.7",
            "governance_readiness": "0.7",
            "audience_burden": "0.3",
            "conflict_risk": "0.2",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row])
        self.assertTrue(any("purpose_fit" in error and "between 0 and 1" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
