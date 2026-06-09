"""Tests for the Framework Drift Catalyst Canvas module."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

TEST_DIR = Path(__file__).resolve().parent
PYTHON_DIR = TEST_DIR.parent

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from framework_drift_canvas.models import FrameworkDriftItem  # noqa: E402
from framework_drift_canvas.scoring import conceptual_integrity, drift_risk, repair_priority_score, score_item  # noqa: E402
from framework_drift_canvas.validation import validate_rows  # noqa: E402


def sample_item() -> FrameworkDriftItem:
    return FrameworkDriftItem(
        item="Test framework drift item",
        item_type="definition",
        description="A test framework drift item for scoring.",
        definition_consistency=0.80,
        boundary_clarity=0.76,
        evidence_currency=0.74,
        metadata_consistency=0.72,
        link_health=0.70,
        governance_maturity=0.68,
        reuse_pressure=0.42,
        stale_evidence_risk=0.34,
        dependency_complexity=0.32,
        platform_alignment=0.74,
        audience_impact=0.64,
        owner="test",
        status="active",
        review_date="2026-06-09",
    )


class FrameworkDriftCanvasTests(unittest.TestCase):
    def test_conceptual_integrity_range(self) -> None:
        value = conceptual_integrity(sample_item())
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_drift_risk_range(self) -> None:
        value = drift_risk(sample_item())
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_repair_priority_score_range(self) -> None:
        value = repair_priority_score(sample_item())
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_score_item_ranges(self) -> None:
        result = score_item(sample_item())

        for field in [
            "conceptual_integrity",
            "drift_risk",
            "repair_priority_score",
        ]:
            value = getattr(result, field)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_validation_catches_duplicate_items(self) -> None:
        row = {
            "item": "Duplicate",
            "item_type": "definition",
            "description": "A useful description",
            "definition_consistency": "0.8",
            "boundary_clarity": "0.7",
            "evidence_currency": "0.7",
            "metadata_consistency": "0.7",
            "link_health": "0.7",
            "governance_maturity": "0.7",
            "reuse_pressure": "0.4",
            "stale_evidence_risk": "0.3",
            "dependency_complexity": "0.3",
            "platform_alignment": "0.7",
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
            "item_type": "definition",
            "description": "A useful description",
            "definition_consistency": "1.2",
            "boundary_clarity": "0.7",
            "evidence_currency": "0.7",
            "metadata_consistency": "0.7",
            "link_health": "0.7",
            "governance_maturity": "0.7",
            "reuse_pressure": "0.4",
            "stale_evidence_risk": "0.3",
            "dependency_complexity": "0.3",
            "platform_alignment": "0.7",
            "audience_impact": "0.7",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-09",
        }

        errors = validate_rows([row])
        self.assertTrue(any("definition_consistency" in error and "between 0 and 1" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
