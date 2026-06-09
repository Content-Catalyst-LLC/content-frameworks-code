-- Catalyst Canvas The Limits of Framework Thinking queries.

.headers on
.mode column

SELECT
  item,
  framework_type,
  usefulness_score,
  distortion_risk,
  review_priority_score,
  status
FROM framework_limits_scores
ORDER BY review_priority_score DESC;

SELECT
  framework_type,
  COUNT(*) AS item_count,
  ROUND(AVG(usefulness_score), 3) AS avg_usefulness,
  ROUND(AVG(distortion_risk), 3) AS avg_distortion_risk,
  ROUND(AVG(review_priority_score), 3) AS avg_review_priority
FROM framework_limits_scores
GROUP BY framework_type
ORDER BY avg_review_priority DESC;

SELECT
  item,
  framework_type,
  distortion_risk,
  review_priority_score,
  status
FROM framework_limits_scores
WHERE distortion_risk >= 0.40
   OR review_priority_score >= 0.45
   OR status IN ('review', 'revise')
ORDER BY review_priority_score DESC, distortion_risk DESC;
