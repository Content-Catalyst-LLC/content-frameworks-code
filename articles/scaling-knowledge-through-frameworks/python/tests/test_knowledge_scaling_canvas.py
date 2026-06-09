"""Tests for the Knowledge Scaling Catalyst Canvas module."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

TEST_DIR = Path(__file__).resolve().parent
PYTHON_DIR = TEST_DIR.parent

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from knowledge_scaling_canvas.models import KnowledgeScalingItem  # noqa: E402
from knowledge_scaling_canvas.scoring import maintenance_risk, review_priority_score, scalability_score, score_item  # noqa: E402
from knowledge_scaling_canvas.validation import validate_rows  # noqa: E402


def sample_item() -> KnowledgeScalingItem:
    return KnowledgeScalingItem(
        item="Test knowledge scaling item",
        asset_type="article map",
        description="A test knowledge scaling item for scoring.",
        modularity=0.80,
        taxonomy_quality=0.76,
        metadata_completeness=0.74,
        link_coverage=0.72,
        evidence_alignment=0.70,
        reuse_readiness=0.68,
        governance_maturity=0.66,
        platform_readiness=0.64,
        audience_pathway_clarity=0.78,
        dependency_complexity=0.34,
        owner="test",
        status="active",
        review_date="2026-06-08",
    )


class KnowledgeScalingCanvasTests(unittest.TestCase):
    def test_scalability_score_range(self) -> None:
        value = scalability_score(sample_item())
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
            "scalability_score",
            "maintenance_risk",
            "review_priority_score",
        ]:
            value = getattr(result, field)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_validation_catches_duplicate_items(self) -> None:
        row = {
            "item": "Duplicate",
            "asset_type": "article map",
            "description": "A useful description",
            "modularity": "0.8",
            "taxonomy_quality": "0.7",
            "metadata_completeness": "0.7",
            "link_coverage": "0.7",
            "evidence_alignment": "0.7",
            "reuse_readiness": "0.7",
            "governance_maturity": "0.7",
            "platform_readiness": "0.7",
            "audience_pathway_clarity": "0.7",
            "dependency_complexity": "0.3",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row, dict(row)])
        self.assertTrue(any("duplicate item" in error for error in errors))

    def test_validation_catches_bad_numeric_range(self) -> None:
        row = {
            "item": "Bad range",
            "asset_type": "article map",
            "description": "A useful description",
            "modularity": "1.2",
            "taxonomy_quality": "0.7",
            "metadata_completeness": "0.7",
            "link_coverage": "0.7",
            "evidence_alignment": "0.7",
            "reuse_readiness": "0.7",
            "governance_maturity": "0.7",
            "platform_readiness": "0.7",
            "audience_pathway_clarity": "0.7",
            "dependency_complexity": "0.3",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row])
        self.assertTrue(any("modularity" in error and "between 0 and 1" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
