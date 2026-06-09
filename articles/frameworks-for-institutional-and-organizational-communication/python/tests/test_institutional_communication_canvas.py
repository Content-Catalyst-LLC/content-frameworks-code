"""Tests for the Institutional Communication Catalyst Canvas module."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

TEST_DIR = Path(__file__).resolve().parent
PYTHON_DIR = TEST_DIR.parent

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from institutional_communication_canvas.models import CommunicationItem  # noqa: E402
from institutional_communication_canvas.scoring import evidence_gap, quality_score, score_item, trust_risk  # noqa: E402
from institutional_communication_canvas.validation import validate_rows  # noqa: E402


def sample_item() -> CommunicationItem:
    return CommunicationItem(
        item="Test communication item",
        communication_type="governance",
        description="A test institutional communication item for scoring.",
        clarity=0.80,
        authority_coverage=0.78,
        evidence_strength=0.70,
        stakeholder_visibility=0.72,
        feedback_quality=0.68,
        channel_fit=0.76,
        cultural_alignment=0.74,
        governance_coverage=0.72,
        ambiguity=0.30,
        claim_strength=0.82,
        owner="test",
        status="active",
        review_date="2026-06-08",
    )


class InstitutionalCommunicationCanvasTests(unittest.TestCase):
    def test_quality_score_range(self) -> None:
        value = quality_score(sample_item())
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_evidence_gap(self) -> None:
        self.assertAlmostEqual(evidence_gap(sample_item()), 0.12)

    def test_trust_risk_range(self) -> None:
        value = trust_risk(sample_item())
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_score_item_ranges(self) -> None:
        result = score_item(sample_item())

        for field in [
            "quality_score",
            "evidence_gap",
            "trust_risk",
            "review_priority_score",
        ]:
            value = getattr(result, field)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_validation_catches_duplicate_items(self) -> None:
        row = {
            "item": "Duplicate",
            "communication_type": "governance",
            "description": "A useful description",
            "clarity": "0.8",
            "authority_coverage": "0.7",
            "evidence_strength": "0.7",
            "stakeholder_visibility": "0.7",
            "feedback_quality": "0.7",
            "channel_fit": "0.7",
            "cultural_alignment": "0.7",
            "governance_coverage": "0.7",
            "ambiguity": "0.2",
            "claim_strength": "0.8",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row, dict(row)])
        self.assertTrue(any("duplicate item" in error for error in errors))

    def test_validation_catches_bad_numeric_range(self) -> None:
        row = {
            "item": "Bad range",
            "communication_type": "governance",
            "description": "A useful description",
            "clarity": "1.2",
            "authority_coverage": "0.7",
            "evidence_strength": "0.7",
            "stakeholder_visibility": "0.7",
            "feedback_quality": "0.7",
            "channel_fit": "0.7",
            "cultural_alignment": "0.7",
            "governance_coverage": "0.7",
            "ambiguity": "0.2",
            "claim_strength": "0.8",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row])
        self.assertTrue(any("clarity" in error and "between 0 and 1" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
