-- Catalyst Canvas Positioning Frameworks queries.

.headers on
.mode column

SELECT
  idea,
  category_frame,
  weighted_readiness,
  evidence_gap,
  drift_risk,
  ethical_risk,
  status
FROM positioning_scores
ORDER BY weighted_readiness DESC;

SELECT
  idea,
  evidence_gap,
  drift_risk,
  ethical_risk,
  status
FROM positioning_scores
WHERE evidence_gap >= 0.15
   OR drift_risk >= 0.60
   OR ethical_risk >= 0.50
   OR status IN ('review', 'revise')
ORDER BY evidence_gap DESC, drift_risk DESC;
