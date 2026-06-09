-- Catalyst Canvas Strategic Foresight and Scenario Thinking queries.

.headers on
.mode column

SELECT
  item,
  foresight_type,
  quality_score,
  assumption_risk,
  review_priority_score,
  status
FROM strategic_foresight_scores
ORDER BY review_priority_score DESC;

SELECT
  foresight_type,
  COUNT(*) AS item_count,
  ROUND(AVG(quality_score), 3) AS avg_quality,
  ROUND(AVG(assumption_risk), 3) AS avg_assumption_risk,
  ROUND(AVG(review_priority_score), 3) AS avg_review_priority
FROM strategic_foresight_scores
GROUP BY foresight_type
ORDER BY avg_review_priority DESC;

SELECT
  item,
  foresight_type,
  assumption_risk,
  review_priority_score,
  status
FROM strategic_foresight_scores
WHERE assumption_risk >= 0.18
   OR review_priority_score >= 0.45
   OR status IN ('review', 'revise')
ORDER BY review_priority_score DESC, assumption_risk DESC;
