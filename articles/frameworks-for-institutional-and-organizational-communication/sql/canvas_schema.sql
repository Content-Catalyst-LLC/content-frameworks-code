-- Catalyst Canvas schema for institutional and organizational communication governance.

DROP TABLE IF EXISTS institutional_communication_items;

CREATE TABLE institutional_communication_items (
  item TEXT PRIMARY KEY,
  communication_type TEXT NOT NULL,
  description TEXT NOT NULL,
  clarity REAL NOT NULL CHECK (clarity BETWEEN 0 AND 1),
  authority_coverage REAL NOT NULL CHECK (authority_coverage BETWEEN 0 AND 1),
  evidence_strength REAL NOT NULL CHECK (evidence_strength BETWEEN 0 AND 1),
  stakeholder_visibility REAL NOT NULL CHECK (stakeholder_visibility BETWEEN 0 AND 1),
  feedback_quality REAL NOT NULL CHECK (feedback_quality BETWEEN 0 AND 1),
  channel_fit REAL NOT NULL CHECK (channel_fit BETWEEN 0 AND 1),
  cultural_alignment REAL NOT NULL CHECK (cultural_alignment BETWEEN 0 AND 1),
  governance_coverage REAL NOT NULL CHECK (governance_coverage BETWEEN 0 AND 1),
  ambiguity REAL NOT NULL CHECK (ambiguity BETWEEN 0 AND 1),
  claim_strength REAL NOT NULL CHECK (claim_strength BETWEEN 0 AND 1),
  owner TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('active', 'review', 'revise', 'archive')),
  review_date TEXT NOT NULL
);

DROP VIEW IF EXISTS institutional_communication_scores;

CREATE VIEW institutional_communication_scores AS
SELECT
  item,
  communication_type,
  description,
  clarity,
  authority_coverage,
  evidence_strength,
  stakeholder_visibility,
  feedback_quality,
  channel_fit,
  cultural_alignment,
  governance_coverage,
  ambiguity,
  claim_strength,
  ROUND((
    clarity
    + authority_coverage
    + evidence_strength
    + stakeholder_visibility
    + feedback_quality
    + channel_fit
    + cultural_alignment
    + governance_coverage
  ) / 8.0, 3) AS quality_score,
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
        ambiguity * 0.25
        + (1 - governance_coverage) * 0.25
        + (1 - evidence_strength) * 0.20
        + (1 - stakeholder_visibility) * 0.15
        + (1 - feedback_quality) * 0.15
      ) > 1 THEN 1
      ELSE (
        ambiguity * 0.25
        + (1 - governance_coverage) * 0.25
        + (1 - evidence_strength) * 0.20
        + (1 - stakeholder_visibility) * 0.15
        + (1 - feedback_quality) * 0.15
      )
    END,
    3
  ) AS trust_risk,
  ROUND(
    CASE
      WHEN (
        (
          CASE
            WHEN (
              ambiguity * 0.25
              + (1 - governance_coverage) * 0.25
              + (1 - evidence_strength) * 0.20
              + (1 - stakeholder_visibility) * 0.15
              + (1 - feedback_quality) * 0.15
            ) > 1 THEN 1
            ELSE (
              ambiguity * 0.25
              + (1 - governance_coverage) * 0.25
              + (1 - evidence_strength) * 0.20
              + (1 - stakeholder_visibility) * 0.15
              + (1 - feedback_quality) * 0.15
            )
          END
        ) * 0.40
        + (1 - authority_coverage) * 0.25
        + (CASE WHEN claim_strength - evidence_strength > 0 THEN claim_strength - evidence_strength ELSE 0 END) * 0.20
        + (1 - feedback_quality) * 0.15
      ) > 1 THEN 1
      ELSE (
        (
          CASE
            WHEN (
              ambiguity * 0.25
              + (1 - governance_coverage) * 0.25
              + (1 - evidence_strength) * 0.20
              + (1 - stakeholder_visibility) * 0.15
              + (1 - feedback_quality) * 0.15
            ) > 1 THEN 1
            ELSE (
              ambiguity * 0.25
              + (1 - governance_coverage) * 0.25
              + (1 - evidence_strength) * 0.20
              + (1 - stakeholder_visibility) * 0.15
              + (1 - feedback_quality) * 0.15
            )
          END
        ) * 0.40
        + (1 - authority_coverage) * 0.25
        + (CASE WHEN claim_strength - evidence_strength > 0 THEN claim_strength - evidence_strength ELSE 0 END) * 0.20
        + (1 - feedback_quality) * 0.15
      )
    END,
    3
  ) AS review_priority_score,
  owner,
  status,
  review_date
FROM institutional_communication_items;
