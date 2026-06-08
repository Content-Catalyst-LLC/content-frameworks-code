-- Generic Catalyst Canvas article-readiness queries.

.headers on
.mode column

SELECT
  canvas_dimension,
  readiness_score,
  governance_need,
  ethical_risk,
  status
FROM article_canvas_scores
ORDER BY readiness_score ASC;

SELECT
  canvas_dimension,
  readiness_score,
  governance_need,
  ethical_risk,
  status
FROM article_canvas_scores
WHERE readiness_score < 0.74
   OR governance_need >= 0.75
   OR ethical_risk >= 0.50
   OR status IN ('review', 'revise')
ORDER BY readiness_score ASC;
