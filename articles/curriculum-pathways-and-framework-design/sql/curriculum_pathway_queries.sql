.headers on
.mode csv

SELECT pathway_cluster, status, COUNT(*) AS node_count
FROM curriculum_pathway_inventory
GROUP BY pathway_cluster, status
ORDER BY pathway_cluster, status;

SELECT learning_stage, COUNT(*) AS node_count
FROM curriculum_pathway_inventory
GROUP BY learning_stage
ORDER BY node_count DESC, learning_stage;

SELECT
  n.node_slug,
  n.title,
  COUNT(p.prerequisite_slug) AS required_prerequisites,
  SUM(CASE WHEN pn.status = 'published' THEN 1 ELSE 0 END) AS published_prerequisites
FROM curriculum_pathway_inventory n
LEFT JOIN prerequisite_relationships p ON n.node_slug = p.node_slug
LEFT JOIN curriculum_pathway_inventory pn ON p.prerequisite_slug = pn.node_slug
GROUP BY n.node_slug, n.title
ORDER BY published_prerequisites ASC, n.node_slug;

SELECT
  n.node_slug,
  n.title,
  COUNT(o.objective_id) AS objective_count,
  SUM(CASE WHEN o.support_material_present = 'yes' THEN 1 ELSE 0 END) AS supported_objectives,
  SUM(CASE WHEN o.assessment_present = 'yes' THEN 1 ELSE 0 END) AS assessed_objectives
FROM curriculum_pathway_inventory n
LEFT JOIN learning_objectives o ON n.node_slug = o.node_slug AND o.required = 'yes'
GROUP BY n.node_slug, n.title
ORDER BY supported_objectives ASC, n.node_slug;

SELECT
  node_slug,
  title,
  (
    (CASE WHEN clear_headings = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN descriptive_links = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN alt_text = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN plain_language_summary = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN reflection_prompt = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN assessment_point = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN revision_prompt = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN application_example = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN transfer_task = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN repository_support = 'yes' THEN 1 ELSE 0 END)
  ) AS pathway_support_features_present
FROM curriculum_pathway_inventory
ORDER BY pathway_support_features_present ASC, node_slug;
