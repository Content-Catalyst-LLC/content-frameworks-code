-- Catalyst Canvas Logic Model and Theory of Change queries.

.headers on
.mode column

SELECT
  element,
  model_layer,
  pathway_quality,
  assumption_risk,
  evidence_gap,
  governance_priority,
  status
FROM logic_model_scores
ORDER BY governance_priority DESC;

SELECT
  model_layer,
  COUNT(*) AS element_count,
  ROUND(AVG(pathway_quality), 3) AS avg_pathway_quality,
  ROUND(AVG(assumption_risk), 3) AS avg_assumption_risk,
  ROUND(AVG(governance_priority), 3) AS avg_governance_priority
FROM logic_model_scores
GROUP BY model_layer
ORDER BY avg_governance_priority DESC;

SELECT
  element,
  model_layer,
  assumption_risk,
  evidence_gap,
  governance_priority,
  status
FROM logic_model_scores
WHERE evidence_gap >= 0.15
   OR assumption_risk >= 0.40
   OR governance_priority >= 0.45
   OR status IN ('review', 'revise')
ORDER BY governance_priority DESC, assumption_risk DESC;
