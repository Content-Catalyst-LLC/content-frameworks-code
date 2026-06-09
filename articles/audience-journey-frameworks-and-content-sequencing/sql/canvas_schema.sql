-- Catalyst Canvas schema for audience journey and content sequencing diagnostics.

DROP TABLE IF EXISTS audience_journey_stages;

CREATE TABLE audience_journey_stages (
  stage TEXT PRIMARY KEY,
  audience_need TEXT NOT NULL,
  journey_type TEXT NOT NULL,
  stage_clarity REAL NOT NULL CHECK (stage_clarity BETWEEN 0 AND 1),
  content_coverage REAL NOT NULL CHECK (content_coverage BETWEEN 0 AND 1),
  transition_quality REAL NOT NULL CHECK (transition_quality BETWEEN 0 AND 1),
  evidence_readiness REAL NOT NULL CHECK (evidence_readiness BETWEEN 0 AND 1),
  governance_readiness REAL NOT NULL CHECK (governance_readiness BETWEEN 0 AND 1),
  required_links INTEGER NOT NULL CHECK (required_links >= 0),
  available_links INTEGER NOT NULL CHECK (available_links >= 0),
  persona_fit REAL NOT NULL CHECK (persona_fit BETWEEN 0 AND 1),
  staleness_risk REAL NOT NULL CHECK (staleness_risk BETWEEN 0 AND 1),
  owner TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('active', 'review', 'revise', 'archive')),
  review_date TEXT NOT NULL
);

DROP VIEW IF EXISTS audience_journey_scores;

CREATE VIEW audience_journey_scores AS
SELECT
  stage,
  audience_need,
  journey_type,
  ROUND((stage_clarity + content_coverage + transition_quality + evidence_readiness + governance_readiness) / 5.0, 3) AS readiness_score,
  ROUND(
    stage_clarity * 0.18 +
    content_coverage * 0.22 +
    transition_quality * 0.20 +
    evidence_readiness * 0.22 +
    governance_readiness * 0.18,
    3
  ) AS weighted_readiness,
  CASE
    WHEN required_links - available_links > 0 THEN required_links - available_links
    ELSE 0
  END AS link_gap,
  ROUND(1.0 - persona_fit, 3) AS persona_mismatch,
  staleness_risk,
  owner,
  status,
  review_date
FROM audience_journey_stages;
