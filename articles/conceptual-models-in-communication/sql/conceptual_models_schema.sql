DROP TABLE IF EXISTS communication_model_inventory;
DROP TABLE IF EXISTS model_elements;
DROP TABLE IF EXISTS model_relationships;
DROP TABLE IF EXISTS editorial_review_queue;

CREATE TABLE communication_model_inventory (
  model_id TEXT PRIMARY KEY,
  model_name TEXT NOT NULL,
  model_type TEXT NOT NULL,
  status TEXT NOT NULL,
  primary_domain TEXT NOT NULL,
  audience_visible TEXT NOT NULL,
  context_visible TEXT NOT NULL,
  interpretation_visible TEXT NOT NULL,
  power_visible TEXT NOT NULL,
  feedback_visible TEXT NOT NULL,
  evidence_visible TEXT NOT NULL,
  limitations_visible TEXT NOT NULL,
  assumptions_visible TEXT NOT NULL,
  domain_fit TEXT NOT NULL,
  abstraction_risk TEXT NOT NULL
);

CREATE TABLE model_elements (
  model_id TEXT NOT NULL,
  element TEXT NOT NULL,
  present TEXT NOT NULL,
  importance TEXT NOT NULL
);

CREATE TABLE model_relationships (
  model_id TEXT NOT NULL,
  source_element TEXT NOT NULL,
  target_element TEXT NOT NULL,
  relationship_type TEXT NOT NULL,
  active TEXT NOT NULL
);

CREATE TABLE editorial_review_queue (
  review_id TEXT PRIMARY KEY,
  model_id TEXT NOT NULL,
  issue_type TEXT NOT NULL,
  severity TEXT NOT NULL,
  review_note TEXT NOT NULL
);

.mode csv
.import --skip 1 data/communication_model_inventory.csv communication_model_inventory
.import --skip 1 data/model_elements.csv model_elements
.import --skip 1 data/model_relationships.csv model_relationships
.import --skip 1 data/editorial_review_queue.csv editorial_review_queue
