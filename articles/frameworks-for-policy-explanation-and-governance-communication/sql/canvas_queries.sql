-- Catalyst Canvas Policy Explanation and Governance Communication queries.

.headers on
.mode column

SELECT
  item,
  policy_area,
  completeness_score,
  evidence_gap,
  governance_risk,
  review_priority_score,
  status
FROM policy_governance_scores
ORDER BY review_priority_score DESC;

SELECT
  policy_area,
  COUNT(*) AS item_count,
  ROUND(AVG(completeness_score), 3) AS avg_completeness,
  ROUND(AVG(governance_risk), 3) AS avg_governance_risk,
  ROUND(AVG(review_priority_score), 3) AS avg_review_priority
FROM policy_governance_scores
GROUP BY policy_area
ORDER BY avg_review_priority DESC;

SELECT
  item,
  policy_area,
  evidence_gap,
  governance_risk,
  review_priority_score,
  status
FROM policy_governance_scores
WHERE evidence_gap >= 0.15
   OR governance_risk >= 0.55
   OR review_priority_score >= 0.45
   OR status IN ('review', 'revise')
ORDER BY review_priority_score DESC, governance_risk DESC;
