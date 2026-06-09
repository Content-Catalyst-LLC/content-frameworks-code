-- Catalyst Canvas BCG Matrix queries.

.headers on
.mode column

SELECT
  item,
  portfolio_area,
  quadrant,
  growth_score,
  relative_share_score,
  evidence_gap,
  portfolio_priority,
  status
FROM bcg_scores
ORDER BY portfolio_priority DESC;

SELECT
  quadrant,
  COUNT(*) AS item_count,
  ROUND(AVG(growth_score), 3) AS avg_growth_score,
  ROUND(AVG(relative_share_score), 3) AS avg_relative_share_score,
  ROUND(AVG(portfolio_priority), 3) AS avg_portfolio_priority
FROM bcg_scores
GROUP BY quadrant
ORDER BY avg_portfolio_priority DESC;

SELECT
  item,
  quadrant,
  evidence_gap,
  portfolio_priority,
  status
FROM bcg_scores
WHERE evidence_gap >= 0.15
   OR portfolio_priority >= 0.70
   OR status IN ('review', 'revise')
ORDER BY portfolio_priority DESC, evidence_gap DESC;
