-- Catalyst Canvas SWOT Analysis queries.

.headers on
.mode column

SELECT
  item,
  quadrant,
  orientation,
  weighted_priority,
  evidence_gap,
  governance_priority,
  status
FROM swot_scores
ORDER BY governance_priority DESC;

SELECT
  quadrant,
  COUNT(*) AS item_count,
  ROUND(AVG(weighted_priority), 3) AS avg_weighted_priority,
  ROUND(AVG(evidence_gap), 3) AS avg_evidence_gap
FROM swot_scores
GROUP BY quadrant
ORDER BY quadrant;

SELECT
  item,
  quadrant,
  evidence_gap,
  governance_priority,
  status
FROM swot_scores
WHERE evidence_gap >= 0.15
   OR governance_priority >= 0.75
   OR status IN ('review', 'revise')
ORDER BY governance_priority DESC, evidence_gap DESC;
