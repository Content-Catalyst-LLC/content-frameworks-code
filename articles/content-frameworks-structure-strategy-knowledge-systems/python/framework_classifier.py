"""
Content Frameworks: Framework Library Classifier

Educational example for organizing a framework library by function.
"""

from __future__ import annotations

import pandas as pd


def compute_framework_profile(row: pd.Series) -> float:
    """Compute a stylized framework usefulness profile."""
    return (
        0.22 * row["complexity_level"]
        + 0.20 * row["transferability"]
        - 0.12 * row["ethical_risk"]
        + 0.24 * row["knowledge_depth"]
        + 0.22 * row["action_support"]
    )


def main() -> None:
    frameworks = pd.read_csv("../data/framework_library.csv")
    frameworks["framework_profile"] = frameworks.apply(compute_framework_profile, axis=1)

    frameworks["requires_caution"] = (
        (frameworks["ethical_risk"] > 0.50)
        | (frameworks["knowledge_depth"] < 0.50)
    )

    frameworks = frameworks.sort_values("framework_profile", ascending=False)

    print(frameworks)

    frameworks.to_csv("../outputs/framework_library_scored.csv", index=False)


if __name__ == "__main__":
    main()
