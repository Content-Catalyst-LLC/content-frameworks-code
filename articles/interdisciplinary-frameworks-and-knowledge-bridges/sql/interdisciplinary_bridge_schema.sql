DROP TABLE IF EXISTS knowledge_bridge_inventory;
DROP TABLE IF EXISTS vocabulary_alignment;
DROP TABLE IF EXISTS evidence_compatibility;
DROP TABLE IF EXISTS editorial_review_queue;

CREATE TABLE knowledge_bridge_inventory (
  bridge_id TEXT PRIMARY KEY,
  bridge_title TEXT NOT NULL,
  bridge_type TEXT NOT NULL,
  source_domain TEXT NOT NULL,
  target_domain TEXT NOT NULL,
  source_method_visible TEXT NOT NULL,
  target_method_visible TEXT NOT NULL,
  assumptions_visible TEXT NOT NULL,
  audience_context_present TEXT NOT NULL,
  plain_language_bridge_summary TEXT NOT NULL,
  example_present TEXT NOT NULL,
  misuse_warning_present TEXT NOT NULL,
  review_owner_present TEXT NOT NULL,
  last_review_date_present TEXT NOT NULL,
  revision_queue_checked TEXT NOT NULL
);

CREATE TABLE vocabulary_alignment (
  term_id TEXT PRIMARY KEY,
  bridge_id TEXT NOT NULL,
  term TEXT NOT NULL,
  shared_term TEXT NOT NULL,
  source_definition_present TEXT NOT NULL,
  target_definition_present TEXT NOT NULL,
  translation_note_present TEXT NOT NULL
);

CREATE TABLE evidence_compatibility (
  link_id TEXT PRIMARY KEY,
  bridge_id TEXT NOT NULL,
  evidence_type TEXT NOT NULL,
  evidence_type_classified TEXT NOT NULL,
  method_fit_explained TEXT NOT NULL,
  limitation_visible TEXT NOT NULL
);

CREATE TABLE editorial_review_queue (
  review_id TEXT PRIMARY KEY,
  record_id TEXT NOT NULL,
  issue_type TEXT NOT NULL,
  severity TEXT NOT NULL,
  review_note TEXT NOT NULL
);

.mode csv
.import --skip 1 data/knowledge_bridge_inventory.csv knowledge_bridge_inventory
.import --skip 1 data/vocabulary_alignment.csv vocabulary_alignment
.import --skip 1 data/evidence_compatibility.csv evidence_compatibility
.import --skip 1 data/editorial_review_queue.csv editorial_review_queue
