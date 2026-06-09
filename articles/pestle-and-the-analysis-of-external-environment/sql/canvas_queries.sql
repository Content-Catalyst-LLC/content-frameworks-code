-- Catalyst Canvas PESTLE Analysis queries.

.headers on
.mode column

SELECT
  factor,
  category,
  signal_type,
  weighted_priority,
  evidence_gap,
  monitoring_priority,
  governance_priority,
  status
FROM pestle_scores
ORDER BY governance_priority DESC;

SELECT
  category,
  COUNT(*) AS factor_count,
  ROUND(AVG(weighted_priority), 3) AS avg_weighted_priority,
  ROUND(AVG(evidence_gap), 3) AS avg_evidence_gap,
  ROUND(AVG(monitoring_priority), 3) AS avg_monitoring_priority
FROM pestle_scores
GROUP BY category
ORDER BY category;

SELECT
  factor,
  category,
  signal_type,
  evidence_gap,
  monitoring_priority,
  governance_priority,
  status
FROM pestle_scores
WHERE evidence_gap >= 0.15
   OR monitoring_priority >= 0.50
   OR governance_priority >= 0.75
   OR status IN ('review', 'revise')
ORDER BY governance_priority DESC, monitoring_priority DESC;
