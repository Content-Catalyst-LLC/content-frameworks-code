-- Catalyst Canvas Framework Drift and Conceptual Decay queries.

.headers on
.mode column

SELECT
  item,
  item_type,
  conceptual_integrity,
  drift_risk,
  repair_priority_score,
  status
FROM framework_drift_scores
ORDER BY repair_priority_score DESC;

SELECT
  item_type,
  COUNT(*) AS item_count,
  ROUND(AVG(conceptual_integrity), 3) AS avg_conceptual_integrity,
  ROUND(AVG(drift_risk), 3) AS avg_drift_risk,
  ROUND(AVG(repair_priority_score), 3) AS avg_repair_priority
FROM framework_drift_scores
GROUP BY item_type
ORDER BY avg_repair_priority DESC;

SELECT
  item,
  item_type,
  drift_risk,
  repair_priority_score,
  status
FROM framework_drift_scores
WHERE drift_risk >= 0.40
   OR repair_priority_score >= 0.55
   OR status IN ('review', 'revise')
ORDER BY repair_priority_score DESC, drift_risk DESC;
