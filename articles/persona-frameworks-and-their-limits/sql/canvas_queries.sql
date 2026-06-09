-- Catalyst Canvas Persona Frameworks queries.

.headers on
.mode column

SELECT
  persona,
  segment,
  weighted_readiness,
  risk_score,
  revision_pressure,
  status
FROM persona_scores
ORDER BY weighted_readiness DESC;

SELECT
  persona,
  segment,
  risk_score,
  revision_pressure,
  status
FROM persona_scores
WHERE risk_score >= 0.50
   OR revision_pressure >= 0.15
   OR status IN ('review', 'revise')
ORDER BY risk_score DESC, revision_pressure DESC;
