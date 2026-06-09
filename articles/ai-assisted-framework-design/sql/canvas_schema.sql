-- Catalyst Canvas schema for AI-Assisted Framework Design.

DROP TABLE IF EXISTS ai_assisted_framework_design_items;

CREATE TABLE ai_assisted_framework_design_items (
  item TEXT PRIMARY KEY,
  item_type TEXT NOT NULL,
  description TEXT NOT NULL,
  conceptual_clarity REAL NOT NULL CHECK (conceptual_clarity BETWEEN 0 AND 1),
  evidence_grounding REAL NOT NULL CHECK (evidence_grounding BETWEEN 0 AND 1),
  metadata_consistency REAL NOT NULL CHECK (metadata_consistency BETWEEN 0 AND 1),
  human_review_strength REAL NOT NULL CHECK (human_review_strength BETWEEN 0 AND 1),
  bias_review REAL NOT NULL CHECK (bias_review BETWEEN 0 AND 1),
  governance_maturity REAL NOT NULL CHECK (governance_maturity BETWEEN 0 AND 1),
  platform_readiness REAL NOT NULL CHECK (platform_readiness BETWEEN 0 AND 1),
  drift_control REAL NOT NULL CHECK (drift_control BETWEEN 0 AND 1),
  unsupported_claim_risk REAL NOT NULL CHECK (unsupported_claim_risk BETWEEN 0 AND 1),
  generic_structure_risk REAL NOT NULL CHECK (generic_structure_risk BETWEEN 0 AND 1),
  output_validation REAL NOT NULL CHECK (output_validation BETWEEN 0 AND 1),
  audience_impact REAL NOT NULL CHECK (audience_impact BETWEEN 0 AND 1),
  owner TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('active', 'review', 'revise', 'archive')),
  review_date TEXT NOT NULL
);

DROP VIEW IF EXISTS ai_assisted_framework_design_scores;

CREATE VIEW ai_assisted_framework_design_scores AS
SELECT
  item,
  item_type,
  description,
  conceptual_clarity,
  evidence_grounding,
  metadata_consistency,
  human_review_strength,
  bias_review,
  governance_maturity,
  platform_readiness,
  drift_control,
  unsupported_claim_risk,
  generic_structure_risk,
  output_validation,
  audience_impact,
  ROUND((
    conceptual_clarity
    + evidence_grounding
    + metadata_consistency
    + human_review_strength
    + bias_review
    + governance_maturity
    + platform_readiness
    + drift_control
  ) / 8.0, 3) AS readiness_score,
  ROUND(
    CASE
      WHEN (
        (1 - (
          conceptual_clarity
          + evidence_grounding
          + metadata_consistency
          + human_review_strength
          + bias_review
          + governance_maturity
          + platform_readiness
          + drift_control
        ) / 8.0) * 0.32
        + unsupported_claim_risk * 0.24
        + generic_structure_risk * 0.18
        + (1 - bias_review) * 0.14
        + (1 - output_validation) * 0.12
      ) > 1 THEN 1
      ELSE (
        (1 - (
          conceptual_clarity
          + evidence_grounding
          + metadata_consistency
          + human_review_strength
          + bias_review
          + governance_maturity
          + platform_readiness
          + drift_control
        ) / 8.0) * 0.32
        + unsupported_claim_risk * 0.24
        + generic_structure_risk * 0.18
        + (1 - bias_review) * 0.14
        + (1 - output_validation) * 0.12
      )
    END,
    3
  ) AS ai_framework_risk,
  ROUND(
    CASE
      WHEN (
        (
          CASE
            WHEN (
              (1 - (
                conceptual_clarity
                + evidence_grounding
                + metadata_consistency
                + human_review_strength
                + bias_review
                + governance_maturity
                + platform_readiness
                + drift_control
              ) / 8.0) * 0.32
              + unsupported_claim_risk * 0.24
              + generic_structure_risk * 0.18
              + (1 - bias_review) * 0.14
              + (1 - output_validation) * 0.12
            ) > 1 THEN 1
            ELSE (
              (1 - (
                conceptual_clarity
                + evidence_grounding
                + metadata_consistency
                + human_review_strength
                + bias_review
                + governance_maturity
                + platform_readiness
                + drift_control
              ) / 8.0) * 0.32
              + unsupported_claim_risk * 0.24
              + generic_structure_risk * 0.18
              + (1 - bias_review) * 0.14
              + (1 - output_validation) * 0.12
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
                conceptual_clarity
                + evidence_grounding
                + metadata_consistency
                + human_review_strength
                + bias_review
                + governance_maturity
                + platform_readiness
                + drift_control
              ) / 8.0) * 0.32
              + unsupported_claim_risk * 0.24
              + generic_structure_risk * 0.18
              + (1 - bias_review) * 0.14
              + (1 - output_validation) * 0.12
            ) > 1 THEN 1
            ELSE (
              (1 - (
                conceptual_clarity
                + evidence_grounding
                + metadata_consistency
                + human_review_strength
                + bias_review
                + governance_maturity
                + platform_readiness
                + drift_control
              ) / 8.0) * 0.32
              + unsupported_claim_risk * 0.24
              + generic_structure_risk * 0.18
              + (1 - bias_review) * 0.14
              + (1 - output_validation) * 0.12
            )
          END
        ) * 0.70
        + audience_impact * 0.30
      )
    END,
    3
  ) AS governance_priority_score,
  owner,
  status,
  review_date
FROM ai_assisted_framework_design_items;
