.headers on
.mode csv

SELECT story_purpose, COUNT(*) AS asset_count
FROM storytelling_framework_inventory
GROUP BY story_purpose
ORDER BY story_purpose;

SELECT audience, COUNT(*) AS asset_count
FROM storytelling_framework_inventory
GROUP BY audience
ORDER BY audience;

SELECT
  asset_id,
  asset_name,
  story_purpose,
  (
    (CASE WHEN context_present = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN actors_present = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN tension_present = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN sequence_present = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN transformation_present = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN action_present = 'yes' THEN 1 ELSE 0 END)
  ) AS narrative_dimension_count,
  (
    (CASE WHEN context_supported = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN actors_supported = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN tension_supported = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN sequence_supported = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN transformation_supported = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN action_supported = 'yes' THEN 1 ELSE 0 END)
  ) AS supported_dimension_count
FROM storytelling_framework_inventory
ORDER BY narrative_dimension_count ASC, supported_dimension_count ASC, asset_id;

SELECT
  asset_id,
  asset_name,
  (
    (CASE WHEN uses_savior_framing = 'no' THEN 1 ELSE 0 END) +
    (CASE WHEN overdramatizes_tension = 'no' THEN 1 ELSE 0 END) +
    (CASE WHEN uses_unsupported_anecdote = 'no' THEN 1 ELSE 0 END) +
    (CASE WHEN uses_pressure_cta = 'no' THEN 1 ELSE 0 END)
  ) AS ethical_features
FROM storytelling_framework_inventory
ORDER BY ethical_features ASC, asset_id;
