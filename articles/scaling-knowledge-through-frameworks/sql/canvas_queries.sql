-- Catalyst Canvas Scaling Knowledge Through Frameworks queries.

.headers on
.mode column

SELECT
  item,
  asset_type,
  scalability_score,
  maintenance_risk,
  review_priority_score,
  status
FROM knowledge_scaling_scores
ORDER BY review_priority_score DESC;

SELECT
  asset_type,
  COUNT(*) AS item_count,
  ROUND(AVG(scalability_score), 3) AS avg_scalability,
  ROUND(AVG(maintenance_risk), 3) AS avg_maintenance_risk,
  ROUND(AVG(review_priority_score), 3) AS avg_review_priority
FROM knowledge_scaling_scores
GROUP BY asset_type
ORDER BY avg_review_priority DESC;

SELECT
  item,
  asset_type,
  maintenance_risk,
  review_priority_score,
  status
FROM knowledge_scaling_scores
WHERE maintenance_risk >= 0.40
   OR review_priority_score >= 0.45
   OR status IN ('review', 'revise')
ORDER BY review_priority_score DESC, maintenance_risk DESC;
