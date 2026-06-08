DROP TABLE IF EXISTS evidence_architecture_inventory;
DROP TABLE IF EXISTS claim_inventory;
DROP TABLE IF EXISTS source_inventory;
DROP TABLE IF EXISTS visual_evidence_inventory;
DROP TABLE IF EXISTS editorial_review_queue;

CREATE TABLE evidence_architecture_inventory (
  article_slug TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  status TEXT NOT NULL,
  limitations_visible TEXT NOT NULL,
  uncertainty_visible TEXT NOT NULL,
  assumptions_visible TEXT NOT NULL,
  confidence_language_present TEXT NOT NULL,
  source_review_complete TEXT NOT NULL,
  last_review_date_present TEXT NOT NULL,
  revision_queue_checked TEXT NOT NULL
);

CREATE TABLE claim_inventory (
  claim_id TEXT PRIMARY KEY,
  article_slug TEXT NOT NULL,
  claim_type TEXT NOT NULL,
  claim_strength TEXT NOT NULL,
  source_id TEXT NOT NULL,
  direct_support TEXT NOT NULL
);

CREATE TABLE source_inventory (
  source_id TEXT PRIMARY KEY,
  source_title TEXT NOT NULL,
  source_type TEXT NOT NULL,
  authority_level TEXT NOT NULL,
  review_status TEXT NOT NULL
);

CREATE TABLE visual_evidence_inventory (
  visual_id TEXT PRIMARY KEY,
  article_slug TEXT NOT NULL,
  visual_type TEXT NOT NULL,
  source_visible TEXT NOT NULL,
  caption_explains_claim TEXT NOT NULL,
  alt_text_present TEXT NOT NULL,
  visual_limitations_visible TEXT NOT NULL
);

CREATE TABLE editorial_review_queue (
  review_id TEXT PRIMARY KEY,
  record_id TEXT NOT NULL,
  issue_type TEXT NOT NULL,
  severity TEXT NOT NULL,
  review_note TEXT NOT NULL
);

.mode csv
.import --skip 1 data/evidence_architecture_inventory.csv evidence_architecture_inventory
.import --skip 1 data/claim_inventory.csv claim_inventory
.import --skip 1 data/source_inventory.csv source_inventory
.import --skip 1 data/visual_evidence_inventory.csv visual_evidence_inventory
.import --skip 1 data/editorial_review_queue.csv editorial_review_queue
