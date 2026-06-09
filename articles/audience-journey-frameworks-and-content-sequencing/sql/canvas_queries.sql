-- Catalyst Canvas Audience Journey queries.

.headers on
.mode column

SELECT
  stage,
  journey_type,
  weighted_readiness,
  link_gap,
  persona_mismatch,
  staleness_risk,
  status
FROM audience_journey_scores
ORDER BY weighted_readiness DESC;

SELECT
  stage,
  link_gap,
  persona_mismatch,
  staleness_risk,
  status
FROM audience_journey_scores
WHERE link_gap > 0
   OR persona_mismatch >= 0.35
   OR staleness_risk >= 0.50
   OR status IN ('review', 'revise')
ORDER BY link_gap DESC, staleness_risk DESC;
