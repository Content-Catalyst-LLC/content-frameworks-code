
from __future__ import annotations
import re

TEXT_FIELDS = [
    "record_id", "article_slug", "article_title", "module_kind", "article_stage",
    "canvas_dimension", "description", "owner", "status", "review_date"
]
NUMERIC_FIELDS = [
    "content_value", "audience_value", "evidence_strength",
    "repository_support", "governance_need", "ethical_risk"
]
VALID_STATUSES = {"active", "review", "revise", "archive"}
VALID_STAGES = {"active", "planned", "draft"}
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

def validate_rows(rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    if not rows:
        return ["Input contains no Canvas records."]
    seen_ids: set[str] = set()
    for index, row in enumerate(rows, start=1):
        label = f"row {index}"
        for field in TEXT_FIELDS:
            if field not in row or not str(row[field]).strip():
                errors.append(f"{label}: missing required field '{field}'.")
        for field in NUMERIC_FIELDS:
            if field not in row or str(row[field]).strip() == "":
                errors.append(f"{label}: missing required numeric field '{field}'.")
                continue
            try:
                value = float(row[field])
            except ValueError:
                errors.append(f"{label}: field '{field}' must be numeric.")
                continue
            if not 0.0 <= value <= 1.0:
                errors.append(f"{label}: field '{field}' must be between 0 and 1.")
        record_id = str(row.get("record_id", "")).strip().casefold()
        if record_id:
            if record_id in seen_ids:
                errors.append(f"{label}: duplicate record_id '{row.get('record_id')}'.")
            seen_ids.add(record_id)
        status = str(row.get("status", "")).strip()
        if status and status not in VALID_STATUSES:
            errors.append(f"{label}: status '{status}' must be one of {sorted(VALID_STATUSES)}.")
        stage = str(row.get("article_stage", "")).strip()
        if stage and stage not in VALID_STAGES:
            errors.append(f"{label}: article_stage '{stage}' must be one of {sorted(VALID_STAGES)}.")
        review_date = str(row.get("review_date", "")).strip()
        if review_date and not DATE_PATTERN.match(review_date):
            errors.append(f"{label}: review_date '{review_date}' must use YYYY-MM-DD.")
    return errors

def validate_weights(weights: dict[str, float], tolerance: float = 0.000001) -> None:
    total = sum(weights.values())
    if abs(total - 1.0) > tolerance:
        raise ValueError(f"Weights must sum to 1.0, got {total:.6f}.")
    for name, value in weights.items():
        if value < 0:
            raise ValueError(f"Weight '{name}' cannot be negative.")
