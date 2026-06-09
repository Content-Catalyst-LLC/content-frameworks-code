-- Catalyst Canvas Porter Five Forces queries.

.headers on
.mode column

SELECT
  force,
  market_boundary,
  weighted_priority,
  evidence_gap,
  governance_priority,
  status
FROM five_forces_scores
ORDER BY governance_priority DESC;

SELECT
  force,
  COUNT(*) AS record_count,
  ROUND(AVG(weighted_priority), 3) AS avg_weighted_priority,
  ROUND(AVG(evidence_gap), 3) AS avg_evidence_gap,
  ROUND(AVG(governance_priority), 3) AS avg_governance_priority
FROM five_forces_scores
GROUP BY force
ORDER BY avg_governance_priority DESC;

SELECT
  force,
  market_boundary,
  evidence_gap,
  governance_priority,
  status
FROM five_forces_scores
WHERE evidence_gap >= 0.15
   OR governance_priority >= 0.75
   OR status IN ('review', 'revise')
ORDER BY governance_priority DESC, evidence_gap DESC;
