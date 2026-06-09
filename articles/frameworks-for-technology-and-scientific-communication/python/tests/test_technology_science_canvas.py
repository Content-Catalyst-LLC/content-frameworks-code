"""Tests for the Technology and Scientific Communication Catalyst Canvas module."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

TEST_DIR = Path(__file__).resolve().parent
PYTHON_DIR = TEST_DIR.parent

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from technology_science_canvas.models import TechScienceItem  # noqa: E402
from technology_science_canvas.scoring import evidence_gap, hype_risk, quality_score, score_item  # noqa: E402
from technology_science_canvas.validation import validate_rows  # noqa: E402


def sample_item() -> TechScienceItem:
    return TechScienceItem(
        item="Test science item",
        communication_type="science",
        description="A test technical and scientific communication item for scoring.",
        claim_clarity=0.80,
        evidence_strength=0.70,
        method_transparency=0.76,
        uncertainty_disclosure=0.68,
        audience_fit=0.74,
        risk_visibility=0.72,
        stakeholder_visibility=0.66,
        promotional_intensity=0.30,
        claim_breadth=0.82,
        owner="test",
        status="active",
        review_date="2026-06-08",
    )


class TechnologyScienceCanvasTests(unittest.TestCase):
    def test_quality_score_range(self) -> None:
        value = quality_score(sample_item())
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_evidence_gap(self) -> None:
        self.assertAlmostEqual(evidence_gap(sample_item()), 0.12)

    def test_hype_risk_range(self) -> None:
        value = hype_risk(sample_item())
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_score_item_ranges(self) -> None:
        result = score_item(sample_item())

        for field in [
            "quality_score",
            "evidence_gap",
            "hype_risk",
            "review_priority_score",
        ]:
            value = getattr(result, field)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_validation_catches_duplicate_items(self) -> None:
        row = {
            "item": "Duplicate",
            "communication_type": "science",
            "description": "A useful description",
            "claim_clarity": "0.8",
            "evidence_strength": "0.7",
            "method_transparency": "0.7",
            "uncertainty_disclosure": "0.7",
            "audience_fit": "0.7",
            "risk_visibility": "0.7",
            "stakeholder_visibility": "0.7",
            "promotional_intensity": "0.2",
            "claim_breadth": "0.8",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row, dict(row)])
        self.assertTrue(any("duplicate item" in error for error in errors))

    def test_validation_catches_bad_numeric_range(self) -> None:
        row = {
            "item": "Bad range",
            "communication_type": "science",
            "description": "A useful description",
            "claim_clarity": "1.2",
            "evidence_strength": "0.7",
            "method_transparency": "0.7",
            "uncertainty_disclosure": "0.7",
            "audience_fit": "0.7",
            "risk_visibility": "0.7",
            "stakeholder_visibility": "0.7",
            "promotional_intensity": "0.2",
            "claim_breadth": "0.8",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row])
        self.assertTrue(any("claim_clarity" in error and "between 0 and 1" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
