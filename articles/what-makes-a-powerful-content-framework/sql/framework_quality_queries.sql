.headers on
.mode csv

SELECT
  domain,
  ROUND(AVG(
    clarity +
    coherence +
    transferability +
    adaptability +
    explanatory_depth +
    domain_fit +
    audience_fit +
    evidence_alignment +
    ethical_safety +
    governability
  ), 2) AS average_quality_score
FROM framework_quality
GROUP BY domain
ORDER BY average_quality_score DESC;

SELECT
  framework_id,
  framework_name,
  domain,
  (
    clarity +
    coherence +
    transferability +
    adaptability +
    explanatory_depth +
    domain_fit +
    audience_fit +
    evidence_alignment +
    ethical_safety +
    governability
  ) AS quality_score,
  ROUND((evidence_alignment + ethical_safety + governability) / 3.0, 2) AS readiness_score,
  risk_severity
FROM framework_quality
ORDER BY quality_score DESC;

SELECT
  slug,
  title,
  ROUND(
    (
      (excerpt = 'yes') +
      (tags = 'yes') +
      (github_url = 'yes') +
      (image_alt = 'yes') +
      (references_complete = 'yes') +
      (last_reviewed = 'yes') +
      (series_context = 'yes') +
      (footer_navigation = 'yes')
    ) / 8.0,
    3
  ) AS metadata_completion_rate
FROM metadata_inventory
ORDER BY metadata_completion_rate ASC;

SELECT
  source_slug,
  COUNT(*) AS outgoing_link_count
FROM internal_links
GROUP BY source_slug
ORDER BY outgoing_link_count DESC;
