# Tests for the Logic Model Catalyst Canvas module.

from __future__ import annotations

from pathlib import Path
import sys
import unittest

TEST_DIR = Path(__file__).resolve().parent
PYTHON_DIR = TEST_DIR.parent

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from logic_model_canvas.models import LogicModelElement  # noqa: E402
from logic_model_canvas.scoring import assumption_risk, evidence_gap, pathway_quality, score_element  # noqa: E402
from logic_model_canvas.validation import validate_rows  # noqa: E402


def sample_element() -> LogicModelElement:
    return LogicModelElement(
        element="Test outcome",
        model_layer="outcome",
        description="A test logic-model element for scoring.",
        evidence_strength=0.70,
        assumption_importance=0.80,
        assumption_evidence=0.60,
        measurement_coverage=0.72,
        outcome_clarity=0.76,
        claim_strength=0.82,
        owner="test",
        status="active",
        review_date="2026-06-08",
    )


class LogicModelCanvasTests(unittest.TestCase):
    def test_assumption_risk(self) -> None:
        self.assertAlmostEqual(assumption_risk(sample_element()), 0.32)

    def test_evidence_gap(self) -> None:
        self.assertAlmostEqual(evidence_gap(sample_element()), 0.12)

    def test_pathway_quality_range(self) -> None:
        value = pathway_quality(sample_element())
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_score_element_ranges(self) -> None:
        result = score_element(sample_element())
        for field in ["assumption_risk", "evidence_gap", "pathway_quality", "governance_priority"]:
            value = getattr(result, field)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_validation_catches_duplicate_elements(self) -> None:
        row = {
            "element": "Duplicate",
            "model_layer": "output",
            "description": "A useful description",
            "evidence_strength": "0.8",
            "assumption_importance": "0.7",
            "assumption_evidence": "0.7",
            "measurement_coverage": "0.8",
            "outcome_clarity": "0.8",
            "claim_strength": "0.8",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }
        errors = validate_rows([row, dict(row)])
        self.assertTrue(any("duplicate element" in error for error in errors))

    def test_validation_catches_bad_model_layer(self) -> None:
        row = {
            "element": "Bad layer",
            "model_layer": "vague",
            "description": "A useful description",
            "evidence_strength": "0.8",
            "assumption_importance": "0.7",
            "assumption_evidence": "0.7",
            "measurement_coverage": "0.8",
            "outcome_clarity": "0.8",
            "claim_strength": "0.8",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }
        errors = validate_rows([row])
        self.assertTrue(any("model_layer" in error and "must be one of" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
