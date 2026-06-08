.headers on
.mode csv

SELECT
  concept_cluster,
  status,
  COUNT(*) AS article_count
FROM learning_path_inventory
GROUP BY concept_cluster, status
ORDER BY concept_cluster, status;

SELECT
  learning_stage,
  COUNT(*) AS article_count
FROM learning_path_inventory
GROUP BY learning_stage
ORDER BY article_count DESC, learning_stage;

SELECT
  l.slug,
  l.title,
  l.status,
  l.learning_stage,
  COUNT(p.prerequisite_slug) AS required_prerequisites,
  SUM(CASE WHEN lp.status = 'published' THEN 1 ELSE 0 END) AS published_prerequisites,
  CASE
    WHEN COUNT(p.prerequisite_slug) = 0 THEN 1.0
    ELSE ROUND(SUM(CASE WHEN lp.status = 'published' THEN 1 ELSE 0 END) * 1.0 / COUNT(p.prerequisite_slug), 3)
  END AS prerequisite_readiness
FROM learning_path_inventory l
LEFT JOIN prerequisite_relationships p
  ON l.slug = p.article_slug
LEFT JOIN learning_path_inventory lp
  ON p.prerequisite_slug = lp.slug
GROUP BY l.slug, l.title, l.status, l.learning_stage
ORDER BY prerequisite_readiness ASC, l.slug;

SELECT
  slug,
  title,
  status,
  learning_stage,
  ROUND(
    0.18 * CASE WHEN orientation_support = 'yes' THEN 1 ELSE 0 END +
    0.18 * CASE WHEN worked_examples = 'yes' THEN 1 ELSE 0 END +
    0.16 * CASE WHEN feedback_prompts = 'yes' THEN 1 ELSE 0 END +
    0.18 * CASE WHEN transfer_support = 'yes' THEN 1 ELSE 0 END +
    0.10 * (
      (CASE WHEN alt_text = 'yes' THEN 1 ELSE 0 END) +
      (CASE WHEN clear_headings = 'yes' THEN 1 ELSE 0 END) +
      (CASE WHEN descriptive_links = 'yes' THEN 1 ELSE 0 END) +
      (CASE WHEN summary_support = 'yes' THEN 1 ELSE 0 END)
    ) / 4.0 -
    CASE
      WHEN cognitive_load_risk = 'high' THEN 0.25
      WHEN cognitive_load_risk = 'medium' THEN 0.10
      ELSE 0
    END,
    3
  ) AS partial_scaffold_score_without_prereq_component
FROM learning_path_inventory
ORDER BY partial_scaffold_score_without_prereq_component ASC, slug;

SELECT
  severity,
  issue_type,
  COUNT(*) AS queue_count
FROM editorial_review_queue
GROUP BY severity, issue_type
ORDER BY severity, issue_type;
