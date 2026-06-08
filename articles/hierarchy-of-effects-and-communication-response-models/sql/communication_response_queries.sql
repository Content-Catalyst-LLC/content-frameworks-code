.headers on
.mode csv

SELECT primary_response_stage, COUNT(*) AS asset_count
FROM communication_response_inventory
GROUP BY primary_response_stage
ORDER BY primary_response_stage;

SELECT audience, COUNT(*) AS asset_count
FROM communication_response_inventory
GROUP BY audience
ORDER BY audience;

SELECT
  asset_id,
  asset_name,
  primary_response_stage,
  (
    (CASE WHEN awareness_supported = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN knowledge_supported = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN liking_supported = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN preference_supported = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN conviction_supported = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN action_supported = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN follow_through_supported = 'yes' THEN 1 ELSE 0 END)
  ) AS supported_stage_count,
  (
    (CASE WHEN awareness_evidence_present = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN knowledge_evidence_present = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN liking_evidence_present = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN preference_evidence_present = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN conviction_evidence_present = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN action_evidence_present = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN follow_through_evidence_present = 'yes' THEN 1 ELSE 0 END)
  ) AS evidence_stage_count
FROM communication_response_inventory
ORDER BY supported_stage_count ASC, evidence_stage_count ASC, asset_id;

SELECT
  asset_id,
  asset_name,
  (
    (CASE WHEN uses_false_urgency = 'no' THEN 1 ELSE 0 END) +
    (CASE WHEN overclaims_response = 'no' THEN 1 ELSE 0 END) +
    (CASE WHEN uses_pressure_cta = 'no' THEN 1 ELSE 0 END) +
    (CASE WHEN audience_agency_preserved = 'yes' THEN 1 ELSE 0 END)
  ) AS ethical_features
FROM communication_response_inventory
ORDER BY ethical_features ASC, asset_id;
