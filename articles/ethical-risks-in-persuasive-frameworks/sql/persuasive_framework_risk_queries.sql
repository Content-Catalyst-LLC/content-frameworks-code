.headers on
.mode csv

SELECT framework_used, COUNT(*) AS asset_count
FROM persuasive_framework_risk_inventory
GROUP BY framework_used
ORDER BY framework_used;

SELECT audience, COUNT(*) AS asset_count
FROM persuasive_framework_risk_inventory
GROUP BY audience
ORDER BY audience;

SELECT
  asset_id,
  asset_name,
  framework_used,
  requested_action,
  ROUND(1.0 * supported_persuasive_claims / CASE WHEN total_persuasive_claims = 0 THEN 1 ELSE total_persuasive_claims END, 3) AS evidence_support_ratio,
  (
    (CASE WHEN clear_claim = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN refusal_visible = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN decision_support_present = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN commitment_transparent = 'yes' THEN 1 ELSE 0 END)
  ) AS agency_features,
  (
    (CASE WHEN uses_false_urgency = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN uses_false_scarcity = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN uses_fear_escalation = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN uses_shame_pressure = 'yes' THEN 1 ELSE 0 END)
  ) AS pressure_flags
FROM persuasive_framework_risk_inventory
ORDER BY pressure_flags DESC, evidence_support_ratio ASC, asset_id;

SELECT
  asset_id,
  asset_name,
  (
    (CASE WHEN hidden_terms = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN cancellation_friction = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN preselected_consent = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN disguised_ad = 'yes' THEN 1 ELSE 0 END)
  ) AS dark_pattern_flags
FROM persuasive_framework_risk_inventory
ORDER BY dark_pattern_flags DESC, asset_id;
