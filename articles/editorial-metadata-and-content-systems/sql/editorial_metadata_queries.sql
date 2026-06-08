.headers on
.mode csv

SELECT
  slug,
  title,
  status,
  cluster_name,
  article_type,
  ROUND(
    (
      (title <> '') +
      (seo_title <> '') +
      (slug <> '') +
      (series <> '') +
      (cluster_name <> '') +
      (article_type <> '') +
      (status <> '') +
      (description <> '') +
      (excerpt = 'yes') +
      (tags <> '') +
      (image_title <> '') +
      (image_filename <> '') +
      (alt_text <> '') +
      (caption <> '') +
      (image_description <> '') +
      (references_complete = 'yes') +
      (repository_url <> '') +
      (repository_path <> '') +
      (previous_title <> '') +
      (article_map_title <> '') +
      (article_map_url <> '') +
      (next_title <> '') +
      (last_reviewed <> '')
    ) / 23.0,
    3
  ) AS metadata_completion_rate
FROM editorial_metadata_inventory
ORDER BY metadata_completion_rate ASC, slug;

SELECT
  slug,
  title,
  repository_path,
  'articles/' || slug || '/' AS expected_repository_path,
  repository_path = 'articles/' || slug || '/' AS repository_path_aligned
FROM editorial_metadata_inventory
ORDER BY slug;

SELECT
  slug,
  previous_title,
  previous_url,
  article_map_title,
  article_map_url,
  next_title,
  next_url
FROM editorial_metadata_inventory
ORDER BY article_order;

SELECT
  slug,
  COUNT(*) AS reference_records,
  SUM(CASE WHEN authority_level = 'high' THEN 1 ELSE 0 END) AS high_authority_sources,
  SUM(CASE WHEN review_status = 'ready' THEN 1 ELSE 0 END) AS ready_reference_records
FROM reference_metadata
GROUP BY slug
ORDER BY reference_records DESC;

SELECT
  severity,
  issue_type,
  COUNT(*) AS queue_count
FROM editorial_review_queue
GROUP BY severity, issue_type
ORDER BY severity, issue_type;
