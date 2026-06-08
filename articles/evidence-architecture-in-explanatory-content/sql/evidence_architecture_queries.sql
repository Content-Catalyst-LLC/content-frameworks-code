.headers on
.mode csv

SELECT source_type, authority_level, COUNT(*) AS source_count
FROM source_inventory
GROUP BY source_type, authority_level
ORDER BY source_type, authority_level;

SELECT
  c.article_slug,
  COUNT(c.claim_id) AS claim_count,
  SUM(CASE WHEN c.direct_support = 'yes' THEN 1 ELSE 0 END) AS directly_supported_claims
FROM claim_inventory c
GROUP BY c.article_slug
ORDER BY directly_supported_claims ASC, c.article_slug;

SELECT
  e.article_slug,
  e.title,
  (
    (CASE WHEN e.limitations_visible = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN e.uncertainty_visible = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN e.assumptions_visible = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN e.confidence_language_present = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN e.source_review_complete = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN e.last_review_date_present = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN e.revision_queue_checked = 'yes' THEN 1 ELSE 0 END)
  ) AS evidence_architecture_features_present
FROM evidence_architecture_inventory e
ORDER BY evidence_architecture_features_present ASC, e.article_slug;

SELECT
  v.article_slug,
  COUNT(v.visual_id) AS visual_count,
  SUM(CASE WHEN v.source_visible = 'yes' THEN 1 ELSE 0 END) AS visuals_with_sources,
  SUM(CASE WHEN v.alt_text_present = 'yes' THEN 1 ELSE 0 END) AS visuals_with_alt_text,
  SUM(CASE WHEN v.visual_limitations_visible = 'yes' THEN 1 ELSE 0 END) AS visuals_with_limitations
FROM visual_evidence_inventory v
GROUP BY v.article_slug
ORDER BY visuals_with_limitations ASC, v.article_slug;
