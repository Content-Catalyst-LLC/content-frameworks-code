.headers on
.mode csv

SELECT
  cluster_name,
  status,
  COUNT(*) AS article_count
FROM content_inventory
GROUP BY cluster_name, status
ORDER BY cluster_name, status;

SELECT
  slug,
  title,
  status,
  ROUND(
    (
      (excerpt = 'yes') +
      (tags = 'yes') +
      (github_url = 'yes') +
      (image_alt = 'yes') +
      (references_complete = 'yes') +
      (last_reviewed = 'yes') +
      (series_context = 'yes') +
      (footer_navigation = 'yes') +
      (repository_manifest = 'yes') +
      (accessibility_notes = 'yes')
    ) / 10.0,
    3
  ) AS metadata_completion_rate
FROM content_inventory
ORDER BY metadata_completion_rate ASC, slug;

SELECT
  a.slug,
  a.title,
  a.status,
  COALESCE(i.incoming_links, 0) AS incoming_links,
  COALESCE(o.outgoing_links, 0) AS outgoing_links,
  COALESCE(i.incoming_links, 0) + COALESCE(o.outgoing_links, 0) AS total_link_degree
FROM content_inventory a
LEFT JOIN (
  SELECT target_slug AS slug, COUNT(*) AS incoming_links
  FROM internal_links
  GROUP BY target_slug
) i
  ON a.slug = i.slug
LEFT JOIN (
  SELECT source_slug AS slug, COUNT(*) AS outgoing_links
  FROM internal_links
  GROUP BY source_slug
) o
  ON a.slug = o.slug
ORDER BY total_link_degree ASC, a.slug;

SELECT
  slug,
  COUNT(*) AS evidence_records,
  SUM(CASE WHEN authority_level = 'high' THEN 1 ELSE 0 END) AS high_authority_sources,
  SUM(CASE WHEN review_status = 'ready' THEN 1 ELSE 0 END) AS ready_evidence_records
FROM evidence_register
GROUP BY slug
ORDER BY evidence_records DESC;

SELECT
  severity,
  issue_type,
  COUNT(*) AS queue_count
FROM editorial_review_queue
GROUP BY severity, issue_type
ORDER BY severity, issue_type;
