.headers on
.mode csv

SELECT
  lineage,
  COUNT(*) AS framework_count
FROM historical_framework_records
GROUP BY lineage
ORDER BY framework_count DESC;

SELECT
  period,
  COUNT(*) AS framework_count
FROM historical_framework_records
GROUP BY period
ORDER BY framework_count DESC;

SELECT
  framework_id,
  framework_name,
  lineage,
  domain,
  ROUND(
    (
      (purpose_documented = 'yes') +
      (use_conditions_documented = 'yes') +
      (limitations_documented = 'yes') +
      (owner_assigned = 'yes') +
      (review_cycle_defined = 'yes')
    ) / 5.0,
    3
  ) AS governance_score,
  CASE
    WHEN transferred_across_domains = 'yes' AND use_conditions_documented != 'yes' THEN 'transfer review required'
    WHEN risk_severity = 'high' THEN 'high risk review required'
    WHEN (
      (purpose_documented = 'yes') +
      (use_conditions_documented = 'yes') +
      (limitations_documented = 'yes') +
      (owner_assigned = 'yes') +
      (review_cycle_defined = 'yes')
    ) / 5.0 < 0.8 THEN 'governance incomplete'
    WHEN risk_severity = 'medium' THEN 'risk review recommended'
    ELSE 'managed use'
  END AS review_status,
  risk_severity
FROM historical_framework_records
ORDER BY review_status, risk_severity;

SELECT
  source_framework_id,
  COUNT(*) AS outgoing_influence_count
FROM framework_influence_edges
GROUP BY source_framework_id
ORDER BY outgoing_influence_count DESC;

SELECT
  source_slug,
  COUNT(*) AS outgoing_link_count
FROM internal_links
GROUP BY source_slug
ORDER BY outgoing_link_count DESC;
