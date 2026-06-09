-- Catalyst Canvas schema for Scaling Knowledge Through Frameworks governance.

DROP TABLE IF EXISTS knowledge_scaling_items;

CREATE TABLE knowledge_scaling_items (
  item TEXT PRIMARY KEY,
  asset_type TEXT NOT NULL,
  description TEXT NOT NULL,
  modularity REAL NOT NULL CHECK (modularity BETWEEN 0 AND 1),
  taxonomy_quality REAL NOT NULL CHECK (taxonomy_quality BETWEEN 0 AND 1),
  metadata_completeness REAL NOT NULL CHECK (metadata_completeness BETWEEN 0 AND 1),
  link_coverage REAL NOT NULL CHECK (link_coverage BETWEEN 0 AND 1),
  evidence_alignment REAL NOT NULL CHECK (evidence_alignment BETWEEN 0 AND 1),
  reuse_readiness REAL NOT NULL CHECK (reuse_readiness BETWEEN 0 AND 1),
  governance_maturity REAL NOT NULL CHECK (governance_maturity BETWEEN 0 AND 1),
  platform_readiness REAL NOT NULL CHECK (platform_readiness BETWEEN 0 AND 1),
  audience_pathway_clarity REAL NOT NULL CHECK (audience_pathway_clarity BETWEEN 0 AND 1),
  dependency_complexity REAL NOT NULL CHECK (dependency_complexity BETWEEN 0 AND 1),
  owner TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('active', 'review', 'revise', 'archive')),
  review_date TEXT NOT NULL
);

DROP VIEW IF EXISTS knowledge_scaling_scores;

CREATE VIEW knowledge_scaling_scores AS
SELECT
  item,
  asset_type,
  description,
  modularity,
  taxonomy_quality,
  metadata_completeness,
  link_coverage,
  evidence_alignment,
  reuse_readiness,
  governance_maturity,
  platform_readiness,
  audience_pathway_clarity,
  dependency_complexity,
  ROUND((
    modularity
    + taxonomy_quality
    + metadata_completeness
    + link_coverage
    + evidence_alignment
    + reuse_readiness
    + governance_maturity
    + platform_readiness
    + audience_pathway_clarity
  ) / 9.0, 3) AS scalability_score,
  ROUND(
    CASE
      WHEN (
        (1 - governance_maturity) * 0.30
        + (1 - evidence_alignment) * 0.25
        + (1 - link_coverage) * 0.20
        + dependency_complexity * 0.25
      ) > 1 THEN 1
      ELSE (
        (1 - governance_maturity) * 0.30
        + (1 - evidence_alignment) * 0.25
        + (1 - link_coverage) * 0.20
        + dependency_complexity * 0.25
      )
    END,
    3
  ) AS maintenance_risk,
  ROUND(
    CASE
      WHEN (
        (1 - (
          modularity
          + taxonomy_quality
          + metadata_completeness
          + link_coverage
          + evidence_alignment
          + reuse_readiness
          + governance_maturity
          + platform_readiness
          + audience_pathway_clarity
        ) / 9.0) * 0.50
        + (
          CASE
            WHEN (
              (1 - governance_maturity) * 0.30
              + (1 - evidence_alignment) * 0.25
              + (1 - link_coverage) * 0.20
              + dependency_complexity * 0.25
            ) > 1 THEN 1
            ELSE (
              (1 - governance_maturity) * 0.30
              + (1 - evidence_alignment) * 0.25
              + (1 - link_coverage) * 0.20
              + dependency_complexity * 0.25
            )
          END
        ) * 0.50
      ) > 1 THEN 1
      ELSE (
        (1 - (
          modularity
          + taxonomy_quality
          + metadata_completeness
          + link_coverage
          + evidence_alignment
          + reuse_readiness
          + governance_maturity
          + platform_readiness
          + audience_pathway_clarity
        ) / 9.0) * 0.50
        + (
          CASE
            WHEN (
              (1 - governance_maturity) * 0.30
              + (1 - evidence_alignment) * 0.25
              + (1 - link_coverage) * 0.20
              + dependency_complexity * 0.25
            ) > 1 THEN 1
            ELSE (
              (1 - governance_maturity) * 0.30
              + (1 - evidence_alignment) * 0.25
              + (1 - link_coverage) * 0.20
              + dependency_complexity * 0.25
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
FROM knowledge_scaling_items;
