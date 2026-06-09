"""Tests for the Ansoff Matrix Catalyst Canvas module."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

TEST_DIR = Path(__file__).resolve().parent
PYTHON_DIR = TEST_DIR.parent

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from ansoff_canvas.models import GrowthOption  # noqa: E402
from ansoff_canvas.scoring import evidence_gap, risk_score, score_option  # noqa: E402
from ansoff_canvas.validation import validate_rows  # noqa: E402


def sample_option() -> GrowthOption:
    return GrowthOption(
        option="Test option",
        growth_path="market penetration",
        market_status="existing",
        product_status="existing",
        description="A test growth option for scoring.",
        strategic_fit=0.80,
        evidence_strength=0.70,
        feasibility=0.76,
        capability_readiness=0.78,
        expected_value=0.82,
        market_familiarity=0.88,
        product_familiarity=0.90,
        uncertainty=0.30,
        claim_strength=0.78,
        owner="test",
        status="active",
        review_date="2026-06-08",
    )


class AnsoffCanvasTests(unittest.TestCase):
    def test_evidence_gap(self) -> None:
        self.assertAlmostEqual(evidence_gap(sample_option()), 0.08)

    def test_risk_score_range(self) -> None:
        value = risk_score(sample_option())
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_score_option_ranges(self) -> None:
        result = score_option(sample_option())

        for field in [
            "readiness_score",
            "risk_score",
            "evidence_gap",
            "growth_quality",
            "governance_priority",
        ]:
            value = getattr(result, field)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_validation_catches_duplicate_options(self) -> None:
        row = {
            "option": "Duplicate",
            "growth_path": "market penetration",
            "market_status": "existing",
            "product_status": "existing",
            "description": "A useful description",
            "strategic_fit": "0.8",
            "evidence_strength": "0.7",
            "feasibility": "0.7",
            "capability_readiness": "0.7",
            "expected_value": "0.8",
            "market_familiarity": "0.8",
            "product_familiarity": "0.8",
            "uncertainty": "0.4",
            "claim_strength": "0.8",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row, dict(row)])
        self.assertTrue(any("duplicate option" in error for error in errors))

    def test_validation_catches_path_mismatch(self) -> None:
        row = {
            "option": "Mismatch",
            "growth_path": "diversification",
            "market_status": "existing",
            "product_status": "existing",
            "description": "A useful description",
            "strategic_fit": "0.8",
            "evidence_strength": "0.7",
            "feasibility": "0.7",
            "capability_readiness": "0.7",
            "expected_value": "0.8",
            "market_familiarity": "0.8",
            "product_familiarity": "0.8",
            "uncertainty": "0.4",
            "claim_strength": "0.8",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row])
        self.assertTrue(any("does not match market/product status" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
