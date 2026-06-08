"""Tests for the STP Catalyst Canvas module."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

TEST_DIR = Path(__file__).resolve().parent
PYTHON_DIR = TEST_DIR.parent

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from stp_canvas.models import SegmentProfile  # noqa: E402
from stp_canvas.scoring import (  # noqa: E402
    GOVERNANCE_WEIGHTS,
    TARGET_WEIGHTS,
    score_profile,
)
from stp_canvas.validation import validate_rows, validate_weights  # noqa: E402


def sample_profile() -> SegmentProfile:
    return SegmentProfile(
        segment="Test segment",
        description="A test segment for scoring.",
        primary_job="Understand the STP scoring logic.",
        content_pathway="Test pathway",
        need_intensity=0.80,
        strategic_fit=0.70,
        reachability=0.60,
        evidence_fit=0.75,
        ethical_responsibility=0.90,
        category_clarity=0.65,
        audience_relevance=0.80,
        differentiation=0.60,
        credibility=0.72,
        stereotype_risk=0.20,
        exclusion_risk=0.30,
        owner="test",
        status="active",
        review_date="2026-06-08",
    )


class STPCanvasTests(unittest.TestCase):
    def test_weights_sum_to_one(self) -> None:
        validate_weights(TARGET_WEIGHTS)
        validate_weights(GOVERNANCE_WEIGHTS)

    def test_score_profile_ranges(self) -> None:
        result = score_profile(sample_profile())

        for field in [
            "target_score",
            "weighted_target_score",
            "positioning_score",
            "positioning_gap",
            "ethical_risk_score",
            "governance_score",
        ]:
            value = getattr(result, field)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_validation_catches_duplicate_segments(self) -> None:
        row = {
            "segment": "Duplicate",
            "description": "A useful description",
            "primary_job": "A useful primary job",
            "content_pathway": "A useful pathway",
            "need_intensity": "0.8",
            "strategic_fit": "0.7",
            "reachability": "0.6",
            "evidence_fit": "0.7",
            "ethical_responsibility": "0.8",
            "category_clarity": "0.6",
            "audience_relevance": "0.7",
            "differentiation": "0.6",
            "credibility": "0.7",
            "stereotype_risk": "0.2",
            "exclusion_risk": "0.3",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row, dict(row)])
        self.assertTrue(any("duplicate segment" in error for error in errors))

    def test_validation_catches_out_of_range_scores(self) -> None:
        row = {
            "segment": "Out of range",
            "description": "A useful description",
            "primary_job": "A useful primary job",
            "content_pathway": "A useful pathway",
            "need_intensity": "1.2",
            "strategic_fit": "0.7",
            "reachability": "0.6",
            "evidence_fit": "0.7",
            "ethical_responsibility": "0.8",
            "category_clarity": "0.6",
            "audience_relevance": "0.7",
            "differentiation": "0.6",
            "credibility": "0.7",
            "stereotype_risk": "0.2",
            "exclusion_risk": "0.3",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row])
        self.assertTrue(any("between 0 and 1" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
