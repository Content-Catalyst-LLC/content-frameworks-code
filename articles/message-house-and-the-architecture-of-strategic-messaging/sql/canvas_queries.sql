-- Catalyst Canvas Message House queries.

.headers on
.mode column

SELECT
  pillar,
  weighted_readiness,
  proof_gap,
  ethical_risk,
  status
FROM message_house_scores
ORDER BY weighted_readiness DESC;

SELECT
  pillar,
  proof_gap,
  ethical_risk,
  status
FROM message_house_scores
WHERE proof_gap >= 0.10
   OR ethical_risk >= 0.50
   OR status IN ('review', 'revise')
ORDER BY proof_gap DESC;
