"""Validation helpers for SWOT Analysis Catalyst Canvas inputs."""

from __future__ import annotations

import re


REQUIRED_TEXT_FIELDS = [
    "item",
    "quadrant",
    "orientation",
    "description",
    "owner",
    "status",
    "review_date",
]

REQUIRED_NUMERIC_FIELDS = [
    "impact",
    "confidence",
    "urgency",
    "feasibility",
    "strategic_fit",
    "evidence_strength",
    "claim_strength",
]

VALID_QUADRANTS = {"strength", "weakness", "opportunity", "threat"}
VALID_ORIENTATIONS = {"internal", "external"}
VALID_STATUSES = {"active", "review", "revise", "archive"}
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

EXPECTED_ORIENTATION = {
    "strength": "internal",
    "weakness": "internal",
    "opportunity": "external",
    "threat": "external",
}


def validate_rows(rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []

    if not rows:
        return ["Input contains no SWOT items."]

    seen_items: set[str] = set()

    for index, row in enumerate(rows, start=1):
        row_label = f"row {index}"

        for field in REQUIRED_TEXT_FIELDS:
            if field not in row or not str(row[field]).strip():
                errors.append(f"{row_label}: missing required text field '{field}'.")

        for field in REQUIRED_NUMERIC_FIELDS:
            if field not in row or str(row[field]).strip() == "":
                errors.append(f"{row_label}: missing required numeric field '{field}'.")
                continue

            try:
                value = float(row[field])
            except ValueError:
                errors.append(f"{row_label}: field '{field}' must be numeric.")
                continue

            if not 0.0 <= value <= 1.0:
                errors.append(f"{row_label}: field '{field}' must be between 0 and 1.")

        item = str(row.get("item", "")).strip()
        if item:
            normalized = item.casefold()
            if normalized in seen_items:
                errors.append(f"{row_label}: duplicate item '{item}'.")
            seen_items.add(normalized)

        quadrant = str(row.get("quadrant", "")).strip()
        orientation = str(row.get("orientation", "")).strip()

        if quadrant and quadrant not in VALID_QUADRANTS:
            errors.append(f"{row_label}: quadrant '{quadrant}' must be one of {sorted(VALID_QUADRANTS)}.")

        if orientation and orientation not in VALID_ORIENTATIONS:
            errors.append(f"{row_label}: orientation '{orientation}' must be one of {sorted(VALID_ORIENTATIONS)}.")

        if quadrant in EXPECTED_ORIENTATION and orientation:
            expected = EXPECTED_ORIENTATION[quadrant]
            if orientation != expected:
                errors.append(f"{row_label}: quadrant '{quadrant}' should use orientation '{expected}'.")

        status = str(row.get("status", "")).strip()
        if status and status not in VALID_STATUSES:
            errors.append(f"{row_label}: status '{status}' must be one of {sorted(VALID_STATUSES)}.")

        review_date = str(row.get("review_date", "")).strip()
        if review_date and not DATE_PATTERN.match(review_date):
            errors.append(f"{row_label}: review_date '{review_date}' must use YYYY-MM-DD.")

    return errors


def validate_weights(weights: dict[str, float], tolerance: float = 0.000001) -> None:
    total = sum(weights.values())
    if abs(total - 1.0) > tolerance:
        raise ValueError(f"Weights must sum to 1.0, got {total:.6f}.")

    for key, value in weights.items():
        if value < 0:
            raise ValueError(f"Weight '{key}' cannot be negative.")
