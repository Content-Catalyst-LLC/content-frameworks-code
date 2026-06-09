-- Catalyst Canvas Ansoff Matrix queries.

.headers on
.mode column

SELECT
  option,
  growth_path,
  market_status,
  product_status,
  readiness_score,
  risk_score,
  growth_quality,
  governance_priority,
  status
FROM ansoff_scores
ORDER BY governance_priority DESC;

SELECT
  growth_path,
  COUNT(*) AS option_count,
  ROUND(AVG(readiness_score), 3) AS avg_readiness,
  ROUND(AVG(risk_score), 3) AS avg_risk,
  ROUND(AVG(growth_quality), 3) AS avg_growth_quality
FROM ansoff_scores
GROUP BY growth_path
ORDER BY avg_risk DESC;

SELECT
  option,
  growth_path,
  evidence_gap,
  risk_score,
  governance_priority,
  status
FROM ansoff_scores
WHERE evidence_gap >= 0.15
   OR risk_score >= 0.55
   OR governance_priority >= 0.50
   OR status IN ('review', 'revise')
ORDER BY governance_priority DESC, risk_score DESC;
