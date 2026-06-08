DROP TABLE IF EXISTS five_w_one_h_content_inventory;
DROP TABLE IF EXISTS editorial_review_queue;

CREATE TABLE five_w_one_h_content_inventory (
  asset_id TEXT PRIMARY KEY,
  asset_name TEXT NOT NULL,
  asset_type TEXT NOT NULL,
  audience TEXT NOT NULL,
  who_answered TEXT NOT NULL,
  who_supported TEXT NOT NULL,
  what_answered TEXT NOT NULL,
  what_supported TEXT NOT NULL,
  when_answered TEXT NOT NULL,
  when_supported TEXT NOT NULL,
  where_answered TEXT NOT NULL,
  where_supported TEXT NOT NULL,
  why_answered TEXT NOT NULL,
  why_supported TEXT NOT NULL,
  how_answered TEXT NOT NULL,
  how_supported TEXT NOT NULL,
  audience_context_present TEXT NOT NULL,
  scope_note_present TEXT NOT NULL,
  plain_language_summary_present TEXT NOT NULL,
  review_owner_present TEXT NOT NULL,
  last_review_date_present TEXT NOT NULL,
  freshness_checked TEXT NOT NULL,
  revision_queue_checked TEXT NOT NULL
);

CREATE TABLE editorial_review_queue (
  review_id TEXT PRIMARY KEY,
  record_id TEXT NOT NULL,
  issue_type TEXT NOT NULL,
  severity TEXT NOT NULL,
  review_note TEXT NOT NULL
);

.mode csv
.import --skip 1 data/five_w_one_h_content_inventory.csv five_w_one_h_content_inventory
.import --skip 1 data/editorial_review_queue.csv editorial_review_queue
