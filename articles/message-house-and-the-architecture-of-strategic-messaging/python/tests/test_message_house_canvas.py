"""Tests for the Message House Catalyst Canvas module."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

TEST_DIR = Path(__file__).resolve().parent
PYTHON_DIR = TEST_DIR.parent

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from message_house_canvas.models import MessagePillar  # noqa: E402
from message_house_canvas.scoring import READINESS_WEIGHTS, score_pillar  # noqa: E402
from message_house_canvas.validation import validate_rows, validate_weights  # noqa: E402


def sample_pillar() -> MessagePillar:
    return MessagePillar(
        pillar="Test pillar",
        description="A test pillar for scoring.",
        core_alignment=0.80,
        audience_relevance=0.78,
        evidence_strength=0.76,
        differentiation=0.72,
        governance_readiness=0.74,
        ethical_risk=0.20,
        owner="test",
        status="active",
        review_date="2026-06-08",
    )


class MessageHouseCanvasTests(unittest.TestCase):
    def test_weights_sum_to_one(self) -> None:
        validate_weights(READINESS_WEIGHTS)

    def test_score_pillar_ranges(self) -> None:
        result = score_pillar(sample_pillar())

        for field in [
            "readiness_score",
            "weighted_readiness",
            "proof_gap",
            "message_drift_risk",
            "ethical_risk",
        ]:
            value = getattr(result, field)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_validation_catches_duplicate_pillars(self) -> None:
        row = {
            "pillar": "Duplicate",
            "description": "A useful description",
            "core_alignment": "0.8",
            "audience_relevance": "0.7",
            "evidence_strength": "0.7",
            "differentiation": "0.7",
            "governance_readiness": "0.8",
            "ethical_risk": "0.2",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row, dict(row)])
        self.assertTrue(any("duplicate pillar" in error for error in errors))

    def test_validation_catches_out_of_range_scores(self) -> None:
        row = {
            "pillar": "Out of range",
            "description": "A useful description",
            "core_alignment": "1.2",
            "audience_relevance": "0.7",
            "evidence_strength": "0.7",
            "differentiation": "0.7",
            "governance_readiness": "0.8",
            "ethical_risk": "0.2",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row])
        self.assertTrue(any("between 0 and 1" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
