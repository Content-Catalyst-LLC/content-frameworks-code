.headers on
.mode csv

SELECT
  cluster_name,
  SUM(CASE WHEN status = 'published' THEN 1 ELSE 0 END) AS published_items,
  SUM(CASE WHEN status = 'planned' THEN 1 ELSE 0 END) AS planned_items,
  COUNT(*) AS total_items,
  ROUND(SUM(CASE WHEN status = 'published' THEN 1 ELSE 0 END) * 1.0 / COUNT(*), 3) AS coverage_rate
FROM content_inventory
GROUP BY cluster_name
ORDER BY coverage_rate DESC;

SELECT
  content_type,
  COUNT(*) AS content_count
FROM content_inventory
GROUP BY content_type
ORDER BY content_count DESC;

SELECT
  article_role,
  COUNT(*) AS article_count
FROM content_inventory
GROUP BY article_role
ORDER BY article_count DESC;

SELECT
  relationship_type,
  COUNT(*) AS link_count
FROM internal_links
GROUP BY relationship_type
ORDER BY link_count DESC;

SELECT
  c.slug,
  c.title,
  c.status,
  c.cluster_name,
  c.content_type,
  c.article_role,
  ROUND(
    (
      (m.excerpt = 'yes') +
      (m.tags = 'yes') +
      (m.github_url = 'yes') +
      (m.image_alt = 'yes') +
      (m.references_complete = 'yes') +
      (m.last_reviewed = 'yes') +
      (m.series_context = 'yes') +
      (m.footer_navigation = 'yes')
    ) / 8.0,
    3
  ) AS metadata_completion,
  COALESCE(outgoing.outgoing_links, 0) AS outgoing_links,
  COALESCE(incoming.incoming_links, 0) AS incoming_links,
  COALESCE(outgoing.outgoing_links, 0) + COALESCE(incoming.incoming_links, 0) AS total_link_degree,
  ROUND(
    (
      (r.repository_exists = 'yes') +
      (r.readme_exists = 'yes') +
      (r.python_workflow = 'yes') +
      (r.r_workflow = 'yes') +
      (r.sql_schema = 'yes') +
      (r.workflow_outputs_exist = 'yes') +
      (r.governance_docs = 'yes')
    ) / 7.0,
    3
  ) AS repository_readiness
FROM content_inventory c
LEFT JOIN metadata_inventory m ON c.slug = m.slug
LEFT JOIN repository_inventory r ON c.slug = r.slug
LEFT JOIN (
  SELECT source_slug AS slug, COUNT(*) AS outgoing_links
  FROM internal_links
  GROUP BY source_slug
) outgoing ON c.slug = outgoing.slug
LEFT JOIN (
  SELECT target_slug AS slug, COUNT(*) AS incoming_links
  FROM internal_links
  GROUP BY target_slug
) incoming ON c.slug = incoming.slug
ORDER BY metadata_completion ASC, total_link_degree ASC;
