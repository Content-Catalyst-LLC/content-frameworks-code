# Validation helpers for logic-model and Theory of Change inputs.

from __future__ import annotations

import re

REQUIRED_TEXT_FIELDS = ["element", "model_layer", "description", "owner", "status", "review_date"]
REQUIRED_NUMERIC_FIELDS = [
    "evidence_strength",
    "assumption_importance",
    "assumption_evidence",
    "measurement_coverage",
    "outcome_clarity",
    "claim_strength",
]
VALID_MODEL_LAYERS = {"input", "activity", "output", "outcome", "impact", "assumption", "causal link", "indicator"}
VALID_STATUSES = {"active", "review", "revise", "archive"}
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validate_rows(rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    if not rows:
        return ["Input contains no logic-model elements."]

    seen: set[str] = set()
    for index, row in enumerate(rows, start=1):
        label = f"row {index}"

        for field in REQUIRED_TEXT_FIELDS:
            if field not in row or not str(row[field]).strip():
                errors.append(f"{label}: missing required text field '{field}'.")

        for field in REQUIRED_NUMERIC_FIELDS:
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

        element = str(row.get("element", "")).strip()
        if element:
            normalized = element.casefold()
            if normalized in seen:
                errors.append(f"{label}: duplicate element '{element}'.")
            seen.add(normalized)

        model_layer = str(row.get("model_layer", "")).strip()
        if model_layer and model_layer not in VALID_MODEL_LAYERS:
            errors.append(f"{label}: model_layer '{model_layer}' must be one of {sorted(VALID_MODEL_LAYERS)}.")

        status = str(row.get("status", "")).strip()
        if status and status not in VALID_STATUSES:
            errors.append(f"{label}: status '{status}' must be one of {sorted(VALID_STATUSES)}.")

        review_date = str(row.get("review_date", "")).strip()
        if review_date and not DATE_PATTERN.match(review_date):
            errors.append(f"{label}: review_date '{review_date}' must use YYYY-MM-DD.")

    return errors
