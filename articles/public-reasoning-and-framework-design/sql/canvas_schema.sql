-- Catalyst Canvas schema for Public Reasoning and Framework Design governance.

DROP TABLE IF EXISTS public_reasoning_items;

CREATE TABLE public_reasoning_items (
  item TEXT PRIMARY KEY,
  reasoning_type TEXT NOT NULL,
  description TEXT NOT NULL,
  claim_clarity REAL NOT NULL CHECK (claim_clarity BETWEEN 0 AND 1),
  evidence_visibility REAL NOT NULL CHECK (evidence_visibility BETWEEN 0 AND 1),
  value_transparency REAL NOT NULL CHECK (value_transparency BETWEEN 0 AND 1),
  tradeoff_clarity REAL NOT NULL CHECK (tradeoff_clarity BETWEEN 0 AND 1),
  stakeholder_inclusion REAL NOT NULL CHECK (stakeholder_inclusion BETWEEN 0 AND 1),
  uncertainty_disclosure REAL NOT NULL CHECK (uncertainty_disclosure BETWEEN 0 AND 1),
  participation_fit REAL NOT NULL CHECK (participation_fit BETWEEN 0 AND 1),
  accountability REAL NOT NULL CHECK (accountability BETWEEN 0 AND 1),
  transparency REAL NOT NULL CHECK (transparency BETWEEN 0 AND 1),
  owner TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('active', 'review', 'revise', 'archive')),
  review_date TEXT NOT NULL
);

DROP VIEW IF EXISTS public_reasoning_scores;

CREATE VIEW public_reasoning_scores AS
SELECT
  item,
  reasoning_type,
  description,
  claim_clarity,
  evidence_visibility,
  value_transparency,
  tradeoff_clarity,
  stakeholder_inclusion,
  uncertainty_disclosure,
  participation_fit,
  accountability,
  transparency,
  ROUND((
    claim_clarity
    + evidence_visibility
    + value_transparency
    + tradeoff_clarity
    + stakeholder_inclusion
    + uncertainty_disclosure
    + participation_fit
    + accountability
    + transparency
  ) / 9.0, 3) AS quality_score,
  ROUND(
    CASE
      WHEN (
        (1 - participation_fit) * 0.25
        + (1 - stakeholder_inclusion) * 0.25
        + (1 - transparency) * 0.25
        + (1 - accountability) * 0.25
      ) > 1 THEN 1
      ELSE (
        (1 - participation_fit) * 0.25
        + (1 - stakeholder_inclusion) * 0.25
        + (1 - transparency) * 0.25
        + (1 - accountability) * 0.25
      )
    END,
    3
  ) AS legitimacy_risk,
  ROUND(
    CASE
      WHEN (
        (1 - (
          claim_clarity
          + evidence_visibility
          + value_transparency
          + tradeoff_clarity
          + stakeholder_inclusion
          + uncertainty_disclosure
          + participation_fit
          + accountability
          + transparency
        ) / 9.0) * 0.50
        + (
          CASE
            WHEN (
              (1 - participation_fit) * 0.25
              + (1 - stakeholder_inclusion) * 0.25
              + (1 - transparency) * 0.25
              + (1 - accountability) * 0.25
            ) > 1 THEN 1
            ELSE (
              (1 - participation_fit) * 0.25
              + (1 - stakeholder_inclusion) * 0.25
              + (1 - transparency) * 0.25
              + (1 - accountability) * 0.25
            )
          END
        ) * 0.50
      ) > 1 THEN 1
      ELSE (
        (1 - (
          claim_clarity
          + evidence_visibility
          + value_transparency
          + tradeoff_clarity
          + stakeholder_inclusion
          + uncertainty_disclosure
          + participation_fit
          + accountability
          + transparency
        ) / 9.0) * 0.50
        + (
          CASE
            WHEN (
              (1 - participation_fit) * 0.25
              + (1 - stakeholder_inclusion) * 0.25
              + (1 - transparency) * 0.25
              + (1 - accountability) * 0.25
            ) > 1 THEN 1
            ELSE (
              (1 - participation_fit) * 0.25
              + (1 - stakeholder_inclusion) * 0.25
              + (1 - transparency) * 0.25
              + (1 - accountability) * 0.25
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
FROM public_reasoning_items;
