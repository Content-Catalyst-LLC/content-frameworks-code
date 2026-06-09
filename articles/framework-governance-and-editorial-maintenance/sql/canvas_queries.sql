-- Catalyst Canvas Framework Governance and Editorial Maintenance queries.

.headers on
.mode column

SELECT
  item,
  item_type,
  governance_maturity,
  maintenance_risk,
  review_priority_score,
  status
FROM framework_governance_scores
ORDER BY review_priority_score DESC;

SELECT
  item_type,
  COUNT(*) AS item_count,
  ROUND(AVG(governance_maturity), 3) AS avg_governance_maturity,
  ROUND(AVG(maintenance_risk), 3) AS avg_maintenance_risk,
  ROUND(AVG(review_priority_score), 3) AS avg_review_priority
FROM framework_governance_scores
GROUP BY item_type
ORDER BY avg_review_priority DESC;

SELECT
  item,
  item_type,
  maintenance_risk,
  review_priority_score,
  status
FROM framework_governance_scores
WHERE maintenance_risk >= 0.40
   OR review_priority_score >= 0.55
   OR status IN ('review', 'revise')
ORDER BY review_priority_score DESC, maintenance_risk DESC;
