"""Tests for the Persona Frameworks Catalyst Canvas module."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

TEST_DIR = Path(__file__).resolve().parent
PYTHON_DIR = TEST_DIR.parent

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from persona_canvas.models import PersonaRecord  # noqa: E402
from persona_canvas.scoring import READINESS_WEIGHTS, score_record  # noqa: E402
from persona_canvas.validation import validate_rows, validate_weights  # noqa: E402


def sample_record() -> PersonaRecord:
    return PersonaRecord(
        persona="Test persona",
        segment="Test segment",
        description="A test persona for scoring.",
        content_pathway="test_pathway",
        evidence_strength=0.80,
        specificity=0.78,
        content_fit=0.76,
        segment_alignment=0.74,
        governance_readiness=0.72,
        stereotype_risk=0.20,
        exclusion_risk=0.25,
        weak_evidence_risk=0.22,
        overgeneralization_risk=0.28,
        owner="test",
        status="active",
        review_date="2026-06-08",
    )


class PersonaCanvasTests(unittest.TestCase):
    def test_weights_sum_to_one(self) -> None:
        validate_weights(READINESS_WEIGHTS)

    def test_score_record_ranges(self) -> None:
        result = score_record(sample_record())

        for field in [
            "readiness_score",
            "weighted_readiness",
            "risk_score",
            "revision_pressure",
            "evidence_strength",
        ]:
            value = getattr(result, field)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_validation_catches_duplicate_personas(self) -> None:
        row = {
            "persona": "Duplicate",
            "segment": "Segment",
            "description": "A useful description",
            "content_pathway": "pathway",
            "evidence_strength": "0.8",
            "specificity": "0.7",
            "content_fit": "0.7",
            "segment_alignment": "0.7",
            "governance_readiness": "0.8",
            "stereotype_risk": "0.2",
            "exclusion_risk": "0.2",
            "weak_evidence_risk": "0.3",
            "overgeneralization_risk": "0.3",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row, dict(row)])
        self.assertTrue(any("duplicate persona" in error for error in errors))

    def test_validation_catches_out_of_range_scores(self) -> None:
        row = {
            "persona": "Out of range",
            "segment": "Segment",
            "description": "A useful description",
            "content_pathway": "pathway",
            "evidence_strength": "1.2",
            "specificity": "0.7",
            "content_fit": "0.7",
            "segment_alignment": "0.7",
            "governance_readiness": "0.8",
            "stereotype_risk": "0.2",
            "exclusion_risk": "0.2",
            "weak_evidence_risk": "0.3",
            "overgeneralization_risk": "0.3",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row])
        self.assertTrue(any("between 0 and 1" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
