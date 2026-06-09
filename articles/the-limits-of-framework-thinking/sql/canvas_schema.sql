-- Catalyst Canvas schema for The Limits of Framework Thinking governance.

DROP TABLE IF EXISTS framework_limits_items;

CREATE TABLE framework_limits_items (
  item TEXT PRIMARY KEY,
  framework_type TEXT NOT NULL,
  description TEXT NOT NULL,
  clarity REAL NOT NULL CHECK (clarity BETWEEN 0 AND 1),
  fit REAL NOT NULL CHECK (fit BETWEEN 0 AND 1),
  evidence_alignment REAL NOT NULL CHECK (evidence_alignment BETWEEN 0 AND 1),
  assumption_transparency REAL NOT NULL CHECK (assumption_transparency BETWEEN 0 AND 1),
  governance_readiness REAL NOT NULL CHECK (governance_readiness BETWEEN 0 AND 1),
  oversimplification_risk REAL NOT NULL CHECK (oversimplification_risk BETWEEN 0 AND 1),
  false_precision_risk REAL NOT NULL CHECK (false_precision_risk BETWEEN 0 AND 1),
  context_loss REAL NOT NULL CHECK (context_loss BETWEEN 0 AND 1),
  audience_burden REAL NOT NULL CHECK (audience_burden BETWEEN 0 AND 1),
  value_opacity REAL NOT NULL CHECK (value_opacity BETWEEN 0 AND 1),
  owner TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('active', 'review', 'revise', 'archive')),
  review_date TEXT NOT NULL
);

DROP VIEW IF EXISTS framework_limits_scores;

CREATE VIEW framework_limits_scores AS
SELECT
  item,
  framework_type,
  description,
  clarity,
  fit,
  evidence_alignment,
  assumption_transparency,
  governance_readiness,
  oversimplification_risk,
  false_precision_risk,
  context_loss,
  audience_burden,
  value_opacity,
  ROUND((
    clarity
    + fit
    + evidence_alignment
    + assumption_transparency
    + governance_readiness
  ) / 5.0, 3) AS usefulness_score,
  ROUND(
    CASE
      WHEN (
        oversimplification_risk * 0.22
        + false_precision_risk * 0.22
        + context_loss * 0.20
        + audience_burden * 0.18
        + value_opacity * 0.18
      ) > 1 THEN 1
      ELSE (
        oversimplification_risk * 0.22
        + false_precision_risk * 0.22
        + context_loss * 0.20
        + audience_burden * 0.18
        + value_opacity * 0.18
      )
    END,
    3
  ) AS distortion_risk,
  ROUND(
    CASE
      WHEN (
        (1 - (
          clarity
          + fit
          + evidence_alignment
          + assumption_transparency
          + governance_readiness
        ) / 5.0) * 0.50
        + (
          CASE
            WHEN (
              oversimplification_risk * 0.22
              + false_precision_risk * 0.22
              + context_loss * 0.20
              + audience_burden * 0.18
              + value_opacity * 0.18
            ) > 1 THEN 1
            ELSE (
              oversimplification_risk * 0.22
              + false_precision_risk * 0.22
              + context_loss * 0.20
              + audience_burden * 0.18
              + value_opacity * 0.18
            )
          END
        ) * 0.50
      ) > 1 THEN 1
      ELSE (
        (1 - (
          clarity
          + fit
          + evidence_alignment
          + assumption_transparency
          + governance_readiness
        ) / 5.0) * 0.50
        + (
          CASE
            WHEN (
              oversimplification_risk * 0.22
              + false_precision_risk * 0.22
              + context_loss * 0.20
              + audience_burden * 0.18
              + value_opacity * 0.18
            ) > 1 THEN 1
            ELSE (
              oversimplification_risk * 0.22
              + false_precision_risk * 0.22
              + context_loss * 0.20
              + audience_burden * 0.18
              + value_opacity * 0.18
            )
          END
        ) * 0.50
      )
    END,
    3
  ) AS review_priority_score,
  owner,
  status,
  review_date
FROM framework_limits_items;
