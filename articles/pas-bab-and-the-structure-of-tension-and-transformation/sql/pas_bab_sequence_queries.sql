.headers on
.mode csv

SELECT framework_used, COUNT(*) AS message_count
FROM pas_bab_message_inventory
GROUP BY framework_used
ORDER BY framework_used;

SELECT audience, COUNT(*) AS message_count
FROM pas_bab_message_inventory
GROUP BY audience
ORDER BY audience;

SELECT
  message_id,
  asset_name,
  framework_used,
  (
    (CASE WHEN problem_clear = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN before_state_specific = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN audience_context_present = 'yes' THEN 1 ELSE 0 END)
  ) AS current_state_features,
  (
    (CASE WHEN stakes_visible = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN agitation_proportionate = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN consequence_supported = 'yes' THEN 1 ELSE 0 END)
  ) AS stakes_features,
  (
    (CASE WHEN after_state_credible = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN transformation_bounded = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN benefit_claim_supported = 'yes' THEN 1 ELSE 0 END)
  ) AS transformation_features,
  (
    (CASE WHEN solution_fit_clear = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN bridge_mechanism_visible = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN commitment_transparent = 'yes' THEN 1 ELSE 0 END)
  ) AS bridge_features
FROM pas_bab_message_inventory
ORDER BY message_id;

SELECT
  message_id,
  asset_name,
  (
    (CASE WHEN uses_invented_pain = 'no' THEN 1 ELSE 0 END) +
    (CASE WHEN uses_fear_escalation = 'no' THEN 1 ELSE 0 END) +
    (CASE WHEN uses_false_urgency = 'no' THEN 1 ELSE 0 END) +
    (CASE WHEN audience_agency_preserved = 'yes' THEN 1 ELSE 0 END)
  ) AS ethical_features
FROM pas_bab_message_inventory
ORDER BY ethical_features ASC, message_id;
