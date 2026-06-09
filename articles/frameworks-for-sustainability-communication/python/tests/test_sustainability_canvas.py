"""Tests for the Sustainability Communication Catalyst Canvas module."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

TEST_DIR = Path(__file__).resolve().parent
PYTHON_DIR = TEST_DIR.parent

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from sustainability_canvas.models import SustainabilityClaim  # noqa: E402
from sustainability_canvas.scoring import evidence_gap, greenwashing_risk, quality_score, score_claim  # noqa: E402
from sustainability_canvas.validation import validate_rows  # noqa: E402


def sample_claim() -> SustainabilityClaim:
    return SustainabilityClaim(
        claim="Test sustainability claim",
        claim_type="performance",
        description="A test sustainability communication claim for scoring.",
        claim_specificity=0.80,
        boundary_clarity=0.76,
        evidence_strength=0.70,
        materiality_relevance=0.78,
        stakeholder_visibility=0.72,
        accountability_coverage=0.74,
        uncertainty_disclosure=0.68,
        promotional_intensity=0.30,
        claim_strength=0.82,
        owner="test",
        status="active",
        review_date="2026-06-08",
    )


class SustainabilityCanvasTests(unittest.TestCase):
    def test_quality_score_range(self) -> None:
        value = quality_score(sample_claim())
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_evidence_gap(self) -> None:
        self.assertAlmostEqual(evidence_gap(sample_claim()), 0.12)

    def test_greenwashing_risk_range(self) -> None:
        value = greenwashing_risk(sample_claim())
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_score_claim_ranges(self) -> None:
        result = score_claim(sample_claim())

        for field in [
            "quality_score",
            "evidence_gap",
            "greenwashing_risk",
            "review_priority_score",
        ]:
            value = getattr(result, field)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_validation_catches_duplicate_claims(self) -> None:
        row = {
            "claim": "Duplicate",
            "claim_type": "performance",
            "description": "A useful description",
            "claim_specificity": "0.8",
            "boundary_clarity": "0.7",
            "evidence_strength": "0.7",
            "materiality_relevance": "0.7",
            "stakeholder_visibility": "0.7",
            "accountability_coverage": "0.7",
            "uncertainty_disclosure": "0.7",
            "promotional_intensity": "0.2",
            "claim_strength": "0.8",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row, dict(row)])
        self.assertTrue(any("duplicate claim" in error for error in errors))

    def test_validation_catches_bad_numeric_range(self) -> None:
        row = {
            "claim": "Bad range",
            "claim_type": "performance",
            "description": "A useful description",
            "claim_specificity": "1.2",
            "boundary_clarity": "0.7",
            "evidence_strength": "0.7",
            "materiality_relevance": "0.7",
            "stakeholder_visibility": "0.7",
            "accountability_coverage": "0.7",
            "uncertainty_disclosure": "0.7",
            "promotional_intensity": "0.2",
            "claim_strength": "0.8",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row])
        self.assertTrue(any("claim_specificity" in error and "between 0 and 1" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
