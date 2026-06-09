-- Catalyst Canvas Framework Composition queries.

.headers on
.mode column

SELECT
  item,
  composition_type,
  quality_score,
  confusion_risk,
  review_priority_score,
  status
FROM framework_composition_scores
ORDER BY review_priority_score DESC;

SELECT
  composition_type,
  COUNT(*) AS item_count,
  ROUND(AVG(quality_score), 3) AS avg_quality,
  ROUND(AVG(confusion_risk), 3) AS avg_confusion_risk,
  ROUND(AVG(review_priority_score), 3) AS avg_review_priority
FROM framework_composition_scores
GROUP BY composition_type
ORDER BY avg_review_priority DESC;

SELECT
  item,
  composition_type,
  confusion_risk,
  review_priority_score,
  status
FROM framework_composition_scores
WHERE confusion_risk >= 0.40
   OR review_priority_score >= 0.45
   OR status IN ('review', 'revise')
ORDER BY review_priority_score DESC, confusion_risk DESC;
