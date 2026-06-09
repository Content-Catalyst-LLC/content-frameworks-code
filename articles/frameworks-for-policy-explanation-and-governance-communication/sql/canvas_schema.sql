-- Catalyst Canvas schema for policy explanation and governance communication diagnostics.

DROP TABLE IF EXISTS policy_governance_items;

CREATE TABLE policy_governance_items (
  item TEXT PRIMARY KEY,
  policy_area TEXT NOT NULL,
  description TEXT NOT NULL,
  problem_clarity REAL NOT NULL CHECK (problem_clarity BETWEEN 0 AND 1),
  authority_clarity REAL NOT NULL CHECK (authority_clarity BETWEEN 0 AND 1),
  evidence_strength REAL NOT NULL CHECK (evidence_strength BETWEEN 0 AND 1),
  stakeholder_visibility REAL NOT NULL CHECK (stakeholder_visibility BETWEEN 0 AND 1),
  implementation_detail REAL NOT NULL CHECK (implementation_detail BETWEEN 0 AND 1),
  accountability_coverage REAL NOT NULL CHECK (accountability_coverage BETWEEN 0 AND 1),
  participation_clarity REAL NOT NULL CHECK (participation_clarity BETWEEN 0 AND 1),
  ambiguity REAL NOT NULL CHECK (ambiguity BETWEEN 0 AND 1),
  claim_strength REAL NOT NULL CHECK (claim_strength BETWEEN 0 AND 1),
  owner TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('active', 'review', 'revise', 'archive')),
  review_date TEXT NOT NULL
);

DROP VIEW IF EXISTS policy_governance_scores;

CREATE VIEW policy_governance_scores AS
SELECT
  item,
  policy_area,
  description,
  problem_clarity,
  authority_clarity,
  evidence_strength,
  stakeholder_visibility,
  implementation_detail,
  accountability_coverage,
  participation_clarity,
  ambiguity,
  claim_strength,
  ROUND((
    problem_clarity
    + authority_clarity
    + evidence_strength
    + stakeholder_visibility
    + implementation_detail
    + accountability_coverage
    + participation_clarity
  ) / 7.0, 3) AS completeness_score,
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
        (1 - accountability_coverage) * 0.25
        + (1 - stakeholder_visibility) * 0.20
        + (1 - evidence_strength) * 0.20
        + ambiguity * 0.20
        + (1 - implementation_detail) * 0.15
      ) > 1 THEN 1
      ELSE (
        (1 - accountability_coverage) * 0.25
        + (1 - stakeholder_visibility) * 0.20
        + (1 - evidence_strength) * 0.20
        + ambiguity * 0.20
        + (1 - implementation_detail) * 0.15
      )
    END,
    3
  ) AS governance_risk,
  ROUND(
    CASE
      WHEN (
        (CASE WHEN claim_strength - evidence_strength > 0 THEN claim_strength - evidence_strength ELSE 0 END) * 0.35
        + (
          CASE
            WHEN (
              (1 - accountability_coverage) * 0.25
              + (1 - stakeholder_visibility) * 0.20
              + (1 - evidence_strength) * 0.20
              + ambiguity * 0.20
              + (1 - implementation_detail) * 0.15
            ) > 1 THEN 1
            ELSE (
              (1 - accountability_coverage) * 0.25
              + (1 - stakeholder_visibility) * 0.20
              + (1 - evidence_strength) * 0.20
              + ambiguity * 0.20
              + (1 - implementation_detail) * 0.15
            )
          END
        ) * 0.40
        + (1 - (
          problem_clarity
          + authority_clarity
          + evidence_strength
          + stakeholder_visibility
          + implementation_detail
          + accountability_coverage
          + participation_clarity
        ) / 7.0) * 0.25
      ) > 1 THEN 1
      ELSE (
        (CASE WHEN claim_strength - evidence_strength > 0 THEN claim_strength - evidence_strength ELSE 0 END) * 0.35
        + (
          CASE
            WHEN (
              (1 - accountability_coverage) * 0.25
              + (1 - stakeholder_visibility) * 0.20
              + (1 - evidence_strength) * 0.20
              + ambiguity * 0.20
              + (1 - implementation_detail) * 0.15
            ) > 1 THEN 1
            ELSE (
              (1 - accountability_coverage) * 0.25
              + (1 - stakeholder_visibility) * 0.20
              + (1 - evidence_strength) * 0.20
              + ambiguity * 0.20
              + (1 - implementation_detail) * 0.15
            )
          END
        ) * 0.40
        + (1 - (
          problem_clarity
          + authority_clarity
          + evidence_strength
          + stakeholder_visibility
          + implementation_detail
          + accountability_coverage
          + participation_clarity
        ) / 7.0) * 0.25
      )
    END,
    3
  ) AS review_priority_score,
  owner,
  status,
  review_date
FROM policy_governance_items;
