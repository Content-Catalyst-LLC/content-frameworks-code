-- Catalyst Canvas Sustainability Communication queries.

.headers on
.mode column

SELECT
  claim,
  claim_type,
  quality_score,
  evidence_gap,
  greenwashing_risk,
  review_priority_score,
  status
FROM sustainability_claim_scores
ORDER BY review_priority_score DESC;

SELECT
  claim_type,
  COUNT(*) AS claim_count,
  ROUND(AVG(quality_score), 3) AS avg_quality,
  ROUND(AVG(greenwashing_risk), 3) AS avg_greenwashing_risk,
  ROUND(AVG(review_priority_score), 3) AS avg_review_priority
FROM sustainability_claim_scores
GROUP BY claim_type
ORDER BY avg_review_priority DESC;

SELECT
  claim,
  claim_type,
  evidence_gap,
  greenwashing_risk,
  review_priority_score,
  status
FROM sustainability_claim_scores
WHERE evidence_gap >= 0.15
   OR greenwashing_risk >= 0.55
   OR review_priority_score >= 0.45
   OR status IN ('review', 'revise')
ORDER BY review_priority_score DESC, greenwashing_risk DESC;
