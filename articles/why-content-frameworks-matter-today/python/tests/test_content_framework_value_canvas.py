"""Tests for the Content Framework Value Catalyst Canvas module."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

TEST_DIR = Path(__file__).resolve().parent
PYTHON_DIR = TEST_DIR.parent

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from content_framework_value_canvas.models import ContentFrameworkValueItem  # noqa: E402
from content_framework_value_canvas.scoring import framework_risk, review_priority_score, value_score, score_item  # noqa: E402
from content_framework_value_canvas.validation import validate_rows  # noqa: E402


def sample_item() -> ContentFrameworkValueItem:
    return ContentFrameworkValueItem(
        item="Test content framework value item",
        framework_type="knowledge architecture",
        description="A test content framework value item for scoring.",
        coherence=0.80,
        reuse_readiness=0.76,
        evidence_visibility=0.74,
        audience_pathway_clarity=0.72,
        governance_maturity=0.70,
        platform_readiness=0.68,
        learning_support=0.66,
        ai_readiness=0.64,
        fragmentation_risk=0.32,
        context_preservation=0.74,
        maintenance_burden=0.34,
        owner="test",
        status="active",
        review_date="2026-06-09",
    )


class ContentFrameworkValueCanvasTests(unittest.TestCase):
    def test_value_score_range(self) -> None:
        value = value_score(sample_item())
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_framework_risk_range(self) -> None:
        value = framework_risk(sample_item())
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_review_priority_score_range(self) -> None:
        value = review_priority_score(sample_item())
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_score_item_ranges(self) -> None:
        result = score_item(sample_item())

        for field in [
            "value_score",
            "framework_risk",
            "review_priority_score",
        ]:
            value = getattr(result, field)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_validation_catches_duplicate_items(self) -> None:
        row = {
            "item": "Duplicate",
            "framework_type": "knowledge architecture",
            "description": "A useful description",
            "coherence": "0.8",
            "reuse_readiness": "0.7",
            "evidence_visibility": "0.7",
            "audience_pathway_clarity": "0.7",
            "governance_maturity": "0.7",
            "platform_readiness": "0.7",
            "learning_support": "0.7",
            "ai_readiness": "0.7",
            "fragmentation_risk": "0.3",
            "context_preservation": "0.7",
            "maintenance_burden": "0.3",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-09",
        }

        errors = validate_rows([row, dict(row)])
        self.assertTrue(any("duplicate item" in error for error in errors))

    def test_validation_catches_bad_numeric_range(self) -> None:
        row = {
            "item": "Bad range",
            "framework_type": "knowledge architecture",
            "description": "A useful description",
            "coherence": "1.2",
            "reuse_readiness": "0.7",
            "evidence_visibility": "0.7",
            "audience_pathway_clarity": "0.7",
            "governance_maturity": "0.7",
            "platform_readiness": "0.7",
            "learning_support": "0.7",
            "ai_readiness": "0.7",
            "fragmentation_risk": "0.3",
            "context_preservation": "0.7",
            "maintenance_burden": "0.3",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-09",
        }

        errors = validate_rows([row])
        self.assertTrue(any("coherence" in error and "between 0 and 1" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
