-- Catalyst Canvas OKR KPI Measurement Frameworks queries.

.headers on
.mode column

SELECT
  item,
  measurement_type,
  quality_score,
  measurement_risk,
  evidence_gap,
  governance_priority,
  status
FROM measurement_scores
ORDER BY governance_priority DESC;

SELECT
  measurement_type,
  COUNT(*) AS item_count,
  ROUND(AVG(quality_score), 3) AS avg_quality,
  ROUND(AVG(measurement_risk), 3) AS avg_risk,
  ROUND(AVG(governance_priority), 3) AS avg_governance_priority
FROM measurement_scores
GROUP BY measurement_type
ORDER BY avg_governance_priority DESC;

SELECT
  item,
  measurement_type,
  measurement_risk,
  evidence_gap,
  governance_priority,
  status
FROM measurement_scores
WHERE evidence_gap >= 0.15
   OR measurement_risk >= 0.55
   OR governance_priority >= 0.45
   OR status IN ('review', 'revise')
ORDER BY governance_priority DESC, measurement_risk DESC;
