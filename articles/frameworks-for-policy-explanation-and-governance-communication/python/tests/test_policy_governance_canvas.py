"""Tests for the Policy Governance Catalyst Canvas module."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

TEST_DIR = Path(__file__).resolve().parent
PYTHON_DIR = TEST_DIR.parent

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from policy_governance_canvas.models import PolicyGovernanceItem  # noqa: E402
from policy_governance_canvas.scoring import completeness_score, evidence_gap, governance_risk, score_item  # noqa: E402
from policy_governance_canvas.validation import validate_rows  # noqa: E402


def sample_item() -> PolicyGovernanceItem:
    return PolicyGovernanceItem(
        item="Test policy item",
        policy_area="governance",
        description="A test policy explanation item for scoring.",
        problem_clarity=0.80,
        authority_clarity=0.78,
        evidence_strength=0.70,
        stakeholder_visibility=0.72,
        implementation_detail=0.74,
        accountability_coverage=0.76,
        participation_clarity=0.68,
        ambiguity=0.30,
        claim_strength=0.82,
        owner="test",
        status="active",
        review_date="2026-06-08",
    )


class PolicyGovernanceCanvasTests(unittest.TestCase):
    def test_completeness_score_range(self) -> None:
        value = completeness_score(sample_item())
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_evidence_gap(self) -> None:
        self.assertAlmostEqual(evidence_gap(sample_item()), 0.12)

    def test_governance_risk_range(self) -> None:
        value = governance_risk(sample_item())
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_score_item_ranges(self) -> None:
        result = score_item(sample_item())

        for field in [
            "completeness_score",
            "evidence_gap",
            "governance_risk",
            "review_priority_score",
        ]:
            value = getattr(result, field)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_validation_catches_duplicate_items(self) -> None:
        row = {
            "item": "Duplicate",
            "policy_area": "governance",
            "description": "A useful description",
            "problem_clarity": "0.8",
            "authority_clarity": "0.7",
            "evidence_strength": "0.7",
            "stakeholder_visibility": "0.7",
            "implementation_detail": "0.7",
            "accountability_coverage": "0.7",
            "participation_clarity": "0.7",
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
            "policy_area": "governance",
            "description": "A useful description",
            "problem_clarity": "1.2",
            "authority_clarity": "0.7",
            "evidence_strength": "0.7",
            "stakeholder_visibility": "0.7",
            "implementation_detail": "0.7",
            "accountability_coverage": "0.7",
            "participation_clarity": "0.7",
            "ambiguity": "0.2",
            "claim_strength": "0.8",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }

        errors = validate_rows([row])
        self.assertTrue(any("problem_clarity" in error and "between 0 and 1" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
