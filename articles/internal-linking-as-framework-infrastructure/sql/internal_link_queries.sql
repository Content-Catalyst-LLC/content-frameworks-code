.headers on
.mode csv

SELECT cluster_name, COUNT(*) AS article_count
FROM article_inventory
GROUP BY cluster_name
ORDER BY article_count DESC, cluster_name;

SELECT relationship_type, COUNT(*) AS link_count
FROM internal_links
GROUP BY relationship_type
ORDER BY link_count DESC, relationship_type;

SELECT
  a.slug,
  a.title,
  a.status,
  COALESCE(incoming.incoming_links, 0) AS incoming_links,
  COALESCE(outgoing.outgoing_links, 0) AS outgoing_links,
  COALESCE(incoming.incoming_links, 0) + COALESCE(outgoing.outgoing_links, 0) AS total_link_degree
FROM article_inventory a
LEFT JOIN (
  SELECT target_slug AS slug, COUNT(*) AS incoming_links
  FROM internal_links
  GROUP BY target_slug
) incoming ON a.slug = incoming.slug
LEFT JOIN (
  SELECT source_slug AS slug, COUNT(*) AS outgoing_links
  FROM internal_links
  GROUP BY source_slug
) outgoing ON a.slug = outgoing.slug
ORDER BY total_link_degree ASC, a.slug;
