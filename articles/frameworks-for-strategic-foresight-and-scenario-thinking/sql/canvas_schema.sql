-- Catalyst Canvas schema for strategic foresight and scenario thinking governance.

DROP TABLE IF EXISTS strategic_foresight_items;

CREATE TABLE strategic_foresight_items (
  item TEXT PRIMARY KEY,
  foresight_type TEXT NOT NULL,
  description TEXT NOT NULL,
  driver_clarity REAL NOT NULL CHECK (driver_clarity BETWEEN 0 AND 1),
  uncertainty_logic REAL NOT NULL CHECK (uncertainty_logic BETWEEN 0 AND 1),
  scenario_logic REAL NOT NULL CHECK (scenario_logic BETWEEN 0 AND 1),
  assumption_transparency REAL NOT NULL CHECK (assumption_transparency BETWEEN 0 AND 1),
  option_relevance REAL NOT NULL CHECK (option_relevance BETWEEN 0 AND 1),
  indicator_coverage REAL NOT NULL CHECK (indicator_coverage BETWEEN 0 AND 1),
  evidence_strength REAL NOT NULL CHECK (evidence_strength BETWEEN 0 AND 1),
  stakeholder_visibility REAL NOT NULL CHECK (stakeholder_visibility BETWEEN 0 AND 1),
  importance REAL NOT NULL CHECK (importance BETWEEN 0 AND 1),
  uncertainty REAL NOT NULL CHECK (uncertainty BETWEEN 0 AND 1),
  owner TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('active', 'review', 'revise', 'archive')),
  review_date TEXT NOT NULL
);

DROP VIEW IF EXISTS strategic_foresight_scores;

CREATE VIEW strategic_foresight_scores AS
SELECT
  item,
  foresight_type,
  description,
  driver_clarity,
  uncertainty_logic,
  scenario_logic,
  assumption_transparency,
  option_relevance,
  indicator_coverage,
  evidence_strength,
  stakeholder_visibility,
  importance,
  uncertainty,
  ROUND((
    driver_clarity
    + uncertainty_logic
    + scenario_logic
    + assumption_transparency
    + option_relevance
    + indicator_coverage
    + evidence_strength
    + stakeholder_visibility
  ) / 8.0, 3) AS quality_score,
  ROUND(importance * uncertainty * (1 - evidence_strength), 3) AS assumption_risk,
  ROUND(
    CASE
      WHEN (
        importance * uncertainty * (1 - evidence_strength) * 0.35
        + (1 - indicator_coverage) * 0.25
        + (1 - option_relevance) * 0.20
        + (1 - stakeholder_visibility) * 0.20
      ) > 1 THEN 1
      ELSE (
        importance * uncertainty * (1 - evidence_strength) * 0.35
        + (1 - indicator_coverage) * 0.25
        + (1 - option_relevance) * 0.20
        + (1 - stakeholder_visibility) * 0.20
      )
    END,
    3
  ) AS review_priority_score,
  owner,
  status,
  review_date
FROM strategic_foresight_items;
