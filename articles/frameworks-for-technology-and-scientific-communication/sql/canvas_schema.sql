-- Catalyst Canvas schema for technology and scientific communication governance.

DROP TABLE IF EXISTS technology_science_items;

CREATE TABLE technology_science_items (
  item TEXT PRIMARY KEY,
  communication_type TEXT NOT NULL,
  description TEXT NOT NULL,
  claim_clarity REAL NOT NULL CHECK (claim_clarity BETWEEN 0 AND 1),
  evidence_strength REAL NOT NULL CHECK (evidence_strength BETWEEN 0 AND 1),
  method_transparency REAL NOT NULL CHECK (method_transparency BETWEEN 0 AND 1),
  uncertainty_disclosure REAL NOT NULL CHECK (uncertainty_disclosure BETWEEN 0 AND 1),
  audience_fit REAL NOT NULL CHECK (audience_fit BETWEEN 0 AND 1),
  risk_visibility REAL NOT NULL CHECK (risk_visibility BETWEEN 0 AND 1),
  stakeholder_visibility REAL NOT NULL CHECK (stakeholder_visibility BETWEEN 0 AND 1),
  promotional_intensity REAL NOT NULL CHECK (promotional_intensity BETWEEN 0 AND 1),
  claim_breadth REAL NOT NULL CHECK (claim_breadth BETWEEN 0 AND 1),
  owner TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('active', 'review', 'revise', 'archive')),
  review_date TEXT NOT NULL
);

DROP VIEW IF EXISTS technology_science_scores;

CREATE VIEW technology_science_scores AS
SELECT
  item,
  communication_type,
  description,
  claim_clarity,
  evidence_strength,
  method_transparency,
  uncertainty_disclosure,
  audience_fit,
  risk_visibility,
  stakeholder_visibility,
  promotional_intensity,
  claim_breadth,
  ROUND((
    claim_clarity
    + evidence_strength
    + method_transparency
    + uncertainty_disclosure
    + audience_fit
    + risk_visibility
    + stakeholder_visibility
  ) / 7.0, 3) AS quality_score,
  ROUND(
    CASE
      WHEN claim_breadth - evidence_strength > 0 THEN claim_breadth - evidence_strength
      ELSE 0
    END,
    3
  ) AS evidence_gap,
  ROUND(
    CASE
      WHEN (
        (1 - evidence_strength) * 0.25
        + (1 - uncertainty_disclosure) * 0.25
        + promotional_intensity * 0.25
        + claim_breadth * 0.25
      ) > 1 THEN 1
      ELSE (
        (1 - evidence_strength) * 0.25
        + (1 - uncertainty_disclosure) * 0.25
        + promotional_intensity * 0.25
        + claim_breadth * 0.25
      )
    END,
    3
  ) AS hype_risk,
  ROUND(
    CASE
      WHEN (
        (CASE WHEN claim_breadth - evidence_strength > 0 THEN claim_breadth - evidence_strength ELSE 0 END) * 0.35
        + (
          CASE
            WHEN (
              (1 - evidence_strength) * 0.25
              + (1 - uncertainty_disclosure) * 0.25
              + promotional_intensity * 0.25
              + claim_breadth * 0.25
            ) > 1 THEN 1
            ELSE (
              (1 - evidence_strength) * 0.25
              + (1 - uncertainty_disclosure) * 0.25
              + promotional_intensity * 0.25
              + claim_breadth * 0.25
            )
          END
        ) * 0.40
        + (1 - audience_fit) * 0.15
        + (1 - risk_visibility) * 0.10
      ) > 1 THEN 1
      ELSE (
        (CASE WHEN claim_breadth - evidence_strength > 0 THEN claim_breadth - evidence_strength ELSE 0 END) * 0.35
        + (
          CASE
            WHEN (
              (1 - evidence_strength) * 0.25
              + (1 - uncertainty_disclosure) * 0.25
              + promotional_intensity * 0.25
              + claim_breadth * 0.25
            ) > 1 THEN 1
            ELSE (
              (1 - evidence_strength) * 0.25
              + (1 - uncertainty_disclosure) * 0.25
              + promotional_intensity * 0.25
              + claim_breadth * 0.25
            )
          END
        ) * 0.40
        + (1 - audience_fit) * 0.15
        + (1 - risk_visibility) * 0.10
      )
    END,
    3
  ) AS review_priority_score,
  owner,
  status,
  review_date
FROM technology_science_items;
