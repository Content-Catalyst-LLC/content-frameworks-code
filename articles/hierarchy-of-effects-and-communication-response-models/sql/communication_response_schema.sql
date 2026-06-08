DROP TABLE IF EXISTS communication_response_inventory;
DROP TABLE IF EXISTS editorial_review_queue;

CREATE TABLE communication_response_inventory (
  asset_id TEXT PRIMARY KEY,
  asset_name TEXT NOT NULL,
  asset_type TEXT NOT NULL,
  primary_response_stage TEXT NOT NULL,
  audience TEXT NOT NULL,
  awareness_supported TEXT NOT NULL,
  awareness_evidence_present TEXT NOT NULL,
  knowledge_supported TEXT NOT NULL,
  knowledge_evidence_present TEXT NOT NULL,
  liking_supported TEXT NOT NULL,
  liking_evidence_present TEXT NOT NULL,
  preference_supported TEXT NOT NULL,
  preference_evidence_present TEXT NOT NULL,
  conviction_supported TEXT NOT NULL,
  conviction_evidence_present TEXT NOT NULL,
  action_supported TEXT NOT NULL,
  action_evidence_present TEXT NOT NULL,
  follow_through_supported TEXT NOT NULL,
  follow_through_evidence_present TEXT NOT NULL,
  audience_context_present TEXT NOT NULL,
  audience_readiness_defined TEXT NOT NULL,
  next_step_matches_stage TEXT NOT NULL,
  measurement_aligned TEXT NOT NULL,
  review_owner_present TEXT NOT NULL,
  last_review_date_present TEXT NOT NULL,
  revision_queue_checked TEXT NOT NULL,
  uses_false_urgency TEXT NOT NULL,
  overclaims_response TEXT NOT NULL,
  uses_pressure_cta TEXT NOT NULL,
  audience_agency_preserved TEXT NOT NULL
);

CREATE TABLE editorial_review_queue (
  review_id TEXT PRIMARY KEY,
  record_id TEXT NOT NULL,
  issue_type TEXT NOT NULL,
  severity TEXT NOT NULL,
  review_note TEXT NOT NULL
);

.mode csv
.import --skip 1 data/communication_response_inventory.csv communication_response_inventory
.import --skip 1 data/editorial_review_queue.csv editorial_review_queue
