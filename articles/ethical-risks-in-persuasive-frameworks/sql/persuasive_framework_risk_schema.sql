DROP TABLE IF EXISTS persuasive_framework_risk_inventory;
DROP TABLE IF EXISTS editorial_review_queue;

CREATE TABLE persuasive_framework_risk_inventory (
  asset_id TEXT PRIMARY KEY,
  asset_name TEXT NOT NULL,
  asset_type TEXT NOT NULL,
  framework_used TEXT NOT NULL,
  audience TEXT NOT NULL,
  requested_action TEXT NOT NULL,
  clear_claim TEXT NOT NULL,
  refusal_visible TEXT NOT NULL,
  decision_support_present TEXT NOT NULL,
  commitment_transparent TEXT NOT NULL,
  uses_false_urgency TEXT NOT NULL,
  uses_false_scarcity TEXT NOT NULL,
  uses_fear_escalation TEXT NOT NULL,
  uses_shame_pressure TEXT NOT NULL,
  total_persuasive_claims INTEGER NOT NULL,
  supported_persuasive_claims INTEGER NOT NULL,
  review_owner_present TEXT NOT NULL,
  evidence_reviewed TEXT NOT NULL,
  accessibility_reviewed TEXT NOT NULL,
  revision_queue_checked TEXT NOT NULL,
  plain_language_present TEXT NOT NULL,
  keyboard_path_clear TEXT NOT NULL,
  contrast_and_readability_checked TEXT NOT NULL,
  terms_accessible_before_action TEXT NOT NULL,
  high_stakes_context TEXT NOT NULL,
  financial_or_health_pressure TEXT NOT NULL,
  audience_dependency_present TEXT NOT NULL,
  time_pressure_present TEXT NOT NULL,
  hidden_terms TEXT NOT NULL,
  cancellation_friction TEXT NOT NULL,
  preselected_consent TEXT NOT NULL,
  disguised_ad TEXT NOT NULL
);

CREATE TABLE editorial_review_queue (
  review_id TEXT PRIMARY KEY,
  record_id TEXT NOT NULL,
  issue_type TEXT NOT NULL,
  severity TEXT NOT NULL,
  review_note TEXT NOT NULL
);

.mode csv
.import --skip 1 data/persuasive_framework_risk_inventory.csv persuasive_framework_risk_inventory
.import --skip 1 data/editorial_review_queue.csv editorial_review_queue
