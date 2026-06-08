
from __future__ import annotations
from pathlib import Path
import sys
import unittest
TEST_DIR = Path(__file__).resolve().parent
PYTHON_DIR = TEST_DIR.parent
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))
from content_framework_canvas.models import CanvasRecord
from content_framework_canvas.scoring import READINESS_WEIGHTS, score_record
from content_framework_canvas.validation import validate_rows, validate_weights

def sample_record() -> CanvasRecord:
    return CanvasRecord(
        record_id="test",
        article_slug="test-article",
        article_title="Test Article",
        module_kind="test",
        article_stage="active",
        canvas_dimension="Test Dimension",
        description="A test record for Canvas scoring.",
        content_value=0.80,
        audience_value=0.78,
        evidence_strength=0.76,
        repository_support=0.72,
        governance_need=0.40,
        ethical_risk=0.20,
        owner="test",
        status="active",
        review_date="2026-06-08",
    )

class ContentFrameworkCanvasTests(unittest.TestCase):
    def test_weights_sum_to_one(self) -> None:
        validate_weights(READINESS_WEIGHTS)

    def test_score_ranges(self) -> None:
        result = score_record(sample_record())
        for field in ["content_score", "audience_score", "evidence_score", "repository_score", "governance_pressure", "ethical_risk", "readiness_score"]:
            value = getattr(result, field)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_validation_rejects_bad_score(self) -> None:
        row = {
            "record_id": "bad",
            "article_slug": "test",
            "article_title": "Test",
            "module_kind": "test",
            "article_stage": "active",
            "canvas_dimension": "Dimension",
            "description": "A useful description",
            "content_value": "1.5",
            "audience_value": "0.7",
            "evidence_strength": "0.7",
            "repository_support": "0.7",
            "governance_need": "0.4",
            "ethical_risk": "0.2",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }
        errors = validate_rows([row])
        self.assertTrue(any("between 0 and 1" in error for error in errors))

    def test_validation_rejects_duplicate_record_id(self) -> None:
        row = {
            "record_id": "duplicate",
            "article_slug": "test",
            "article_title": "Test",
            "module_kind": "test",
            "article_stage": "active",
            "canvas_dimension": "Dimension",
            "description": "A useful description",
            "content_value": "0.8",
            "audience_value": "0.7",
            "evidence_strength": "0.7",
            "repository_support": "0.7",
            "governance_need": "0.4",
            "ethical_risk": "0.2",
            "owner": "test",
            "status": "active",
            "review_date": "2026-06-08",
        }
        errors = validate_rows([row, dict(row)])
        self.assertTrue(any("duplicate record_id" in error for error in errors))

if __name__ == "__main__":
    unittest.main()
