-- Catalyst Canvas schema for STP segmentation, targeting, and positioning.

DROP TABLE IF EXISTS stp_canvas_segments;

CREATE TABLE stp_canvas_segments (
  segment TEXT PRIMARY KEY,
  description TEXT NOT NULL,
  primary_job TEXT NOT NULL,
  content_pathway TEXT NOT NULL,
  need_intensity REAL NOT NULL CHECK (need_intensity BETWEEN 0 AND 1),
  strategic_fit REAL NOT NULL CHECK (strategic_fit BETWEEN 0 AND 1),
  reachability REAL NOT NULL CHECK (reachability BETWEEN 0 AND 1),
  evidence_fit REAL NOT NULL CHECK (evidence_fit BETWEEN 0 AND 1),
  ethical_responsibility REAL NOT NULL CHECK (ethical_responsibility BETWEEN 0 AND 1),
  category_clarity REAL NOT NULL CHECK (category_clarity BETWEEN 0 AND 1),
  audience_relevance REAL NOT NULL CHECK (audience_relevance BETWEEN 0 AND 1),
  differentiation REAL NOT NULL CHECK (differentiation BETWEEN 0 AND 1),
  credibility REAL NOT NULL CHECK (credibility BETWEEN 0 AND 1),
  stereotype_risk REAL NOT NULL CHECK (stereotype_risk BETWEEN 0 AND 1),
  exclusion_risk REAL NOT NULL CHECK (exclusion_risk BETWEEN 0 AND 1),
  owner TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('active', 'review', 'revise', 'archive')),
  review_date TEXT NOT NULL
);

DROP VIEW IF EXISTS stp_canvas_scores;

CREATE VIEW stp_canvas_scores AS
SELECT
  segment,
  description,
  primary_job,
  content_pathway,
  ROUND((need_intensity + strategic_fit + reachability + evidence_fit + ethical_responsibility) / 5.0, 3) AS target_score,
  ROUND(
    need_intensity * 0.25 +
    strategic_fit * 0.20 +
    reachability * 0.15 +
    evidence_fit * 0.20 +
    ethical_responsibility * 0.20,
    3
  ) AS weighted_target_score,
  ROUND((category_clarity + audience_relevance + differentiation + evidence_fit + credibility) / 5.0, 3) AS positioning_score,
  ROUND(
    CASE
      WHEN need_intensity - ((category_clarity + audience_relevance + differentiation + evidence_fit + credibility) / 5.0) > 0
      THEN need_intensity - ((category_clarity + audience_relevance + differentiation + evidence_fit + credibility) / 5.0)
      ELSE 0
    END,
    3
  ) AS positioning_gap,
  ROUND(
    CASE
      WHEN stereotype_risk > exclusion_risk THEN stereotype_risk
      ELSE exclusion_risk
    END,
    3
  ) AS ethical_risk_score,
  CASE
    WHEN stereotype_risk >= 0.70 OR exclusion_risk >= 0.70 THEN 'high ethical review'
    WHEN stereotype_risk >= 0.50 OR exclusion_risk >= 0.50 THEN 'moderate ethical review'
    ELSE 'standard review'
  END AS ethical_review_flag,
  owner,
  status,
  review_date
FROM stp_canvas_segments;
