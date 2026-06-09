"""Tests for the Positioning Frameworks Catalyst Canvas module."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

TEST_DIR = Path(__file__).resolve().parent
PYTHON_DIR = TEST_DIR.parent

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from positioning_canvas.models import PositioningRecord  # noqa: E402
from positioning_canvas.scoring import READINESS_WEIGHTS, score_record  # noqa: E402
from positioning_canvas.validation import validate_rows, validate_weights  # noqa: E402


def sample_record() -> PositioningRecord:
    return PositioningRecord(
        idea="Test idea",
        description="A test idea for positioning.",
        category_frame="test_frame",
        audience_pathway="test_pathway",
        category_clarity=0.80,
        audience_relevance=0.78,
        differentiation=0.76,
        evidence_strength=0.74,
        governance_readiness=0.72,
        boundary_clarity=0.70,
        ethical_risk=0.20,
        drift_risk=0.25,
        owner="test",
        status="active",
        review_date="2026-06-08",
    )


class PositioningCanvasTests(unittest.TestCase):
    def test_weights_sum_to_one(self) -> None:
        validate_weights(READINESS_WEIGHTS)

    def test_score_record_ranges(self) -> None:
        result = score_record(sample_record())

        for field in [
            "readiness_score",
            "weighted_readiness",
            "evidence_gap",
            "ethical_risk",
            "drift_risk",
        ]:
            value = getattr(result, field)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_validation_catches_duplicate_ideas(self) -> None:
        row = {
            "idea": "Duplicate",
            "description": "A useful description",
            "category_frame": "framework",
            "audience_pathway": "pathway",
            "category_clarity": "0.8",
            "audience_relevance": "0.7",
            "differentiation": "0.7",
            "evidence_strength": "0.7",
            "governance_readiness": "0.8",
            "boundary_clarity": "0.7",
            "ethical_risk": "0.2",
            "drift_risk": "0.3",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row, dict(row)])
        self.assertTrue(any("duplicate idea" in error for error in errors))

    def test_validation_catches_out_of_range_scores(self) -> None:
        row = {
            "idea": "Out of range",
            "description": "A useful description",
            "category_frame": "framework",
            "audience_pathway": "pathway",
            "category_clarity": "1.2",
            "audience_relevance": "0.7",
            "differentiation": "0.7",
            "evidence_strength": "0.7",
            "governance_readiness": "0.8",
            "boundary_clarity": "0.7",
            "ethical_risk": "0.2",
            "drift_risk": "0.3",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row])
        self.assertTrue(any("between 0 and 1" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
