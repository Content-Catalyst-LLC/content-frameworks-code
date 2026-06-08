.headers on
.mode csv

SELECT
  c.category_id,
  c.category_name,
  c.category_type,
  c.status,
  SUM(CASE WHEN a.assignment_type = 'primary' THEN 1 ELSE 0 END) AS primary_item_count,
  SUM(CASE WHEN a.assignment_type = 'secondary' THEN 1 ELSE 0 END) AS secondary_item_count,
  SUM(CASE WHEN a.assignment_type = 'facet' THEN 1 ELSE 0 END) AS facet_item_count,
  COUNT(a.assignment_id) AS total_assignment_count
FROM taxonomy_categories c
LEFT JOIN taxonomy_assignments a ON c.category_id = a.category_id
GROUP BY c.category_id, c.category_name, c.category_type, c.status
ORDER BY primary_item_count DESC, total_assignment_count DESC;

SELECT
  i.slug,
  i.title,
  i.status,
  i.article_role,
  SUM(CASE WHEN a.assignment_type = 'primary' THEN 1 ELSE 0 END) AS primary_category_count,
  SUM(CASE WHEN a.assignment_type = 'secondary' THEN 1 ELSE 0 END) AS secondary_category_count,
  SUM(CASE WHEN a.assignment_type = 'facet' THEN 1 ELSE 0 END) AS facet_assignment_count
FROM article_inventory i
LEFT JOIN taxonomy_assignments a ON i.slug = a.slug
GROUP BY i.slug, i.title, i.status, i.article_role
ORDER BY primary_category_count ASC, i.slug;

SELECT
  slug,
  title,
  status,
  ROUND(
    (
      (primary_category = 'yes') +
      (secondary_categories = 'yes') +
      (article_role = 'yes') +
      (reader_stage = 'yes') +
      (governance_owner = 'yes') +
      (last_reviewed = 'yes') +
      (category_definition = 'yes') +
      (boundary_notes = 'yes')
    ) / 8.0,
    3
  ) AS taxonomy_metadata_completion
FROM taxonomy_metadata_inventory
ORDER BY taxonomy_metadata_completion ASC;

SELECT
  assignment_type,
  COUNT(*) AS assignment_count
FROM taxonomy_assignments
GROUP BY assignment_type
ORDER BY assignment_count DESC;

SELECT
  category_type,
  COUNT(*) AS category_count
FROM taxonomy_categories
GROUP BY category_type
ORDER BY category_count DESC;

SELECT
  relationship_type,
  COUNT(*) AS category_count
FROM taxonomy_categories
GROUP BY relationship_type
ORDER BY category_count DESC;
