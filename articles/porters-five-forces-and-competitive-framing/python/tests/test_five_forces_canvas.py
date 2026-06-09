"""Tests for the Porter Five Forces Catalyst Canvas module."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

TEST_DIR = Path(__file__).resolve().parent
PYTHON_DIR = TEST_DIR.parent

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from five_forces_canvas.models import ForceRecord  # noqa: E402
from five_forces_canvas.scoring import PRIORITY_WEIGHTS, evidence_gap, score_record  # noqa: E402
from five_forces_canvas.validation import validate_rows, validate_weights  # noqa: E402


def sample_record() -> ForceRecord:
    return ForceRecord(
        force="rivalry",
        market_boundary="test market",
        description="A test competitive force record.",
        intensity=0.80,
        evidence_strength=0.70,
        uncertainty=0.60,
        strategic_relevance=0.82,
        actionability=0.74,
        claim_strength=0.78,
        owner="test",
        status="active",
        review_date="2026-06-08",
    )


class FiveForcesCanvasTests(unittest.TestCase):
    def test_weights_sum_to_one(self) -> None:
        validate_weights(PRIORITY_WEIGHTS)

    def test_evidence_gap(self) -> None:
        self.assertAlmostEqual(evidence_gap(sample_record()), 0.08)

    def test_score_record_ranges(self) -> None:
        result = score_record(sample_record())

        for field in [
            "readiness_score",
            "weighted_priority",
            "evidence_gap",
            "governance_priority",
        ]:
            value = getattr(result, field)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_validation_catches_duplicate_force_boundary(self) -> None:
        row = {
            "force": "rivalry",
            "market_boundary": "test market",
            "description": "A useful description",
            "intensity": "0.8",
            "evidence_strength": "0.7",
            "uncertainty": "0.6",
            "strategic_relevance": "0.8",
            "actionability": "0.7",
            "claim_strength": "0.8",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row, dict(row)])
        self.assertTrue(any("duplicate force" in error for error in errors))

    def test_validation_catches_bad_force(self) -> None:
        row = {
            "force": "brand pressure",
            "market_boundary": "test market",
            "description": "A useful description",
            "intensity": "0.8",
            "evidence_strength": "0.7",
            "uncertainty": "0.6",
            "strategic_relevance": "0.8",
            "actionability": "0.7",
            "claim_strength": "0.8",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row])
        self.assertTrue(any("force" in error and "must be one of" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
