-- Catalyst Canvas AI-Assisted Framework Design queries.

.headers on
.mode column

SELECT
  item,
  item_type,
  readiness_score,
  ai_framework_risk,
  governance_priority_score,
  status
FROM ai_assisted_framework_design_scores
ORDER BY governance_priority_score DESC;

SELECT
  item_type,
  COUNT(*) AS item_count,
  ROUND(AVG(readiness_score), 3) AS avg_readiness,
  ROUND(AVG(ai_framework_risk), 3) AS avg_ai_risk,
  ROUND(AVG(governance_priority_score), 3) AS avg_governance_priority
FROM ai_assisted_framework_design_scores
GROUP BY item_type
ORDER BY avg_governance_priority DESC;

SELECT
  item,
  item_type,
  ai_framework_risk,
  governance_priority_score,
  status
FROM ai_assisted_framework_design_scores
WHERE ai_framework_risk >= 0.40
   OR governance_priority_score >= 0.55
   OR status IN ('review', 'revise')
ORDER BY governance_priority_score DESC, ai_framework_risk DESC;
