-- Catalyst Canvas schema for Message House strategic messaging diagnostics.

DROP TABLE IF EXISTS message_house_pillars;

CREATE TABLE message_house_pillars (
  pillar TEXT PRIMARY KEY,
  description TEXT NOT NULL,
  core_alignment REAL NOT NULL CHECK (core_alignment BETWEEN 0 AND 1),
  audience_relevance REAL NOT NULL CHECK (audience_relevance BETWEEN 0 AND 1),
  evidence_strength REAL NOT NULL CHECK (evidence_strength BETWEEN 0 AND 1),
  differentiation REAL NOT NULL CHECK (differentiation BETWEEN 0 AND 1),
  governance_readiness REAL NOT NULL CHECK (governance_readiness BETWEEN 0 AND 1),
  ethical_risk REAL NOT NULL CHECK (ethical_risk BETWEEN 0 AND 1),
  owner TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('active', 'review', 'revise', 'archive')),
  review_date TEXT NOT NULL
);

DROP VIEW IF EXISTS message_house_scores;

CREATE VIEW message_house_scores AS
SELECT
  pillar,
  description,
  ROUND((core_alignment + audience_relevance + evidence_strength + differentiation + governance_readiness) / 5.0, 3) AS readiness_score,
  ROUND(
    core_alignment * 0.22 +
    audience_relevance * 0.24 +
    evidence_strength * 0.24 +
    differentiation * 0.16 +
    governance_readiness * 0.14,
    3
  ) AS weighted_readiness,
  ROUND(
    CASE
      WHEN ((core_alignment + audience_relevance + differentiation) / 3.0) - evidence_strength > 0
      THEN ((core_alignment + audience_relevance + differentiation) / 3.0) - evidence_strength
      ELSE 0
    END,
    3
  ) AS proof_gap,
  ethical_risk,
  owner,
  status,
  review_date
FROM message_house_pillars;
