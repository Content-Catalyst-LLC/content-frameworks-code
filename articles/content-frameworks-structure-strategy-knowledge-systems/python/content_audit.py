"""
Content Frameworks: Content Audit Workflow

Educational workflow for scoring article completeness and identifying
maintenance priorities.
"""

from __future__ import annotations

import pandas as pd


def score_article(row: pd.Series) -> float:
    """Compute a simple editorial completeness score."""
    word_score = min(row["word_count"] / 3000.0, 1.0)
    link_score = min(row["internal_links"] / 10.0, 1.0)
    reference_score = min(row["references"] / 10.0, 1.0)

    metadata_score = (
        0.34 * float(row["has_image_metadata"])
        + 0.33 * float(row["has_excerpt"])
        + 0.33 * float(row["has_repository_link"])
    )

    return (
        0.30 * word_score
        + 0.25 * link_score
        + 0.25 * reference_score
        + 0.20 * metadata_score
    )


def main() -> None:
    audit = pd.read_csv("../data/content_audit.csv")
    audit["completion_score"] = audit.apply(score_article, axis=1)

    audit["needs_review"] = (
        (audit["completion_score"] < 0.75)
        | (audit["internal_links"] < 6)
        | (audit["references"] < 6)
    )

    audit = audit.sort_values("completion_score", ascending=True)

    print(audit)

    audit.to_csv("../outputs/content_audit_scores.csv", index=False)


if __name__ == "__main__":
    main()
