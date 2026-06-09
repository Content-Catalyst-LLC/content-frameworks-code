"""Tests for the Framework Governance Catalyst Canvas module."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

TEST_DIR = Path(__file__).resolve().parent
PYTHON_DIR = TEST_DIR.parent

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from framework_governance_canvas.models import FrameworkGovernanceItem  # noqa: E402
from framework_governance_canvas.scoring import governance_maturity, maintenance_risk, review_priority_score, score_item  # noqa: E402
from framework_governance_canvas.validation import validate_rows  # noqa: E402


def sample_item() -> FrameworkGovernanceItem:
    return FrameworkGovernanceItem(
        item="Test framework governance item",
        item_type="article map",
        description="A test framework governance item for scoring.",
        ownership_clarity=0.80,
        review_cycle_strength=0.76,
        metadata_completeness=0.74,
        evidence_status=0.72,
        link_health=0.70,
        taxonomy_alignment=0.68,
        platform_readiness=0.66,
        stale_evidence_risk=0.34,
        dependency_complexity=0.32,
        audience_impact=0.64,
        owner="test",
        status="active",
        review_date="2026-06-09",
    )


class FrameworkGovernanceCanvasTests(unittest.TestCase):
    def test_governance_maturity_range(self) -> None:
        value = governance_maturity(sample_item())
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_maintenance_risk_range(self) -> None:
        value = maintenance_risk(sample_item())
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_review_priority_score_range(self) -> None:
        value = review_priority_score(sample_item())
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_score_item_ranges(self) -> None:
        result = score_item(sample_item())

        for field in [
            "governance_maturity",
            "maintenance_risk",
            "review_priority_score",
        ]:
            value = getattr(result, field)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_validation_catches_duplicate_items(self) -> None:
        row = {
            "item": "Duplicate",
            "item_type": "article map",
            "description": "A useful description",
            "ownership_clarity": "0.8",
            "review_cycle_strength": "0.7",
            "metadata_completeness": "0.7",
            "evidence_status": "0.7",
            "link_health": "0.7",
            "taxonomy_alignment": "0.7",
            "platform_readiness": "0.7",
            "stale_evidence_risk": "0.3",
            "dependency_complexity": "0.3",
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
            "item_type": "article map",
            "description": "A useful description",
            "ownership_clarity": "1.2",
            "review_cycle_strength": "0.7",
            "metadata_completeness": "0.7",
            "evidence_status": "0.7",
            "link_health": "0.7",
            "taxonomy_alignment": "0.7",
            "platform_readiness": "0.7",
            "stale_evidence_risk": "0.3",
            "dependency_complexity": "0.3",
            "audience_impact": "0.7",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-09",
        }

        errors = validate_rows([row])
        self.assertTrue(any("ownership_clarity" in error and "between 0 and 1" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
