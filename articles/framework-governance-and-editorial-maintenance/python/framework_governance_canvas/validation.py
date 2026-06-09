"""Validation helpers for Framework Governance Catalyst Canvas inputs."""

from __future__ import annotations

import re


REQUIRED_TEXT_FIELDS = [
    "item",
    "item_type",
    "description",
    "owner",
    "status",
    "review_date",
]

REQUIRED_NUMERIC_FIELDS = [
    "ownership_clarity",
    "review_cycle_strength",
    "metadata_completeness",
    "evidence_status",
    "link_health",
    "taxonomy_alignment",
    "platform_readiness",
    "stale_evidence_risk",
    "dependency_complexity",
    "audience_impact",
]

VALID_STATUSES = {"active", "review", "revise", "archive"}
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validate_rows(rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []

    if not rows:
        return ["Input contains no framework governance items."]

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

        status = str(row.get("status", "")).strip()
        if status and status not in VALID_STATUSES:
            errors.append(f"{row_label}: status '{status}' must be one of {sorted(VALID_STATUSES)}.")

        review_date = str(row.get("review_date", "")).strip()
        if review_date and not DATE_PATTERN.match(review_date):
            errors.append(f"{row_label}: review_date '{review_date}' must use YYYY-MM-DD.")

    return errors
