.headers on
.mode csv

SELECT source_domain, target_domain, COUNT(*) AS bridge_count
FROM knowledge_bridge_inventory
GROUP BY source_domain, target_domain
ORDER BY source_domain, target_domain;

SELECT bridge_type, COUNT(*) AS bridge_count
FROM knowledge_bridge_inventory
GROUP BY bridge_type
ORDER BY bridge_count DESC, bridge_type;

SELECT
  k.bridge_id,
  k.bridge_title,
  COUNT(v.term_id) AS shared_terms,
  SUM(CASE WHEN v.source_definition_present = 'yes'
       AND v.target_definition_present = 'yes'
       AND v.translation_note_present = 'yes' THEN 1 ELSE 0 END) AS aligned_terms
FROM knowledge_bridge_inventory k
LEFT JOIN vocabulary_alignment v ON k.bridge_id = v.bridge_id AND v.shared_term = 'yes'
GROUP BY k.bridge_id, k.bridge_title
ORDER BY aligned_terms ASC, k.bridge_id;

SELECT
  k.bridge_id,
  k.bridge_title,
  COUNT(e.link_id) AS evidence_links,
  SUM(CASE WHEN e.evidence_type_classified = 'yes'
       AND e.method_fit_explained = 'yes'
       AND e.limitation_visible = 'yes' THEN 1 ELSE 0 END) AS compatible_evidence_links
FROM knowledge_bridge_inventory k
LEFT JOIN evidence_compatibility e ON k.bridge_id = e.bridge_id
GROUP BY k.bridge_id, k.bridge_title
ORDER BY compatible_evidence_links ASC, k.bridge_id;

SELECT
  bridge_id,
  bridge_title,
  (
    (CASE WHEN source_method_visible = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN target_method_visible = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN assumptions_visible = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN audience_context_present = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN plain_language_bridge_summary = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN example_present = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN misuse_warning_present = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN review_owner_present = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN last_review_date_present = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN revision_queue_checked = 'yes' THEN 1 ELSE 0 END)
  ) AS bridge_support_features_present
FROM knowledge_bridge_inventory
ORDER BY bridge_support_features_present ASC, bridge_id;
