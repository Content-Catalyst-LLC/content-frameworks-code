-- Catalyst Canvas schema for PESTLE external-environment diagnostics.

DROP TABLE IF EXISTS pestle_factors;

CREATE TABLE pestle_factors (
  factor TEXT PRIMARY KEY,
  category TEXT NOT NULL CHECK (category IN ('political', 'economic', 'social', 'technological', 'legal', 'environmental')),
  signal_type TEXT NOT NULL,
  description TEXT NOT NULL,
  impact REAL NOT NULL CHECK (impact BETWEEN 0 AND 1),
  urgency REAL NOT NULL CHECK (urgency BETWEEN 0 AND 1),
  evidence_strength REAL NOT NULL CHECK (evidence_strength BETWEEN 0 AND 1),
  uncertainty REAL NOT NULL CHECK (uncertainty BETWEEN 0 AND 1),
  strategic_relevance REAL NOT NULL CHECK (strategic_relevance BETWEEN 0 AND 1),
  actionability REAL NOT NULL CHECK (actionability BETWEEN 0 AND 1),
  claim_strength REAL NOT NULL CHECK (claim_strength BETWEEN 0 AND 1),
  owner TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('active', 'review', 'revise', 'archive')),
  review_date TEXT NOT NULL
);

DROP VIEW IF EXISTS pestle_scores;

CREATE VIEW pestle_scores AS
SELECT
  factor,
  category,
  signal_type,
  description,
  ROUND((impact + urgency + evidence_strength + strategic_relevance + actionability) / 5.0, 3) AS readiness_score,
  ROUND(
    impact * 0.24 +
    urgency * 0.18 +
    evidence_strength * 0.16 +
    uncertainty * 0.12 +
    strategic_relevance * 0.20 +
    actionability * 0.10,
    3
  ) AS weighted_priority,
  ROUND(
    CASE
      WHEN claim_strength - evidence_strength > 0 THEN claim_strength - evidence_strength
      ELSE 0
    END,
    3
  ) AS evidence_gap,
  ROUND(impact * uncertainty, 3) AS monitoring_priority,
  ROUND(
    CASE
      WHEN (
        impact * 0.24 +
        urgency * 0.18 +
        evidence_strength * 0.16 +
        uncertainty * 0.12 +
        strategic_relevance * 0.20 +
        actionability * 0.10
      ) + (
        CASE
          WHEN claim_strength - evidence_strength > 0 THEN claim_strength - evidence_strength
          ELSE 0
        END
      ) * 0.40 > 1 THEN 1
      ELSE (
        impact * 0.24 +
        urgency * 0.18 +
        evidence_strength * 0.16 +
        uncertainty * 0.12 +
        strategic_relevance * 0.20 +
        actionability * 0.10
      ) + (
        CASE
          WHEN claim_strength - evidence_strength > 0 THEN claim_strength - evidence_strength
          ELSE 0
        END
      ) * 0.40
    END,
    3
  ) AS governance_priority,
  owner,
  status,
  review_date
FROM pestle_factors;
