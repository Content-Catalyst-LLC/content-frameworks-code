"""Tests for the AI-Assisted Framework Design Catalyst Canvas module."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

TEST_DIR = Path(__file__).resolve().parent
PYTHON_DIR = TEST_DIR.parent

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from ai_assisted_framework_design_canvas.models import AIAssistedFrameworkItem  # noqa: E402
from ai_assisted_framework_design_canvas.scoring import ai_framework_risk, governance_priority_score, readiness_score, score_item  # noqa: E402
from ai_assisted_framework_design_canvas.validation import validate_rows  # noqa: E402


def sample_item() -> AIAssistedFrameworkItem:
    return AIAssistedFrameworkItem(
        item="Test AI-assisted framework design item",
        item_type="metadata",
        description="A test AI-assisted framework design item for scoring.",
        conceptual_clarity=0.80,
        evidence_grounding=0.76,
        metadata_consistency=0.74,
        human_review_strength=0.72,
        bias_review=0.70,
        governance_maturity=0.68,
        platform_readiness=0.66,
        drift_control=0.64,
        unsupported_claim_risk=0.34,
        generic_structure_risk=0.32,
        output_validation=0.74,
        audience_impact=0.64,
        owner="test",
        status="active",
        review_date="2026-06-09",
    )


class AIAssistedFrameworkDesignCanvasTests(unittest.TestCase):
    def test_readiness_score_range(self) -> None:
        value = readiness_score(sample_item())
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_ai_framework_risk_range(self) -> None:
        value = ai_framework_risk(sample_item())
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_governance_priority_score_range(self) -> None:
        value = governance_priority_score(sample_item())
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_score_item_ranges(self) -> None:
        result = score_item(sample_item())

        for field in [
            "readiness_score",
            "ai_framework_risk",
            "governance_priority_score",
        ]:
            value = getattr(result, field)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_validation_catches_duplicate_items(self) -> None:
        row = {
            "item": "Duplicate",
            "item_type": "metadata",
            "description": "A useful description",
            "conceptual_clarity": "0.8",
            "evidence_grounding": "0.7",
            "metadata_consistency": "0.7",
            "human_review_strength": "0.7",
            "bias_review": "0.7",
            "governance_maturity": "0.7",
            "platform_readiness": "0.7",
            "drift_control": "0.7",
            "unsupported_claim_risk": "0.3",
            "generic_structure_risk": "0.3",
            "output_validation": "0.7",
            "audience_impact": "0.7",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-09",
        }

        errors = validate_rows([row, dict(row)])
        self.assertTrue(any("duplicate item" in error for error in errors))

    def test_validation_catches_bad_numeric_range(self) -> None:
        row = {
            "item": "Bad range",
            "item_type": "metadata",
            "description": "A useful description",
            "conceptual_clarity": "1.2",
            "evidence_grounding": "0.7",
            "metadata_consistency": "0.7",
            "human_review_strength": "0.7",
            "bias_review": "0.7",
            "governance_maturity": "0.7",
            "platform_readiness": "0.7",
            "drift_control": "0.7",
            "unsupported_claim_risk": "0.3",
            "generic_structure_risk": "0.3",
            "output_validation": "0.7",
            "audience_impact": "0.7",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-09",
        }

        errors = validate_rows([row])
        self.assertTrue(any("conceptual_clarity" in error and "between 0 and 1" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
