-- Catalyst Canvas schema for SWOT analysis diagnostics.

DROP TABLE IF EXISTS swot_items;

CREATE TABLE swot_items (
  item TEXT PRIMARY KEY,
  quadrant TEXT NOT NULL CHECK (quadrant IN ('strength', 'weakness', 'opportunity', 'threat')),
  orientation TEXT NOT NULL CHECK (orientation IN ('internal', 'external')),
  description TEXT NOT NULL,
  impact REAL NOT NULL CHECK (impact BETWEEN 0 AND 1),
  confidence REAL NOT NULL CHECK (confidence BETWEEN 0 AND 1),
  urgency REAL NOT NULL CHECK (urgency BETWEEN 0 AND 1),
  feasibility REAL NOT NULL CHECK (feasibility BETWEEN 0 AND 1),
  strategic_fit REAL NOT NULL CHECK (strategic_fit BETWEEN 0 AND 1),
  evidence_strength REAL NOT NULL CHECK (evidence_strength BETWEEN 0 AND 1),
  claim_strength REAL NOT NULL CHECK (claim_strength BETWEEN 0 AND 1),
  owner TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('active', 'review', 'revise', 'archive')),
  review_date TEXT NOT NULL
);

DROP VIEW IF EXISTS swot_scores;

CREATE VIEW swot_scores AS
SELECT
  item,
  quadrant,
  orientation,
  description,
  ROUND((impact + confidence + urgency + feasibility + strategic_fit) / 5.0, 3) AS priority_score,
  ROUND(
    impact * 0.26 +
    confidence * 0.20 +
    urgency * 0.18 +
    feasibility * 0.16 +
    strategic_fit * 0.20,
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
        impact * 0.26 +
        confidence * 0.20 +
        urgency * 0.18 +
        feasibility * 0.16 +
        strategic_fit * 0.20
      ) + (
        CASE
          WHEN claim_strength - evidence_strength > 0 THEN claim_strength - evidence_strength
          ELSE 0
        END
      ) * 0.50 > 1 THEN 1
      ELSE (
        impact * 0.26 +
        confidence * 0.20 +
        urgency * 0.18 +
        feasibility * 0.16 +
        strategic_fit * 0.20
      ) + (
        CASE
          WHEN claim_strength - evidence_strength > 0 THEN claim_strength - evidence_strength
          ELSE 0
        END
      ) * 0.50
    END,
    3
  ) AS governance_priority,
  owner,
  status,
  review_date
FROM swot_items;
