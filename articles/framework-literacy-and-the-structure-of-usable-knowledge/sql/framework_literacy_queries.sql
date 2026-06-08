.headers on
.mode csv

SELECT
  domain,
  ROUND(AVG(
    assumption_awareness +
    blind_spot_recognition +
    boundary_clarity +
    use_condition_clarity +
    evidence_alignment +
    ethical_safety +
    audience_fit +
    domain_fit +
    adaptability +
    governance_readiness
  ), 2) AS average_literacy_score
FROM framework_literacy
GROUP BY domain
ORDER BY average_literacy_score DESC;

SELECT
  framework_id,
  framework_name,
  domain,
  (
    assumption_awareness +
    blind_spot_recognition +
    boundary_clarity +
    use_condition_clarity +
    evidence_alignment +
    ethical_safety +
    audience_fit +
    domain_fit +
    adaptability +
    governance_readiness
  ) AS literacy_score,
  risk_severity,
  primary_blind_spot
FROM framework_literacy
ORDER BY literacy_score DESC;

SELECT
  framework_id,
  framework_name,
  CASE
    WHEN blind_spot_recognition < 4 THEN 'blind-spot documentation required'
    WHEN use_condition_clarity < 4 THEN 'use-condition review required'
    WHEN evidence_alignment < 4 THEN 'evidence review required'
    WHEN ethical_safety < 4 THEN 'ethical review required'
    WHEN governance_readiness < 4 THEN 'governance plan required'
    ELSE 'ready for managed use'
  END AS governance_status
FROM framework_literacy
ORDER BY governance_status;

SELECT
  source_slug,
  COUNT(*) AS outgoing_link_count
FROM internal_links
GROUP BY source_slug
ORDER BY outgoing_link_count DESC;
