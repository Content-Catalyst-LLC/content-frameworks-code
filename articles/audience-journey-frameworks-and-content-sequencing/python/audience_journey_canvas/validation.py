"""Validation helpers for Audience Journey Catalyst Canvas inputs."""

from __future__ import annotations

import re


REQUIRED_TEXT_FIELDS = [
    "stage",
    "audience_need",
    "journey_type",
    "owner",
    "status",
    "review_date",
]

REQUIRED_NUMERIC_FIELDS = [
    "stage_clarity",
    "content_coverage",
    "transition_quality",
    "evidence_readiness",
    "governance_readiness",
    "persona_fit",
    "staleness_risk",
]

REQUIRED_INTEGER_FIELDS = [
    "required_links",
    "available_links",
]

VALID_STATUSES = {"active", "review", "revise", "archive"}
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validate_rows(rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []

    if not rows:
        return ["Input contains no journey stage records."]

    seen_stages: set[str] = set()

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

        for field in REQUIRED_INTEGER_FIELDS:
            if field not in row or str(row[field]).strip() == "":
                errors.append(f"{row_label}: missing required integer field '{field}'.")
                continue

            try:
                value = int(row[field])
            except ValueError:
                errors.append(f"{row_label}: field '{field}' must be an integer.")
                continue

            if value < 0:
                errors.append(f"{row_label}: field '{field}' cannot be negative.")

        stage = str(row.get("stage", "")).strip()
        if stage:
            normalized = stage.casefold()
            if normalized in seen_stages:
                errors.append(f"{row_label}: duplicate stage '{stage}'.")
            seen_stages.add(normalized)

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
