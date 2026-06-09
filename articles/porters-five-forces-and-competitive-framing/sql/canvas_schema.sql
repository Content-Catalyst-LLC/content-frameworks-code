-- Catalyst Canvas schema for Porter Five Forces diagnostics.

DROP TABLE IF EXISTS five_forces_records;

CREATE TABLE five_forces_records (
  force TEXT NOT NULL CHECK (force IN ('rivalry', 'new entrants', 'substitutes', 'supplier power', 'buyer power', 'competition')),
  market_boundary TEXT NOT NULL,
  description TEXT NOT NULL,
  intensity REAL NOT NULL CHECK (intensity BETWEEN 0 AND 1),
  evidence_strength REAL NOT NULL CHECK (evidence_strength BETWEEN 0 AND 1),
  uncertainty REAL NOT NULL CHECK (uncertainty BETWEEN 0 AND 1),
  strategic_relevance REAL NOT NULL CHECK (strategic_relevance BETWEEN 0 AND 1),
  actionability REAL NOT NULL CHECK (actionability BETWEEN 0 AND 1),
  claim_strength REAL NOT NULL CHECK (claim_strength BETWEEN 0 AND 1),
  owner TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('active', 'review', 'revise', 'archive')),
  review_date TEXT NOT NULL,
  PRIMARY KEY (force, market_boundary)
);

DROP VIEW IF EXISTS five_forces_scores;

CREATE VIEW five_forces_scores AS
SELECT
  force,
  market_boundary,
  description,
  ROUND((intensity + evidence_strength + strategic_relevance + actionability) / 4.0, 3) AS readiness_score,
  ROUND(
    intensity * 0.30 +
    evidence_strength * 0.18 +
    uncertainty * 0.12 +
    strategic_relevance * 0.26 +
    actionability * 0.14,
    3
  ) AS weighted_priority,
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
        intensity * 0.30 +
        evidence_strength * 0.18 +
        uncertainty * 0.12 +
        strategic_relevance * 0.26 +
        actionability * 0.14
      ) + (
        CASE
          WHEN claim_strength - evidence_strength > 0 THEN claim_strength - evidence_strength
          ELSE 0
        END
      ) * 0.45 > 1 THEN 1
      ELSE (
        intensity * 0.30 +
        evidence_strength * 0.18 +
        uncertainty * 0.12 +
        strategic_relevance * 0.26 +
        actionability * 0.14
      ) + (
        CASE
          WHEN claim_strength - evidence_strength > 0 THEN claim_strength - evidence_strength
          ELSE 0
        END
      ) * 0.45
    END,
    3
  ) AS governance_priority,
  owner,
  status,
  review_date
FROM five_forces_records;
