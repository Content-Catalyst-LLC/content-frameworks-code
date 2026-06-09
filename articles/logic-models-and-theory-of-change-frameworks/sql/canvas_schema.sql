-- Catalyst Canvas schema for logic-model and Theory of Change diagnostics.

DROP TABLE IF EXISTS logic_model_elements;

CREATE TABLE logic_model_elements (
  element TEXT PRIMARY KEY,
  model_layer TEXT NOT NULL CHECK (model_layer IN ('input', 'activity', 'output', 'outcome', 'impact', 'assumption', 'causal link', 'indicator')),
  description TEXT NOT NULL,
  evidence_strength REAL NOT NULL CHECK (evidence_strength BETWEEN 0 AND 1),
  assumption_importance REAL NOT NULL CHECK (assumption_importance BETWEEN 0 AND 1),
  assumption_evidence REAL NOT NULL CHECK (assumption_evidence BETWEEN 0 AND 1),
  measurement_coverage REAL NOT NULL CHECK (measurement_coverage BETWEEN 0 AND 1),
  outcome_clarity REAL NOT NULL CHECK (outcome_clarity BETWEEN 0 AND 1),
  claim_strength REAL NOT NULL CHECK (claim_strength BETWEEN 0 AND 1),
  owner TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('active', 'review', 'revise', 'archive')),
  review_date TEXT NOT NULL
);

DROP VIEW IF EXISTS logic_model_scores;

CREATE VIEW logic_model_scores AS
SELECT
  element,
  model_layer,
  description,
  evidence_strength,
  assumption_importance,
  assumption_evidence,
  measurement_coverage,
  outcome_clarity,
  claim_strength,
  ROUND(assumption_importance * (1 - assumption_evidence), 3) AS assumption_risk,
  ROUND(CASE WHEN claim_strength - evidence_strength > 0 THEN claim_strength - evidence_strength ELSE 0 END, 3) AS evidence_gap,
  ROUND((evidence_strength + assumption_evidence + measurement_coverage + outcome_clarity) / 4.0, 3) AS pathway_quality,
  ROUND(
    CASE
      WHEN (
        (CASE WHEN claim_strength - evidence_strength > 0 THEN claim_strength - evidence_strength ELSE 0 END) * 0.35
        + (assumption_importance * (1 - assumption_evidence)) * 0.35
        + (1 - measurement_coverage) * 0.20
        + (1 - outcome_clarity) * 0.10
      ) > 1 THEN 1
      ELSE (
        (CASE WHEN claim_strength - evidence_strength > 0 THEN claim_strength - evidence_strength ELSE 0 END) * 0.35
        + (assumption_importance * (1 - assumption_evidence)) * 0.35
        + (1 - measurement_coverage) * 0.20
        + (1 - outcome_clarity) * 0.10
      )
    END,
    3
  ) AS governance_priority,
  owner,
  status,
  review_date
FROM logic_model_elements;
