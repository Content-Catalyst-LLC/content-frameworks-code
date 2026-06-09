-- Catalyst Canvas schema for sustainability communication claim governance.

DROP TABLE IF EXISTS sustainability_claims;

CREATE TABLE sustainability_claims (
  claim TEXT PRIMARY KEY,
  claim_type TEXT NOT NULL,
  description TEXT NOT NULL,
  claim_specificity REAL NOT NULL CHECK (claim_specificity BETWEEN 0 AND 1),
  boundary_clarity REAL NOT NULL CHECK (boundary_clarity BETWEEN 0 AND 1),
  evidence_strength REAL NOT NULL CHECK (evidence_strength BETWEEN 0 AND 1),
  materiality_relevance REAL NOT NULL CHECK (materiality_relevance BETWEEN 0 AND 1),
  stakeholder_visibility REAL NOT NULL CHECK (stakeholder_visibility BETWEEN 0 AND 1),
  accountability_coverage REAL NOT NULL CHECK (accountability_coverage BETWEEN 0 AND 1),
  uncertainty_disclosure REAL NOT NULL CHECK (uncertainty_disclosure BETWEEN 0 AND 1),
  promotional_intensity REAL NOT NULL CHECK (promotional_intensity BETWEEN 0 AND 1),
  claim_strength REAL NOT NULL CHECK (claim_strength BETWEEN 0 AND 1),
  owner TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('active', 'review', 'revise', 'archive')),
  review_date TEXT NOT NULL
);

DROP VIEW IF EXISTS sustainability_claim_scores;

CREATE VIEW sustainability_claim_scores AS
SELECT
  claim,
  claim_type,
  description,
  claim_specificity,
  boundary_clarity,
  evidence_strength,
  materiality_relevance,
  stakeholder_visibility,
  accountability_coverage,
  uncertainty_disclosure,
  promotional_intensity,
  claim_strength,
  ROUND((
    claim_specificity
    + boundary_clarity
    + evidence_strength
    + materiality_relevance
    + stakeholder_visibility
    + accountability_coverage
  ) / 6.0, 3) AS quality_score,
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
        (1 - claim_specificity) * 0.25
        + (1 - evidence_strength) * 0.25
        + (1 - boundary_clarity) * 0.20
        + (1 - accountability_coverage) * 0.15
        + promotional_intensity * 0.15
      ) > 1 THEN 1
      ELSE (
        (1 - claim_specificity) * 0.25
        + (1 - evidence_strength) * 0.25
        + (1 - boundary_clarity) * 0.20
        + (1 - accountability_coverage) * 0.15
        + promotional_intensity * 0.15
      )
    END,
    3
  ) AS greenwashing_risk,
  ROUND(
    CASE
      WHEN (
        (CASE WHEN claim_strength - evidence_strength > 0 THEN claim_strength - evidence_strength ELSE 0 END) * 0.35
        + (
          CASE
            WHEN (
              (1 - claim_specificity) * 0.25
              + (1 - evidence_strength) * 0.25
              + (1 - boundary_clarity) * 0.20
              + (1 - accountability_coverage) * 0.15
              + promotional_intensity * 0.15
            ) > 1 THEN 1
            ELSE (
              (1 - claim_specificity) * 0.25
              + (1 - evidence_strength) * 0.25
              + (1 - boundary_clarity) * 0.20
              + (1 - accountability_coverage) * 0.15
              + promotional_intensity * 0.15
            )
          END
        ) * 0.40
        + (1 - stakeholder_visibility) * 0.15
        + (1 - uncertainty_disclosure) * 0.10
      ) > 1 THEN 1
      ELSE (
        (CASE WHEN claim_strength - evidence_strength > 0 THEN claim_strength - evidence_strength ELSE 0 END) * 0.35
        + (
          CASE
            WHEN (
              (1 - claim_specificity) * 0.25
              + (1 - evidence_strength) * 0.25
              + (1 - boundary_clarity) * 0.20
              + (1 - accountability_coverage) * 0.15
              + promotional_intensity * 0.15
            ) > 1 THEN 1
            ELSE (
              (1 - claim_specificity) * 0.25
              + (1 - evidence_strength) * 0.25
              + (1 - boundary_clarity) * 0.20
              + (1 - accountability_coverage) * 0.15
              + promotional_intensity * 0.15
            )
          END
        ) * 0.40
        + (1 - stakeholder_visibility) * 0.15
        + (1 - uncertainty_disclosure) * 0.10
      )
    END,
    3
  ) AS review_priority_score,
  owner,
  status,
  review_date
FROM sustainability_claims;
