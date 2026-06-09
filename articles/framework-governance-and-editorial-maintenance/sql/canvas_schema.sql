-- Catalyst Canvas schema for Framework Governance and Editorial Maintenance.

DROP TABLE IF EXISTS framework_governance_items;

CREATE TABLE framework_governance_items (
  item TEXT PRIMARY KEY,
  item_type TEXT NOT NULL,
  description TEXT NOT NULL,
  ownership_clarity REAL NOT NULL CHECK (ownership_clarity BETWEEN 0 AND 1),
  review_cycle_strength REAL NOT NULL CHECK (review_cycle_strength BETWEEN 0 AND 1),
  metadata_completeness REAL NOT NULL CHECK (metadata_completeness BETWEEN 0 AND 1),
  evidence_status REAL NOT NULL CHECK (evidence_status BETWEEN 0 AND 1),
  link_health REAL NOT NULL CHECK (link_health BETWEEN 0 AND 1),
  taxonomy_alignment REAL NOT NULL CHECK (taxonomy_alignment BETWEEN 0 AND 1),
  platform_readiness REAL NOT NULL CHECK (platform_readiness BETWEEN 0 AND 1),
  stale_evidence_risk REAL NOT NULL CHECK (stale_evidence_risk BETWEEN 0 AND 1),
  dependency_complexity REAL NOT NULL CHECK (dependency_complexity BETWEEN 0 AND 1),
  audience_impact REAL NOT NULL CHECK (audience_impact BETWEEN 0 AND 1),
  owner TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('active', 'review', 'revise', 'archive')),
  review_date TEXT NOT NULL
);

DROP VIEW IF EXISTS framework_governance_scores;

CREATE VIEW framework_governance_scores AS
SELECT
  item,
  item_type,
  description,
  ownership_clarity,
  review_cycle_strength,
  metadata_completeness,
  evidence_status,
  link_health,
  taxonomy_alignment,
  platform_readiness,
  stale_evidence_risk,
  dependency_complexity,
  audience_impact,
  ROUND((
    ownership_clarity
    + review_cycle_strength
    + metadata_completeness
    + evidence_status
    + link_health
    + taxonomy_alignment
    + platform_readiness
  ) / 7.0, 3) AS governance_maturity,
  ROUND(
    CASE
      WHEN (
        (1 - (
          ownership_clarity
          + review_cycle_strength
          + metadata_completeness
          + evidence_status
          + link_health
          + taxonomy_alignment
          + platform_readiness
        ) / 7.0) * 0.34
        + stale_evidence_risk * 0.22
        + (1 - link_health) * 0.16
        + (1 - platform_readiness) * 0.12
        + dependency_complexity * 0.16
      ) > 1 THEN 1
      ELSE (
        (1 - (
          ownership_clarity
          + review_cycle_strength
          + metadata_completeness
          + evidence_status
          + link_health
          + taxonomy_alignment
          + platform_readiness
        ) / 7.0) * 0.34
        + stale_evidence_risk * 0.22
        + (1 - link_health) * 0.16
        + (1 - platform_readiness) * 0.12
        + dependency_complexity * 0.16
      )
    END,
    3
  ) AS maintenance_risk,
  ROUND(
    CASE
      WHEN (
        (
          CASE
            WHEN (
              (1 - (
                ownership_clarity
                + review_cycle_strength
                + metadata_completeness
                + evidence_status
                + link_health
                + taxonomy_alignment
                + platform_readiness
              ) / 7.0) * 0.34
              + stale_evidence_risk * 0.22
              + (1 - link_health) * 0.16
              + (1 - platform_readiness) * 0.12
              + dependency_complexity * 0.16
            ) > 1 THEN 1
            ELSE (
              (1 - (
                ownership_clarity
                + review_cycle_strength
                + metadata_completeness
                + evidence_status
                + link_health
                + taxonomy_alignment
                + platform_readiness
              ) / 7.0) * 0.34
              + stale_evidence_risk * 0.22
              + (1 - link_health) * 0.16
              + (1 - platform_readiness) * 0.12
              + dependency_complexity * 0.16
            )
          END
        ) * 0.70
        + audience_impact * 0.30
      ) > 1 THEN 1
      ELSE (
        (
          CASE
            WHEN (
              (1 - (
                ownership_clarity
                + review_cycle_strength
                + metadata_completeness
                + evidence_status
                + link_health
                + taxonomy_alignment
                + platform_readiness
              ) / 7.0) * 0.34
              + stale_evidence_risk * 0.22
              + (1 - link_health) * 0.16
              + (1 - platform_readiness) * 0.12
              + dependency_complexity * 0.16
            ) > 1 THEN 1
            ELSE (
              (1 - (
                ownership_clarity
                + review_cycle_strength
                + metadata_completeness
                + evidence_status
                + link_health
                + taxonomy_alignment
                + platform_readiness
              ) / 7.0) * 0.34
              + stale_evidence_risk * 0.22
              + (1 - link_health) * 0.16
              + (1 - platform_readiness) * 0.12
              + dependency_complexity * 0.16
            )
          END
        ) * 0.70
        + audience_impact * 0.30
      )
    END,
    3
  ) AS review_priority_score,
  owner,
  status,
  review_date
FROM framework_governance_items;
