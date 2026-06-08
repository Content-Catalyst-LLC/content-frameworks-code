.headers on
.mode csv

SELECT asset_type, COUNT(*) AS message_count
FROM aida_message_inventory
GROUP BY asset_type
ORDER BY asset_type;

SELECT audience, COUNT(*) AS message_count
FROM aida_message_inventory
GROUP BY audience
ORDER BY audience;

SELECT
  message_id,
  asset_name,
  (
    (CASE WHEN headline_relevant = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN opening_problem_clear = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN attention_claim_supported = 'yes' THEN 1 ELSE 0 END)
  ) AS attention_features,
  (
    (CASE WHEN audience_relevance_visible = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN context_provided = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN evidence_or_example_present = 'yes' THEN 1 ELSE 0 END)
  ) AS interest_features,
  (
    (CASE WHEN value_proposition_clear = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN benefit_claim_supported = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN fit_and_limits_visible = 'yes' THEN 1 ELSE 0 END)
  ) AS desire_features,
  (
    (CASE WHEN cta_clear = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN cta_feasible = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN commitment_transparent = 'yes' THEN 1 ELSE 0 END)
  ) AS action_features
FROM aida_message_inventory
ORDER BY message_id;

SELECT
  message_id,
  asset_name,
  (
    (CASE WHEN uses_false_urgency = 'no' THEN 1 ELSE 0 END) +
    (CASE WHEN uses_exaggerated_claims = 'no' THEN 1 ELSE 0 END) +
    (CASE WHEN uses_hidden_cost_or_condition = 'no' THEN 1 ELSE 0 END) +
    (CASE WHEN audience_agency_preserved = 'yes' THEN 1 ELSE 0 END)
  ) AS ethical_features
FROM aida_message_inventory
ORDER BY ethical_features ASC, message_id;
