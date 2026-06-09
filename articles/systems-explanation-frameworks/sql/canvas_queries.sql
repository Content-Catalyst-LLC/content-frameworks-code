-- Catalyst Canvas Systems Explanation queries.

.headers on
.mode column

SELECT
  item,
  explanation_type,
  quality_score,
  systems_ambiguity,
  review_priority_score,
  status
FROM systems_explanation_scores
ORDER BY review_priority_score DESC;

SELECT
  explanation_type,
  COUNT(*) AS item_count,
  ROUND(AVG(quality_score), 3) AS avg_quality,
  ROUND(AVG(systems_ambiguity), 3) AS avg_ambiguity,
  ROUND(AVG(review_priority_score), 3) AS avg_review_priority
FROM systems_explanation_scores
GROUP BY explanation_type
ORDER BY avg_review_priority DESC;

SELECT
  item,
  explanation_type,
  systems_ambiguity,
  review_priority_score,
  status
FROM systems_explanation_scores
WHERE systems_ambiguity >= 0.45
   OR review_priority_score >= 0.45
   OR status IN ('review', 'revise')
ORDER BY review_priority_score DESC, systems_ambiguity DESC;
