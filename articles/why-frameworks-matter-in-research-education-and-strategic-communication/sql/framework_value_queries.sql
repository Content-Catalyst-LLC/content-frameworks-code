.headers on
.mode csv

SELECT
  cluster_name,
  status,
  COUNT(*) AS article_count
FROM article_map
GROUP BY cluster_name, status
ORDER BY cluster_name, status;

SELECT
  domain,
  ROUND(AVG(
    comprehension +
    comparison +
    retention +
    action_score +
    governance +
    evidence_integrity +
    audience_fit +
    ethical_safety
  ), 2) AS average_framework_value_score
FROM framework_value
GROUP BY domain
ORDER BY average_framework_value_score DESC;

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
