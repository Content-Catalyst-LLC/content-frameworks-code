-- Generic Catalyst Canvas readiness schema for Content Frameworks articles.

DROP TABLE IF EXISTS article_canvas_records;

CREATE TABLE article_canvas_records (
  record_id TEXT PRIMARY KEY,
  article_slug TEXT NOT NULL,
  article_title TEXT NOT NULL,
  module_kind TEXT NOT NULL,
  canvas_dimension TEXT NOT NULL,
  description TEXT NOT NULL,
  content_value REAL NOT NULL CHECK (content_value BETWEEN 0 AND 1),
  audience_value REAL NOT NULL CHECK (audience_value BETWEEN 0 AND 1),
  evidence_strength REAL NOT NULL CHECK (evidence_strength BETWEEN 0 AND 1),
  repository_support REAL NOT NULL CHECK (repository_support BETWEEN 0 AND 1),
  governance_need REAL NOT NULL CHECK (governance_need BETWEEN 0 AND 1),
  ethical_risk REAL NOT NULL CHECK (ethical_risk BETWEEN 0 AND 1),
  owner TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('active', 'review', 'revise', 'archive')),
  review_date TEXT NOT NULL
);

DROP VIEW IF EXISTS article_canvas_scores;

CREATE VIEW article_canvas_scores AS
SELECT
  record_id,
  article_slug,
  article_title,
  module_kind,
  canvas_dimension,
  ROUND(
    content_value * 0.22 +
    audience_value * 0.24 +
    evidence_strength * 0.22 +
    repository_support * 0.16 +
    (1.0 - governance_need) * 0.10 +
    (1.0 - ethical_risk) * 0.06,
    3
  ) AS readiness_score,
  governance_need,
  ethical_risk,
  owner,
  status,
  review_date
FROM article_canvas_records;
