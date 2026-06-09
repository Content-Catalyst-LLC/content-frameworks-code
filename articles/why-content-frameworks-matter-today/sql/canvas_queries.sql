-- Catalyst Canvas Why Content Frameworks Matter Today queries.

.headers on
.mode column

SELECT
  item,
  framework_type,
  value_score,
  framework_risk,
  review_priority_score,
  status
FROM content_framework_value_scores
ORDER BY review_priority_score DESC;

SELECT
  framework_type,
  COUNT(*) AS item_count,
  ROUND(AVG(value_score), 3) AS avg_value,
  ROUND(AVG(framework_risk), 3) AS avg_risk,
  ROUND(AVG(review_priority_score), 3) AS avg_review_priority
FROM content_framework_value_scores
GROUP BY framework_type
ORDER BY avg_review_priority DESC;

SELECT
  item,
  framework_type,
  framework_risk,
  review_priority_score,
  status
FROM content_framework_value_scores
WHERE framework_risk >= 0.40
   OR review_priority_score >= 0.45
   OR status IN ('review', 'revise')
ORDER BY review_priority_score DESC, framework_risk DESC;
