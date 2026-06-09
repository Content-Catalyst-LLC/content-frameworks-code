-- Catalyst Canvas Public Reasoning and Framework Design queries.

.headers on
.mode column

SELECT
  item,
  reasoning_type,
  quality_score,
  legitimacy_risk,
  review_priority_score,
  status
FROM public_reasoning_scores
ORDER BY review_priority_score DESC;

SELECT
  reasoning_type,
  COUNT(*) AS item_count,
  ROUND(AVG(quality_score), 3) AS avg_quality,
  ROUND(AVG(legitimacy_risk), 3) AS avg_legitimacy_risk,
  ROUND(AVG(review_priority_score), 3) AS avg_review_priority
FROM public_reasoning_scores
GROUP BY reasoning_type
ORDER BY avg_review_priority DESC;

SELECT
  item,
  reasoning_type,
  legitimacy_risk,
  review_priority_score,
  status
FROM public_reasoning_scores
WHERE legitimacy_risk >= 0.40
   OR review_priority_score >= 0.45
   OR status IN ('review', 'revise')
ORDER BY review_priority_score DESC, legitimacy_risk DESC;
