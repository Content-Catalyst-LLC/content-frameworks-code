.headers on
.mode csv

SELECT asset_type, COUNT(*) AS asset_count
FROM five_w_one_h_content_inventory
GROUP BY asset_type
ORDER BY asset_type;

SELECT audience, COUNT(*) AS asset_count
FROM five_w_one_h_content_inventory
GROUP BY audience
ORDER BY audience;

SELECT
  asset_id,
  asset_name,
  (
    (CASE WHEN who_answered = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN what_answered = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN when_answered = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN where_answered = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN why_answered = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN how_answered = 'yes' THEN 1 ELSE 0 END)
  ) AS answered_question_count,
  (
    (CASE WHEN who_supported = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN what_supported = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN when_supported = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN where_supported = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN why_supported = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN how_supported = 'yes' THEN 1 ELSE 0 END)
  ) AS supported_question_count
FROM five_w_one_h_content_inventory
ORDER BY answered_question_count ASC, supported_question_count ASC, asset_id;

SELECT
  asset_id,
  asset_name,
  (
    (CASE WHEN audience_context_present = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN scope_note_present = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN plain_language_summary_present = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN review_owner_present = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN last_review_date_present = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN freshness_checked = 'yes' THEN 1 ELSE 0 END) +
    (CASE WHEN revision_queue_checked = 'yes' THEN 1 ELSE 0 END)
  ) AS governance_and_audience_features
FROM five_w_one_h_content_inventory
ORDER BY governance_and_audience_features ASC, asset_id;
