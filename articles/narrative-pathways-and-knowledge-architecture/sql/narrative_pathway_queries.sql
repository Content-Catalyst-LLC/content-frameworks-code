.headers on
.mode csv

SELECT
  reader_state,
  COUNT(*) AS article_count
FROM pathway_article_inventory
GROUP BY reader_state
ORDER BY article_count DESC;

SELECT
  article_role,
  COUNT(*) AS article_count
FROM pathway_article_inventory
GROUP BY article_role
ORDER BY article_count DESC;

SELECT
  pathway_type,
  COUNT(*) AS pathway_count
FROM narrative_pathway_definitions
GROUP BY pathway_type
ORDER BY pathway_count DESC;

SELECT
  a.slug,
  a.title,
  a.status,
  a.article_role,
  a.pathway_role,
  a.reader_state,
  COALESCE(outgoing.outgoing_links, 0) AS outgoing_links,
  COALESCE(incoming.incoming_links, 0) AS incoming_links,
  COALESCE(outgoing.outgoing_links, 0) + COALESCE(incoming.incoming_links, 0) AS total_link_degree,
  CASE
    WHEN a.status = 'planned' THEN 'planned'
    WHEN a.has_series_context != 'yes' OR a.links_to_article_map != 'yes' THEN 'orientation review required'
    WHEN a.has_transition_links != 'yes' OR a.has_next_step != 'yes' THEN 'bridge review required'
    WHEN COALESCE(outgoing.outgoing_links, 0) + COALESCE(incoming.incoming_links, 0) < 2 THEN 'link review required'
    ELSE 'ready'
  END AS pathway_readiness
FROM pathway_article_inventory a
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
ORDER BY pathway_readiness, total_link_degree DESC;

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
