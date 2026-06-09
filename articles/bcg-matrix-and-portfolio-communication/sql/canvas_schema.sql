-- Catalyst Canvas schema for BCG Matrix portfolio diagnostics.

DROP TABLE IF EXISTS bcg_portfolio_items;

CREATE TABLE bcg_portfolio_items (
  item TEXT PRIMARY KEY,
  portfolio_area TEXT NOT NULL,
  description TEXT NOT NULL,
  growth_score REAL NOT NULL CHECK (growth_score BETWEEN 0 AND 1),
  relative_share_score REAL NOT NULL CHECK (relative_share_score BETWEEN 0 AND 1),
  evidence_strength REAL NOT NULL CHECK (evidence_strength BETWEEN 0 AND 1),
  strategic_fit REAL NOT NULL CHECK (strategic_fit BETWEEN 0 AND 1),
  maintenance_burden REAL NOT NULL CHECK (maintenance_burden BETWEEN 0 AND 1),
  claim_strength REAL NOT NULL CHECK (claim_strength BETWEEN 0 AND 1),
  owner TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('active', 'review', 'revise', 'archive')),
  review_date TEXT NOT NULL
);

DROP VIEW IF EXISTS bcg_scores;

CREATE VIEW bcg_scores AS
SELECT
  item,
  portfolio_area,
  description,
  growth_score,
  relative_share_score,
  evidence_strength,
  strategic_fit,
  maintenance_burden,
  claim_strength,
  CASE
    WHEN growth_score >= 0.60 AND relative_share_score >= 0.60 THEN 'star'
    WHEN growth_score < 0.60 AND relative_share_score >= 0.60 THEN 'cash_cow'
    WHEN growth_score >= 0.60 AND relative_share_score < 0.60 THEN 'question_mark'
    ELSE 'review_quadrant'
  END AS quadrant,
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
        CASE
          WHEN growth_score >= 0.60 AND relative_share_score >= 0.60 THEN 0.85
          WHEN growth_score < 0.60 AND relative_share_score >= 0.60 THEN 0.60
          WHEN growth_score >= 0.60 AND relative_share_score < 0.60 THEN 0.78
          ELSE 0.70
        END
      ) * 0.35
      + strategic_fit * 0.30
      + maintenance_burden * 0.15
      + (
        CASE
          WHEN claim_strength - evidence_strength > 0 THEN claim_strength - evidence_strength
          ELSE 0
        END
      ) * 0.20 > 1 THEN 1
      ELSE (
        CASE
          WHEN growth_score >= 0.60 AND relative_share_score >= 0.60 THEN 0.85
          WHEN growth_score < 0.60 AND relative_share_score >= 0.60 THEN 0.60
          WHEN growth_score >= 0.60 AND relative_share_score < 0.60 THEN 0.78
          ELSE 0.70
        END
      ) * 0.35
      + strategic_fit * 0.30
      + maintenance_burden * 0.15
      + (
        CASE
          WHEN claim_strength - evidence_strength > 0 THEN claim_strength - evidence_strength
          ELSE 0
        END
      ) * 0.20
    END,
    3
  ) AS portfolio_priority,
  owner,
  status,
  review_date
FROM bcg_portfolio_items;
