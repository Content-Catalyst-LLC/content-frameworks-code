DROP TABLE IF EXISTS research_communication_inventory;
DROP TABLE IF EXISTS claim_inventory;
DROP TABLE IF EXISTS source_inventory;
DROP TABLE IF EXISTS editorial_review_queue;

CREATE TABLE research_communication_inventory (
  article_slug TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  status TEXT NOT NULL,
  research_domain TEXT NOT NULL,
  audience TEXT NOT NULL,
  method_explained TEXT NOT NULL,
  limitations_visible TEXT NOT NULL,
  uncertainty_visible TEXT NOT NULL,
  assumptions_visible TEXT NOT NULL,
  confidence_language_present TEXT NOT NULL,
  audience_defined TEXT NOT NULL,
  prior_knowledge_supported TEXT NOT NULL,
  plain_language_summary TEXT NOT NULL,
  implications_bounded TEXT NOT NULL,
  visuals_accessible TEXT NOT NULL,
  tables_explained TEXT NOT NULL,
  alt_text_present TEXT NOT NULL
);

CREATE TABLE claim_inventory (
  claim_id TEXT PRIMARY KEY,
  article_slug TEXT NOT NULL,
  claim_type TEXT NOT NULL,
  claim_strength TEXT NOT NULL,
  claim_supported TEXT NOT NULL,
  source_id TEXT NOT NULL
);

CREATE TABLE source_inventory (
  source_id TEXT PRIMARY KEY,
  source_title TEXT NOT NULL,
  source_type TEXT NOT NULL,
  authority_level TEXT NOT NULL,
  review_status TEXT NOT NULL
);

CREATE TABLE editorial_review_queue (
  review_id TEXT PRIMARY KEY,
  record_id TEXT NOT NULL,
  issue_type TEXT NOT NULL,
  severity TEXT NOT NULL,
  review_note TEXT NOT NULL
);

.mode csv
.import --skip 1 data/research_communication_inventory.csv research_communication_inventory
.import --skip 1 data/claim_inventory.csv claim_inventory
.import --skip 1 data/source_inventory.csv source_inventory
.import --skip 1 data/editorial_review_queue.csv editorial_review_queue
