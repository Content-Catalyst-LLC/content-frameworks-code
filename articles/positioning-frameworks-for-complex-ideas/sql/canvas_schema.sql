-- Catalyst Canvas schema for positioning complex ideas.

DROP TABLE IF EXISTS positioning_records;

CREATE TABLE positioning_records (
  idea TEXT PRIMARY KEY,
  description TEXT NOT NULL,
  category_frame TEXT NOT NULL,
  audience_pathway TEXT NOT NULL,
  category_clarity REAL NOT NULL CHECK (category_clarity BETWEEN 0 AND 1),
  audience_relevance REAL NOT NULL CHECK (audience_relevance BETWEEN 0 AND 1),
  differentiation REAL NOT NULL CHECK (differentiation BETWEEN 0 AND 1),
  evidence_strength REAL NOT NULL CHECK (evidence_strength BETWEEN 0 AND 1),
  governance_readiness REAL NOT NULL CHECK (governance_readiness BETWEEN 0 AND 1),
  boundary_clarity REAL NOT NULL CHECK (boundary_clarity BETWEEN 0 AND 1),
  ethical_risk REAL NOT NULL CHECK (ethical_risk BETWEEN 0 AND 1),
  drift_risk REAL NOT NULL CHECK (drift_risk BETWEEN 0 AND 1),
  owner TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('active', 'review', 'revise', 'archive')),
  review_date TEXT NOT NULL
);

DROP VIEW IF EXISTS positioning_scores;

CREATE VIEW positioning_scores AS
SELECT
  idea,
  description,
  category_frame,
  audience_pathway,
  ROUND((category_clarity + audience_relevance + differentiation + evidence_strength + governance_readiness + boundary_clarity) / 6.0, 3) AS readiness_score,
  ROUND(
    category_clarity * 0.18 +
    audience_relevance * 0.20 +
    differentiation * 0.16 +
    evidence_strength * 0.20 +
    governance_readiness * 0.14 +
    boundary_clarity * 0.12,
    3
  ) AS weighted_readiness,
  ROUND(
    CASE
      WHEN ((category_clarity + audience_relevance + differentiation) / 3.0) - evidence_strength > 0
      THEN ((category_clarity + audience_relevance + differentiation) / 3.0) - evidence_strength
      ELSE 0
    END,
    3
  ) AS evidence_gap,
  drift_risk,
  ethical_risk,
  owner,
  status,
  review_date
FROM positioning_records;
