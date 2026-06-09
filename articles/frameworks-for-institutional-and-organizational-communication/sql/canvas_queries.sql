-- Catalyst Canvas Institutional and Organizational Communication queries.

.headers on
.mode column

SELECT
  item,
  communication_type,
  quality_score,
  evidence_gap,
  trust_risk,
  review_priority_score,
  status
FROM institutional_communication_scores
ORDER BY review_priority_score DESC;

SELECT
  communication_type,
  COUNT(*) AS item_count,
  ROUND(AVG(quality_score), 3) AS avg_quality,
  ROUND(AVG(trust_risk), 3) AS avg_trust_risk,
  ROUND(AVG(review_priority_score), 3) AS avg_review_priority
FROM institutional_communication_scores
GROUP BY communication_type
ORDER BY avg_review_priority DESC;

SELECT
  item,
  communication_type,
  evidence_gap,
  trust_risk,
  review_priority_score,
  status
FROM institutional_communication_scores
WHERE evidence_gap >= 0.15
   OR trust_risk >= 0.55
   OR review_priority_score >= 0.45
   OR status IN ('review', 'revise')
ORDER BY review_priority_score DESC, trust_risk DESC;
