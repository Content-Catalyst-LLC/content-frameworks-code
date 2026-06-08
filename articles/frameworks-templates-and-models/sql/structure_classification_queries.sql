.headers on
.mode csv

SELECT
  observed_type,
  COUNT(*) AS structure_count
FROM content_structure_inventory
GROUP BY observed_type
ORDER BY structure_count DESC;

SELECT
  declared_type,
  observed_type,
  COUNT(*) AS count
FROM content_structure_inventory
GROUP BY declared_type, observed_type
ORDER BY declared_type, observed_type;

SELECT
  structure_id,
  structure_name,
  declared_type,
  observed_type,
  CASE
    WHEN declared_type != observed_type THEN 'declared type mismatch'
    WHEN (
      (purpose_documented = 'yes') +
      (use_conditions_documented = 'yes') +
      (limitations_documented = 'yes') +
      (evidence_alignment_reviewed = 'yes') +
      (ethical_risk_reviewed = 'yes') +
      (owner_assigned = 'yes') +
      (review_cycle_defined = 'yes')
    ) / 7.0 < 0.85 THEN 'governance incomplete'
    WHEN risk_severity IN ('high', 'medium') THEN 'risk review required'
    ELSE 'ready for managed use'
  END AS review_status,
  risk_severity,
  risk_note
FROM content_structure_inventory
ORDER BY review_status, risk_severity;

SELECT
  structure_id,
  structure_name,
  ROUND(
    (
      (purpose_documented = 'yes') +
      (use_conditions_documented = 'yes') +
      (limitations_documented = 'yes') +
      (evidence_alignment_reviewed = 'yes') +
      (ethical_risk_reviewed = 'yes') +
      (owner_assigned = 'yes') +
      (review_cycle_defined = 'yes')
    ) / 7.0,
    3
  ) AS governance_completion
FROM content_structure_inventory
ORDER BY governance_completion ASC;

SELECT
  source_slug,
  COUNT(*) AS outgoing_link_count
FROM internal_links
GROUP BY source_slug
ORDER BY outgoing_link_count DESC;
