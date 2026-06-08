.headers on
.mode csv

SELECT
  cluster_name,
  SUM(CASE WHEN status = 'published' THEN 1 ELSE 0 END) AS published_articles,
  SUM(CASE WHEN status = 'planned' THEN 1 ELSE 0 END) AS planned_articles,
  COUNT(*) AS total_articles,
  ROUND(SUM(CASE WHEN status = 'published' THEN 1 ELSE 0 END) * 1.0 / COUNT(*), 3) AS cluster_readiness
FROM pillar_cluster_articles
GROUP BY cluster_name
ORDER BY cluster_readiness DESC;

SELECT
  a.slug,
  a.title,
  a.cluster_name,
  a.status,
  a.article_role,
  COALESCE(outgoing.outgoing_links, 0) AS outgoing_links,
  COALESCE(incoming.incoming_links, 0) AS incoming_links,
  COALESCE(outgoing.outgoing_links, 0) + COALESCE(incoming.incoming_links, 0) AS total_link_degree
FROM pillar_cluster_articles a
LEFT JOIN (
  SELECT source_slug AS slug, COUNT(*) AS outgoing_links
  FROM internal_links
  GROUP BY source_slug
) outgoing ON a.slug = outgoing.slug
LEFT JOIN (
  SELECT target_slug AS slug, COUNT(*) AS incoming_links
  FROM internal_links
  GROUP BY target_slug
) incoming ON a.slug = incoming.slug
ORDER BY total_link_degree DESC;

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
      (footer_navigation = 'yes')
    ) / 8.0,
    3
  ) AS metadata_completion
FROM metadata_inventory
ORDER BY metadata_completion ASC;

SELECT
  relationship_type,
  COUNT(*) AS link_count
FROM internal_links
GROUP BY relationship_type
ORDER BY link_count DESC;
