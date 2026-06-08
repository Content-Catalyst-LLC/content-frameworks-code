DROP TABLE IF EXISTS pas_bab_message_inventory;
DROP TABLE IF EXISTS editorial_review_queue;

CREATE TABLE pas_bab_message_inventory (
  message_id TEXT PRIMARY KEY,
  asset_name TEXT NOT NULL,
  asset_type TEXT NOT NULL,
  framework_used TEXT NOT NULL,
  audience TEXT NOT NULL,
  problem_clear TEXT NOT NULL,
  before_state_specific TEXT NOT NULL,
  audience_context_present TEXT NOT NULL,
  stakes_visible TEXT NOT NULL,
  agitation_proportionate TEXT NOT NULL,
  consequence_supported TEXT NOT NULL,
  after_state_credible TEXT NOT NULL,
  transformation_bounded TEXT NOT NULL,
  benefit_claim_supported TEXT NOT NULL,
  solution_fit_clear TEXT NOT NULL,
  bridge_mechanism_visible TEXT NOT NULL,
  commitment_transparent TEXT NOT NULL,
  uses_invented_pain TEXT NOT NULL,
  uses_fear_escalation TEXT NOT NULL,
  uses_false_urgency TEXT NOT NULL,
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
.import --skip 1 data/pas_bab_message_inventory.csv pas_bab_message_inventory
.import --skip 1 data/editorial_review_queue.csv editorial_review_queue
