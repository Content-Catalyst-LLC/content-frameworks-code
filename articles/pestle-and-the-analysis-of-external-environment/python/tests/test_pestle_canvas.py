"""Tests for the PESTLE Analysis Catalyst Canvas module."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

TEST_DIR = Path(__file__).resolve().parent
PYTHON_DIR = TEST_DIR.parent

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from pestle_canvas.models import PESTLEFactor  # noqa: E402
from pestle_canvas.scoring import PRIORITY_WEIGHTS, evidence_gap, monitoring_priority, score_factor  # noqa: E402
from pestle_canvas.validation import validate_rows, validate_weights  # noqa: E402


def sample_factor() -> PESTLEFactor:
    return PESTLEFactor(
        factor="Test factor",
        category="technological",
        signal_type="driver",
        description="A test PESTLE factor for scoring.",
        impact=0.80,
        urgency=0.78,
        evidence_strength=0.70,
        uncertainty=0.60,
        strategic_relevance=0.82,
        actionability=0.74,
        claim_strength=0.78,
        owner="test",
        status="active",
        review_date="2026-06-08",
    )


class PESTLECanvasTests(unittest.TestCase):
    def test_weights_sum_to_one(self) -> None:
        validate_weights(PRIORITY_WEIGHTS)

    def test_evidence_gap(self) -> None:
        self.assertAlmostEqual(evidence_gap(sample_factor()), 0.08)

    def test_monitoring_priority(self) -> None:
        self.assertAlmostEqual(monitoring_priority(sample_factor()), 0.48)

    def test_score_factor_ranges(self) -> None:
        result = score_factor(sample_factor())

        for field in [
            "readiness_score",
            "weighted_priority",
            "evidence_gap",
            "monitoring_priority",
            "governance_priority",
        ]:
            value = getattr(result, field)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_validation_catches_duplicate_factors(self) -> None:
        row = {
            "factor": "Duplicate",
            "category": "social",
            "signal_type": "driver",
            "description": "A useful description",
            "impact": "0.8",
            "urgency": "0.7",
            "evidence_strength": "0.7",
            "uncertainty": "0.5",
            "strategic_relevance": "0.8",
            "actionability": "0.7",
            "claim_strength": "0.8",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row, dict(row)])
        self.assertTrue(any("duplicate factor" in error for error in errors))

    def test_validation_catches_bad_category(self) -> None:
        row = {
            "factor": "Bad category",
            "category": "cultural",
            "signal_type": "driver",
            "description": "A useful description",
            "impact": "0.8",
            "urgency": "0.7",
            "evidence_strength": "0.7",
            "uncertainty": "0.5",
            "strategic_relevance": "0.8",
            "actionability": "0.7",
            "claim_strength": "0.8",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row])
        self.assertTrue(any("category" in error and "must be one of" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
