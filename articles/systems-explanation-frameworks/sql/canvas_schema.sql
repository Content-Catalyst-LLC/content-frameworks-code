-- Catalyst Canvas schema for Systems Explanation governance.

DROP TABLE IF EXISTS systems_explanation_items;

CREATE TABLE systems_explanation_items (
  item TEXT PRIMARY KEY,
  explanation_type TEXT NOT NULL,
  description TEXT NOT NULL,
  boundary_clarity REAL NOT NULL CHECK (boundary_clarity BETWEEN 0 AND 1),
  actor_coverage REAL NOT NULL CHECK (actor_coverage BETWEEN 0 AND 1),
  relationship_clarity REAL NOT NULL CHECK (relationship_clarity BETWEEN 0 AND 1),
  feedback_visibility REAL NOT NULL CHECK (feedback_visibility BETWEEN 0 AND 1),
  delay_visibility REAL NOT NULL CHECK (delay_visibility BETWEEN 0 AND 1),
  stock_flow_clarity REAL NOT NULL CHECK (stock_flow_clarity BETWEEN 0 AND 1),
  stakeholder_visibility REAL NOT NULL CHECK (stakeholder_visibility BETWEEN 0 AND 1),
  evidence_strength REAL NOT NULL CHECK (evidence_strength BETWEEN 0 AND 1),
  leverage_readiness REAL NOT NULL CHECK (leverage_readiness BETWEEN 0 AND 1),
  owner TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('active', 'review', 'revise', 'archive')),
  review_date TEXT NOT NULL
);

DROP VIEW IF EXISTS systems_explanation_scores;

CREATE VIEW systems_explanation_scores AS
SELECT
  item,
  explanation_type,
  description,
  boundary_clarity,
  actor_coverage,
  relationship_clarity,
  feedback_visibility,
  delay_visibility,
  stock_flow_clarity,
  stakeholder_visibility,
  evidence_strength,
  leverage_readiness,
  ROUND((
    boundary_clarity
    + actor_coverage
    + relationship_clarity
    + feedback_visibility
    + delay_visibility
    + stock_flow_clarity
    + stakeholder_visibility
    + evidence_strength
    + leverage_readiness
  ) / 9.0, 3) AS quality_score,
  ROUND(
    CASE
      WHEN (
        (1 - boundary_clarity) * 0.30
        + (1 - relationship_clarity) * 0.30
        + (1 - evidence_strength) * 0.25
        + (1 - feedback_visibility) * 0.15
      ) > 1 THEN 1
      ELSE (
        (1 - boundary_clarity) * 0.30
        + (1 - relationship_clarity) * 0.30
        + (1 - evidence_strength) * 0.25
        + (1 - feedback_visibility) * 0.15
      )
    END,
    3
  ) AS systems_ambiguity,
  ROUND(
    CASE
      WHEN (
        (
          CASE
            WHEN (
              (1 - boundary_clarity) * 0.30
              + (1 - relationship_clarity) * 0.30
              + (1 - evidence_strength) * 0.25
              + (1 - feedback_visibility) * 0.15
            ) > 1 THEN 1
            ELSE (
              (1 - boundary_clarity) * 0.30
              + (1 - relationship_clarity) * 0.30
              + (1 - evidence_strength) * 0.25
              + (1 - feedback_visibility) * 0.15
            )
          END
        ) * 0.40
        + (1 - leverage_readiness) * 0.25
        + (1 - stakeholder_visibility) * 0.20
        + (1 - delay_visibility) * 0.15
      ) > 1 THEN 1
      ELSE (
        (
          CASE
            WHEN (
              (1 - boundary_clarity) * 0.30
              + (1 - relationship_clarity) * 0.30
              + (1 - evidence_strength) * 0.25
              + (1 - feedback_visibility) * 0.15
            ) > 1 THEN 1
            ELSE (
              (1 - boundary_clarity) * 0.30
              + (1 - relationship_clarity) * 0.30
              + (1 - evidence_strength) * 0.25
              + (1 - feedback_visibility) * 0.15
            )
          END
        ) * 0.40
        + (1 - leverage_readiness) * 0.25
        + (1 - stakeholder_visibility) * 0.20
        + (1 - delay_visibility) * 0.15
      )
    END,
    3
  ) AS review_priority_score,
  owner,
  status,
  review_date
FROM systems_explanation_items;
