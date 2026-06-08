.headers on
.mode csv

SELECT research_domain, status, COUNT(*) AS article_count
FROM research_communication_inventory
GROUP BY research_domain, status
ORDER BY research_domain, status;

SELECT source_type, authority_level, COUNT(*) AS source_count
FROM source_inventory
GROUP BY source_type, authority_level
ORDER BY source_type, authority_level;

SELECT
  c.article_slug,
  COUNT(c.claim_id) AS claim_count,
  SUM(CASE WHEN c.claim_supported = 'yes' THEN 1 ELSE 0 END) AS supported_claims
FROM claim_inventory c
GROUP BY c.article_slug
ORDER BY supported_claims ASC, c.article_slug;

SELECT
  r.article_slug,
  r.title,
  (
    (CASE WHEN r.method_explained = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN r.limitations_visible = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN r.uncertainty_visible = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN r.assumptions_visible = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN r.confidence_language_present = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN r.audience_defined = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN r.prior_knowledge_supported = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN r.plain_language_summary = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN r.implications_bounded = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN r.visuals_accessible = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN r.tables_explained = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN r.alt_text_present = 'yes' THEN 1 ELSE 0 END)
  ) AS readiness_features_present
FROM research_communication_inventory r
ORDER BY readiness_features_present ASC, r.article_slug;
