"""Tests for the OKRs KPIs Measurement Frameworks Catalyst Canvas module."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

TEST_DIR = Path(__file__).resolve().parent
PYTHON_DIR = TEST_DIR.parent

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from measurement_canvas.models import MeasurementItem  # noqa: E402
from measurement_canvas.scoring import evidence_gap, measurement_risk, quality_score, score_item  # noqa: E402
from measurement_canvas.validation import validate_rows  # noqa: E402


def sample_item() -> MeasurementItem:
    return MeasurementItem(
        item="Test KPI",
        measurement_type="KPI",
        description="A test measurement item for scoring.",
        strategic_relevance=0.82,
        validity=0.78,
        reliability=0.76,
        actionability=0.74,
        timeliness=0.72,
        evidence_strength=0.70,
        gaming_risk=0.30,
        reporting_burden=0.36,
        ambiguity=0.32,
        claim_strength=0.80,
        owner="test",
        status="active",
        review_date="2026-06-08",
    )


class MeasurementCanvasTests(unittest.TestCase):
    def test_quality_score_range(self) -> None:
        value = quality_score(sample_item())
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_measurement_risk_range(self) -> None:
        value = measurement_risk(sample_item())
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_evidence_gap(self) -> None:
        self.assertAlmostEqual(evidence_gap(sample_item()), 0.10)

    def test_score_item_ranges(self) -> None:
        result = score_item(sample_item())

        for field in [
            "quality_score",
            "measurement_risk",
            "evidence_gap",
            "governance_priority",
        ]:
            value = getattr(result, field)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_validation_catches_duplicate_items(self) -> None:
        row = {
            "item": "Duplicate",
            "measurement_type": "KPI",
            "description": "A useful description",
            "strategic_relevance": "0.8",
            "validity": "0.8",
            "reliability": "0.7",
            "actionability": "0.8",
            "timeliness": "0.7",
            "evidence_strength": "0.7",
            "gaming_risk": "0.3",
            "reporting_burden": "0.3",
            "ambiguity": "0.2",
            "claim_strength": "0.8",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row, dict(row)])
        self.assertTrue(any("duplicate item" in error for error in errors))

    def test_validation_catches_bad_measurement_type(self) -> None:
        row = {
            "item": "Bad type",
            "measurement_type": "goal-ish",
            "description": "A useful description",
            "strategic_relevance": "0.8",
            "validity": "0.8",
            "reliability": "0.7",
            "actionability": "0.8",
            "timeliness": "0.7",
            "evidence_strength": "0.7",
            "gaming_risk": "0.3",
            "reporting_burden": "0.3",
            "ambiguity": "0.2",
            "claim_strength": "0.8",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row])
        self.assertTrue(any("measurement_type" in error and "must be one of" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
