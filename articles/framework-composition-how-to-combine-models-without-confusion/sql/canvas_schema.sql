-- Catalyst Canvas schema for Framework Composition governance.

DROP TABLE IF EXISTS framework_composition_items;

CREATE TABLE framework_composition_items (
  item TEXT PRIMARY KEY,
  composition_type TEXT NOT NULL,
  description TEXT NOT NULL,
  purpose_fit REAL NOT NULL CHECK (purpose_fit BETWEEN 0 AND 1),
  role_clarity REAL NOT NULL CHECK (role_clarity BETWEEN 0 AND 1),
  boundary_clarity REAL NOT NULL CHECK (boundary_clarity BETWEEN 0 AND 1),
  sequence_clarity REAL NOT NULL CHECK (sequence_clarity BETWEEN 0 AND 1),
  translation_quality REAL NOT NULL CHECK (translation_quality BETWEEN 0 AND 1),
  evidence_alignment REAL NOT NULL CHECK (evidence_alignment BETWEEN 0 AND 1),
  governance_readiness REAL NOT NULL CHECK (governance_readiness BETWEEN 0 AND 1),
  audience_burden REAL NOT NULL CHECK (audience_burden BETWEEN 0 AND 1),
  conflict_risk REAL NOT NULL CHECK (conflict_risk BETWEEN 0 AND 1),
  owner TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('active', 'review', 'revise', 'archive')),
  review_date TEXT NOT NULL
);

DROP VIEW IF EXISTS framework_composition_scores;

CREATE VIEW framework_composition_scores AS
SELECT
  item,
  composition_type,
  description,
  purpose_fit,
  role_clarity,
  boundary_clarity,
  sequence_clarity,
  translation_quality,
  evidence_alignment,
  governance_readiness,
  audience_burden,
  conflict_risk,
  ROUND((
    purpose_fit
    + role_clarity
    + boundary_clarity
    + sequence_clarity
    + translation_quality
    + evidence_alignment
    + governance_readiness
  ) / 7.0, 3) AS quality_score,
  ROUND(
    CASE
      WHEN (
        (1 - role_clarity) * 0.25
        + audience_burden * 0.25
        + (1 - translation_quality) * 0.25
        + conflict_risk * 0.25
      ) > 1 THEN 1
      ELSE (
        (1 - role_clarity) * 0.25
        + audience_burden * 0.25
        + (1 - translation_quality) * 0.25
        + conflict_risk * 0.25
      )
    END,
    3
  ) AS confusion_risk,
  ROUND(
    CASE
      WHEN (
        (1 - (
          purpose_fit
          + role_clarity
          + boundary_clarity
          + sequence_clarity
          + translation_quality
          + evidence_alignment
          + governance_readiness
        ) / 7.0) * 0.50
        + (
          CASE
            WHEN (
              (1 - role_clarity) * 0.25
              + audience_burden * 0.25
              + (1 - translation_quality) * 0.25
              + conflict_risk * 0.25
            ) > 1 THEN 1
            ELSE (
              (1 - role_clarity) * 0.25
              + audience_burden * 0.25
              + (1 - translation_quality) * 0.25
              + conflict_risk * 0.25
            )
          END
        ) * 0.50
      ) > 1 THEN 1
      ELSE (
        (1 - (
          purpose_fit
          + role_clarity
          + boundary_clarity
          + sequence_clarity
          + translation_quality
          + evidence_alignment
          + governance_readiness
        ) / 7.0) * 0.50
        + (
          CASE
            WHEN (
              (1 - role_clarity) * 0.25
              + audience_burden * 0.25
              + (1 - translation_quality) * 0.25
              + conflict_risk * 0.25
            ) > 1 THEN 1
            ELSE (
              (1 - role_clarity) * 0.25
              + audience_burden * 0.25
              + (1 - translation_quality) * 0.25
              + conflict_risk * 0.25
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
FROM framework_composition_items;
