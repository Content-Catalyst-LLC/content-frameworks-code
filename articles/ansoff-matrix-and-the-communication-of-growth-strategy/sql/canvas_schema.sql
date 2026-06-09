-- Catalyst Canvas schema for Ansoff Matrix growth diagnostics.

DROP TABLE IF EXISTS ansoff_growth_options;

CREATE TABLE ansoff_growth_options (
  option TEXT PRIMARY KEY,
  growth_path TEXT NOT NULL CHECK (growth_path IN ('market penetration', 'market development', 'product development', 'diversification', 'unclear')),
  market_status TEXT NOT NULL CHECK (market_status IN ('existing', 'new')),
  product_status TEXT NOT NULL CHECK (product_status IN ('existing', 'new')),
  description TEXT NOT NULL,
  strategic_fit REAL NOT NULL CHECK (strategic_fit BETWEEN 0 AND 1),
  evidence_strength REAL NOT NULL CHECK (evidence_strength BETWEEN 0 AND 1),
  feasibility REAL NOT NULL CHECK (feasibility BETWEEN 0 AND 1),
  capability_readiness REAL NOT NULL CHECK (capability_readiness BETWEEN 0 AND 1),
  expected_value REAL NOT NULL CHECK (expected_value BETWEEN 0 AND 1),
  market_familiarity REAL NOT NULL CHECK (market_familiarity BETWEEN 0 AND 1),
  product_familiarity REAL NOT NULL CHECK (product_familiarity BETWEEN 0 AND 1),
  uncertainty REAL NOT NULL CHECK (uncertainty BETWEEN 0 AND 1),
  claim_strength REAL NOT NULL CHECK (claim_strength BETWEEN 0 AND 1),
  owner TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('active', 'review', 'revise', 'archive')),
  review_date TEXT NOT NULL
);

DROP VIEW IF EXISTS ansoff_scores;

CREATE VIEW ansoff_scores AS
SELECT
  option,
  growth_path,
  market_status,
  product_status,
  description,
  ROUND((strategic_fit + evidence_strength + feasibility + capability_readiness) / 4.0, 3) AS readiness_score,
  ROUND(
    CASE
      WHEN ((1 - market_familiarity) + (1 - product_familiarity) + uncertainty) / 3.0 > 1 THEN 1
      ELSE ((1 - market_familiarity) + (1 - product_familiarity) + uncertainty) / 3.0
    END,
    3
  ) AS risk_score,
  ROUND(
    CASE
      WHEN claim_strength - evidence_strength > 0 THEN claim_strength - evidence_strength
      ELSE 0
    END,
    3
  ) AS evidence_gap,
  ROUND(
    CASE
      WHEN (
        ((strategic_fit + evidence_strength + feasibility + capability_readiness) / 4.0) * 0.55
        + expected_value * 0.35
        - (
          CASE
            WHEN ((1 - market_familiarity) + (1 - product_familiarity) + uncertainty) / 3.0 > 1 THEN 1
            ELSE ((1 - market_familiarity) + (1 - product_familiarity) + uncertainty) / 3.0
          END
        ) * 0.20
      ) < 0 THEN 0
      WHEN (
        ((strategic_fit + evidence_strength + feasibility + capability_readiness) / 4.0) * 0.55
        + expected_value * 0.35
        - (
          CASE
            WHEN ((1 - market_familiarity) + (1 - product_familiarity) + uncertainty) / 3.0 > 1 THEN 1
            ELSE ((1 - market_familiarity) + (1 - product_familiarity) + uncertainty) / 3.0
          END
        ) * 0.20
      ) > 1 THEN 1
      ELSE (
        ((strategic_fit + evidence_strength + feasibility + capability_readiness) / 4.0) * 0.55
        + expected_value * 0.35
        - (
          CASE
            WHEN ((1 - market_familiarity) + (1 - product_familiarity) + uncertainty) / 3.0 > 1 THEN 1
            ELSE ((1 - market_familiarity) + (1 - product_familiarity) + uncertainty) / 3.0
          END
        ) * 0.20
      )
    END,
    3
  ) AS growth_quality,
  ROUND(
    CASE
      WHEN (
        (
          CASE
            WHEN ((1 - market_familiarity) + (1 - product_familiarity) + uncertainty) / 3.0 > 1 THEN 1
            ELSE ((1 - market_familiarity) + (1 - product_familiarity) + uncertainty) / 3.0
          END
        ) * 0.35
        + (
          CASE
            WHEN claim_strength - evidence_strength > 0 THEN claim_strength - evidence_strength
            ELSE 0
          END
        ) * 0.40
        + (1 - feasibility) * 0.25
      ) > 1 THEN 1
      ELSE (
        (
          CASE
            WHEN ((1 - market_familiarity) + (1 - product_familiarity) + uncertainty) / 3.0 > 1 THEN 1
            ELSE ((1 - market_familiarity) + (1 - product_familiarity) + uncertainty) / 3.0
          END
        ) * 0.35
        + (
          CASE
            WHEN claim_strength - evidence_strength > 0 THEN claim_strength - evidence_strength
            ELSE 0
          END
        ) * 0.40
        + (1 - feasibility) * 0.25
      )
    END,
    3
  ) AS governance_priority,
  owner,
  status,
  review_date
FROM ansoff_growth_options;
