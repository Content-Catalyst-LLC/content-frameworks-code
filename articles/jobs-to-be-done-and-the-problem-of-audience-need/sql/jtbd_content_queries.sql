.headers on
.mode csv

SELECT primary_job, COUNT(*) AS asset_count
FROM jtbd_content_inventory
GROUP BY primary_job
ORDER BY primary_job;

SELECT audience, COUNT(*) AS asset_count
FROM jtbd_content_inventory
GROUP BY audience
ORDER BY audience;

SELECT
  asset_id,
  asset_name,
  primary_job,
  ROUND(1.0 * supported_job_assumptions / CASE WHEN total_job_assumptions = 0 THEN 1 ELSE total_job_assumptions END, 3) AS evidence_support_ratio,
  (
    (CASE WHEN situation_defined = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN motivation_defined = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN desired_outcome_defined = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN constraint_defined = 'yes' THEN 1 ELSE 0 END)
  ) AS job_clarity_features,
  (
    (CASE WHEN format_matches_job = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN examples_match_job = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN sections_match_job = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN next_step_matches_job = 'yes' THEN 1 ELSE 0 END)
  ) AS content_fit_features
FROM jtbd_content_inventory
ORDER BY evidence_support_ratio ASC, job_clarity_features ASC, content_fit_features ASC, asset_id;

SELECT
  asset_id,
  asset_name,
  (
    (CASE WHEN functional_job_supported = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN emotional_job_supported = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN social_job_supported = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN strategic_job_supported = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN learning_job_supported = 'yes' THEN 1 ELSE 0 END)
  ) AS supported_job_dimensions
FROM jtbd_content_inventory
ORDER BY supported_job_dimensions ASC, asset_id;
