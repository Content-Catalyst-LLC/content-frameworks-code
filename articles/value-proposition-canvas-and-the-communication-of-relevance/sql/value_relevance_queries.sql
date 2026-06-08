WITH scored AS (
  SELECT
    item_id,
    title,
    audience_segment,
    status,
    ROUND((job_alignment + pain_relief_alignment + gain_creation_alignment + evidence_strength + communication_clarity + ethical_fit) / 6.0, 3) AS relevance_score,
    primary_risk
  FROM value_relevance_items
)
SELECT
  item_id,
  title,
  audience_segment,
  status,
  relevance_score,
  CASE
    WHEN relevance_score >= 0.88 THEN 'strong relevance'
    WHEN relevance_score >= 0.78 THEN 'publishable with review'
    WHEN relevance_score >= 0.60 THEN 'revise before publication'
    ELSE 'major relevance gap'
  END AS classification,
  primary_risk
FROM scored
ORDER BY relevance_score DESC;
