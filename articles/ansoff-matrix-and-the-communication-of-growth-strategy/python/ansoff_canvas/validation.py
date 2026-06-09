"""Validation helpers for Ansoff Matrix Catalyst Canvas inputs."""

from __future__ import annotations

import re


REQUIRED_TEXT_FIELDS = [
    "option",
    "growth_path",
    "market_status",
    "product_status",
    "description",
    "owner",
    "status",
    "review_date",
]

REQUIRED_NUMERIC_FIELDS = [
    "strategic_fit",
    "evidence_strength",
    "feasibility",
    "capability_readiness",
    "expected_value",
    "market_familiarity",
    "product_familiarity",
    "uncertainty",
    "claim_strength",
]

VALID_GROWTH_PATHS = {
    "market penetration",
    "market development",
    "product development",
    "diversification",
    "unclear",
}
VALID_MARKET_STATUSES = {"existing", "new"}
VALID_PRODUCT_STATUSES = {"existing", "new"}
VALID_STATUSES = {"active", "review", "revise", "archive"}
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

EXPECTED_PATH = {
    ("existing", "existing"): "market penetration",
    ("new", "existing"): "market development",
    ("existing", "new"): "product development",
    ("new", "new"): "diversification",
}


def validate_rows(rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []

    if not rows:
        return ["Input contains no Ansoff growth options."]

    seen_options: set[str] = set()

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

        option = str(row.get("option", "")).strip()
        if option:
            normalized = option.casefold()
            if normalized in seen_options:
                errors.append(f"{row_label}: duplicate option '{option}'.")
            seen_options.add(normalized)

        growth_path = str(row.get("growth_path", "")).strip()
        if growth_path and growth_path not in VALID_GROWTH_PATHS:
            errors.append(f"{row_label}: growth_path '{growth_path}' must be one of {sorted(VALID_GROWTH_PATHS)}.")

        market_status = str(row.get("market_status", "")).strip()
        if market_status and market_status not in VALID_MARKET_STATUSES:
            errors.append(f"{row_label}: market_status '{market_status}' must be existing or new.")

        product_status = str(row.get("product_status", "")).strip()
        if product_status and product_status not in VALID_PRODUCT_STATUSES:
            errors.append(f"{row_label}: product_status '{product_status}' must be existing or new.")

        if market_status in VALID_MARKET_STATUSES and product_status in VALID_PRODUCT_STATUSES and growth_path != "unclear":
            expected = EXPECTED_PATH[(market_status, product_status)]
            if growth_path != expected:
                errors.append(
                    f"{row_label}: growth_path '{growth_path}' does not match market/product status; expected '{expected}'."
                )

        status = str(row.get("status", "")).strip()
        if status and status not in VALID_STATUSES:
            errors.append(f"{row_label}: status '{status}' must be one of {sorted(VALID_STATUSES)}.")

        review_date = str(row.get("review_date", "")).strip()
        if review_date and not DATE_PATTERN.match(review_date):
            errors.append(f"{row_label}: review_date '{review_date}' must use YYYY-MM-DD.")

    return errors
