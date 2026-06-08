-- STP segmentation, targeting, and positioning schema.

DROP TABLE IF EXISTS stp_segments;

CREATE TABLE stp_segments (
  segment TEXT PRIMARY KEY,
  need_intensity REAL NOT NULL,
  strategic_fit REAL NOT NULL,
  reachability REAL NOT NULL,
  evidence_fit REAL NOT NULL,
  ethical_responsibility REAL NOT NULL,
  category_clarity REAL NOT NULL,
  audience_relevance REAL NOT NULL,
  differentiation REAL NOT NULL,
  credibility REAL NOT NULL,
  stereotype_risk REAL NOT NULL,
  exclusion_risk REAL NOT NULL
);

DROP VIEW IF EXISTS stp_scores;

CREATE VIEW stp_scores AS
SELECT
  segment,
  (need_intensity + strategic_fit + reachability + evidence_fit + ethical_responsibility) / 5.0 AS target_score,
  (
    need_intensity * 0.25 +
    strategic_fit * 0.20 +
    reachability * 0.15 +
    evidence_fit * 0.20 +
    ethical_responsibility * 0.20
  ) AS weighted_target_score,
  (category_clarity + audience_relevance + differentiation + evidence_fit + credibility) / 5.0 AS positioning_score,
  CASE
    WHEN need_intensity - ((category_clarity + audience_relevance + differentiation + evidence_fit + credibility) / 5.0) > 0
    THEN need_intensity - ((category_clarity + audience_relevance + differentiation + evidence_fit + credibility) / 5.0)
    ELSE 0
  END AS positioning_gap,
  CASE
    WHEN stereotype_risk >= 0.70 OR exclusion_risk >= 0.70 THEN 'high ethical review'
    WHEN stereotype_risk >= 0.50 OR exclusion_risk >= 0.50 THEN 'moderate ethical review'
    ELSE 'standard review'
  END AS ethical_review_flag
FROM stp_segments;
