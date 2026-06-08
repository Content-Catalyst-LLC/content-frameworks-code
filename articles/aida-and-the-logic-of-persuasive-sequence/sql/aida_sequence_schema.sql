DROP TABLE IF EXISTS aida_message_inventory;
DROP TABLE IF EXISTS editorial_review_queue;

CREATE TABLE aida_message_inventory (
  message_id TEXT PRIMARY KEY,
  asset_name TEXT NOT NULL,
  asset_type TEXT NOT NULL,
  audience TEXT NOT NULL,
  headline_relevant TEXT NOT NULL,
  opening_problem_clear TEXT NOT NULL,
  attention_claim_supported TEXT NOT NULL,
  audience_relevance_visible TEXT NOT NULL,
  context_provided TEXT NOT NULL,
  evidence_or_example_present TEXT NOT NULL,
  value_proposition_clear TEXT NOT NULL,
  benefit_claim_supported TEXT NOT NULL,
  fit_and_limits_visible TEXT NOT NULL,
  cta_clear TEXT NOT NULL,
  cta_feasible TEXT NOT NULL,
  commitment_transparent TEXT NOT NULL,
  uses_false_urgency TEXT NOT NULL,
  uses_exaggerated_claims TEXT NOT NULL,
  uses_hidden_cost_or_condition TEXT NOT NULL,
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
.import --skip 1 data/aida_message_inventory.csv aida_message_inventory
.import --skip 1 data/editorial_review_queue.csv editorial_review_queue
