"""Tests for the Audience Journey Catalyst Canvas module."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

TEST_DIR = Path(__file__).resolve().parent
PYTHON_DIR = TEST_DIR.parent

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from audience_journey_canvas.models import JourneyStage  # noqa: E402
from audience_journey_canvas.scoring import READINESS_WEIGHTS, link_gap, score_stage  # noqa: E402
from audience_journey_canvas.validation import validate_rows, validate_weights  # noqa: E402


def sample_stage() -> JourneyStage:
    return JourneyStage(
        stage="Test stage",
        audience_need="A useful audience need.",
        journey_type="test_journey",
        stage_clarity=0.80,
        content_coverage=0.78,
        transition_quality=0.76,
        evidence_readiness=0.74,
        governance_readiness=0.72,
        required_links=3,
        available_links=2,
        persona_fit=0.82,
        staleness_risk=0.20,
        owner="test",
        status="active",
        review_date="2026-06-08",
    )


class AudienceJourneyCanvasTests(unittest.TestCase):
    def test_weights_sum_to_one(self) -> None:
        validate_weights(READINESS_WEIGHTS)

    def test_link_gap(self) -> None:
        self.assertEqual(link_gap(sample_stage()), 1)

    def test_score_stage_ranges(self) -> None:
        result = score_stage(sample_stage())

        for field in [
            "readiness_score",
            "weighted_readiness",
            "persona_mismatch",
            "journey_risk",
        ]:
            value = getattr(result, field)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_validation_catches_duplicate_stages(self) -> None:
        row = {
            "stage": "Duplicate",
            "audience_need": "A useful need",
            "journey_type": "learning",
            "stage_clarity": "0.8",
            "content_coverage": "0.7",
            "transition_quality": "0.7",
            "evidence_readiness": "0.7",
            "governance_readiness": "0.8",
            "required_links": "2",
            "available_links": "1",
            "persona_fit": "0.8",
            "staleness_risk": "0.2",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row, dict(row)])
        self.assertTrue(any("duplicate stage" in error for error in errors))

    def test_validation_catches_negative_links(self) -> None:
        row = {
            "stage": "Bad links",
            "audience_need": "A useful need",
            "journey_type": "learning",
            "stage_clarity": "0.8",
            "content_coverage": "0.7",
            "transition_quality": "0.7",
            "evidence_readiness": "0.7",
            "governance_readiness": "0.8",
            "required_links": "-2",
            "available_links": "1",
            "persona_fit": "0.8",
            "staleness_risk": "0.2",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row])
        self.assertTrue(any("cannot be negative" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
