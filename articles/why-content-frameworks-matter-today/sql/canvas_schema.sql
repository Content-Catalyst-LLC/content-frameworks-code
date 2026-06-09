-- Catalyst Canvas schema for Why Content Frameworks Matter Today governance.

DROP TABLE IF EXISTS content_framework_value_items;

CREATE TABLE content_framework_value_items (
  item TEXT PRIMARY KEY,
  framework_type TEXT NOT NULL,
  description TEXT NOT NULL,
  coherence REAL NOT NULL CHECK (coherence BETWEEN 0 AND 1),
  reuse_readiness REAL NOT NULL CHECK (reuse_readiness BETWEEN 0 AND 1),
  evidence_visibility REAL NOT NULL CHECK (evidence_visibility BETWEEN 0 AND 1),
  audience_pathway_clarity REAL NOT NULL CHECK (audience_pathway_clarity BETWEEN 0 AND 1),
  governance_maturity REAL NOT NULL CHECK (governance_maturity BETWEEN 0 AND 1),
  platform_readiness REAL NOT NULL CHECK (platform_readiness BETWEEN 0 AND 1),
  learning_support REAL NOT NULL CHECK (learning_support BETWEEN 0 AND 1),
  ai_readiness REAL NOT NULL CHECK (ai_readiness BETWEEN 0 AND 1),
  fragmentation_risk REAL NOT NULL CHECK (fragmentation_risk BETWEEN 0 AND 1),
  context_preservation REAL NOT NULL CHECK (context_preservation BETWEEN 0 AND 1),
  maintenance_burden REAL NOT NULL CHECK (maintenance_burden BETWEEN 0 AND 1),
  owner TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('active', 'review', 'revise', 'archive')),
  review_date TEXT NOT NULL
);

DROP VIEW IF EXISTS content_framework_value_scores;

CREATE VIEW content_framework_value_scores AS
SELECT
  item,
  framework_type,
  description,
  coherence,
  reuse_readiness,
  evidence_visibility,
  audience_pathway_clarity,
  governance_maturity,
  platform_readiness,
  learning_support,
  ai_readiness,
  fragmentation_risk,
  context_preservation,
  maintenance_burden,
  ROUND((
    coherence
    + reuse_readiness
    + evidence_visibility
    + audience_pathway_clarity
    + governance_maturity
    + platform_readiness
    + learning_support
    + ai_readiness
  ) / 8.0, 3) AS value_score,
  ROUND(
    CASE
      WHEN (
        (1 - evidence_visibility) * 0.22
        + (1 - governance_maturity) * 0.22
        + fragmentation_risk * 0.22
        + (1 - context_preservation) * 0.17
        + maintenance_burden * 0.17
      ) > 1 THEN 1
      ELSE (
        (1 - evidence_visibility) * 0.22
        + (1 - governance_maturity) * 0.22
        + fragmentation_risk * 0.22
        + (1 - context_preservation) * 0.17
        + maintenance_burden * 0.17
      )
    END,
    3
  ) AS framework_risk,
  ROUND(
    CASE
      WHEN (
        (1 - (
          coherence
          + reuse_readiness
          + evidence_visibility
          + audience_pathway_clarity
          + governance_maturity
          + platform_readiness
          + learning_support
          + ai_readiness
        ) / 8.0) * 0.50
        + (
          CASE
            WHEN (
              (1 - evidence_visibility) * 0.22
              + (1 - governance_maturity) * 0.22
              + fragmentation_risk * 0.22
              + (1 - context_preservation) * 0.17
              + maintenance_burden * 0.17
            ) > 1 THEN 1
            ELSE (
              (1 - evidence_visibility) * 0.22
              + (1 - governance_maturity) * 0.22
              + fragmentation_risk * 0.22
              + (1 - context_preservation) * 0.17
              + maintenance_burden * 0.17
            )
          END
        ) * 0.50
      ) > 1 THEN 1
      ELSE (
        (1 - (
          coherence
          + reuse_readiness
          + evidence_visibility
          + audience_pathway_clarity
          + governance_maturity
          + platform_readiness
          + learning_support
          + ai_readiness
        ) / 8.0) * 0.50
        + (
          CASE
            WHEN (
              (1 - evidence_visibility) * 0.22
              + (1 - governance_maturity) * 0.22
              + fragmentation_risk * 0.22
              + (1 - context_preservation) * 0.17
              + maintenance_burden * 0.17
            ) > 1 THEN 1
            ELSE (
              (1 - evidence_visibility) * 0.22
              + (1 - governance_maturity) * 0.22
              + fragmentation_risk * 0.22
              + (1 - context_preservation) * 0.17
              + maintenance_burden * 0.17
            )
          END
        ) * 0.50
      )
    END,
    3
  ) AS review_priority_score,
  owner,
  status,
  review_date
FROM content_framework_value_items;
