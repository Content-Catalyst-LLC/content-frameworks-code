-- Catalyst Canvas schema for Framework Drift and Conceptual Decay.

DROP TABLE IF EXISTS framework_drift_items;

CREATE TABLE framework_drift_items (
  item TEXT PRIMARY KEY,
  item_type TEXT NOT NULL,
  description TEXT NOT NULL,
  definition_consistency REAL NOT NULL CHECK (definition_consistency BETWEEN 0 AND 1),
  boundary_clarity REAL NOT NULL CHECK (boundary_clarity BETWEEN 0 AND 1),
  evidence_currency REAL NOT NULL CHECK (evidence_currency BETWEEN 0 AND 1),
  metadata_consistency REAL NOT NULL CHECK (metadata_consistency BETWEEN 0 AND 1),
  link_health REAL NOT NULL CHECK (link_health BETWEEN 0 AND 1),
  governance_maturity REAL NOT NULL CHECK (governance_maturity BETWEEN 0 AND 1),
  reuse_pressure REAL NOT NULL CHECK (reuse_pressure BETWEEN 0 AND 1),
  stale_evidence_risk REAL NOT NULL CHECK (stale_evidence_risk BETWEEN 0 AND 1),
  dependency_complexity REAL NOT NULL CHECK (dependency_complexity BETWEEN 0 AND 1),
  platform_alignment REAL NOT NULL CHECK (platform_alignment BETWEEN 0 AND 1),
  audience_impact REAL NOT NULL CHECK (audience_impact BETWEEN 0 AND 1),
  owner TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('active', 'review', 'revise', 'archive')),
  review_date TEXT NOT NULL
);

DROP VIEW IF EXISTS framework_drift_scores;

CREATE VIEW framework_drift_scores AS
SELECT
  item,
  item_type,
  description,
  definition_consistency,
  boundary_clarity,
  evidence_currency,
  metadata_consistency,
  link_health,
  governance_maturity,
  reuse_pressure,
  stale_evidence_risk,
  dependency_complexity,
  platform_alignment,
  audience_impact,
  ROUND((
    definition_consistency
    + boundary_clarity
    + evidence_currency
    + metadata_consistency
    + link_health
    + governance_maturity
  ) / 6.0, 3) AS conceptual_integrity,
  ROUND(
    CASE
      WHEN (
        (1 - (
          definition_consistency
          + boundary_clarity
          + evidence_currency
          + metadata_consistency
          + link_health
          + governance_maturity
        ) / 6.0) * 0.32
        + reuse_pressure * 0.20
        + stale_evidence_risk * 0.18
        + dependency_complexity * 0.16
        + (1 - platform_alignment) * 0.14
      ) > 1 THEN 1
      ELSE (
        (1 - (
          definition_consistency
          + boundary_clarity
          + evidence_currency
          + metadata_consistency
          + link_health
          + governance_maturity
        ) / 6.0) * 0.32
        + reuse_pressure * 0.20
        + stale_evidence_risk * 0.18
        + dependency_complexity * 0.16
        + (1 - platform_alignment) * 0.14
      )
    END,
    3
  ) AS drift_risk,
  ROUND(
    CASE
      WHEN (
        (
          CASE
            WHEN (
              (1 - (
                definition_consistency
                + boundary_clarity
                + evidence_currency
                + metadata_consistency
                + link_health
                + governance_maturity
              ) / 6.0) * 0.32
              + reuse_pressure * 0.20
              + stale_evidence_risk * 0.18
              + dependency_complexity * 0.16
              + (1 - platform_alignment) * 0.14
            ) > 1 THEN 1
            ELSE (
              (1 - (
                definition_consistency
                + boundary_clarity
                + evidence_currency
                + metadata_consistency
                + link_health
                + governance_maturity
              ) / 6.0) * 0.32
              + reuse_pressure * 0.20
              + stale_evidence_risk * 0.18
              + dependency_complexity * 0.16
              + (1 - platform_alignment) * 0.14
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
                definition_consistency
                + boundary_clarity
                + evidence_currency
                + metadata_consistency
                + link_health
                + governance_maturity
              ) / 6.0) * 0.32
              + reuse_pressure * 0.20
              + stale_evidence_risk * 0.18
              + dependency_complexity * 0.16
              + (1 - platform_alignment) * 0.14
            ) > 1 THEN 1
            ELSE (
              (1 - (
                definition_consistency
                + boundary_clarity
                + evidence_currency
                + metadata_consistency
                + link_health
                + governance_maturity
              ) / 6.0) * 0.32
              + reuse_pressure * 0.20
              + stale_evidence_risk * 0.18
              + dependency_complexity * 0.16
              + (1 - platform_alignment) * 0.14
            )
          END
        ) * 0.70
        + audience_impact * 0.30
      )
    END,
    3
  ) AS repair_priority_score,
  owner,
  status,
  review_date
FROM framework_drift_items;
