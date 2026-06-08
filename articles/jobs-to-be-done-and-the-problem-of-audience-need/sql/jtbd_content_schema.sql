DROP TABLE IF EXISTS jtbd_content_inventory;
DROP TABLE IF EXISTS editorial_review_queue;

CREATE TABLE jtbd_content_inventory (
  asset_id TEXT PRIMARY KEY,
  asset_name TEXT NOT NULL,
  asset_type TEXT NOT NULL,
  primary_job TEXT NOT NULL,
  audience TEXT NOT NULL,
  situation_defined TEXT NOT NULL,
  motivation_defined TEXT NOT NULL,
  desired_outcome_defined TEXT NOT NULL,
  constraint_defined TEXT NOT NULL,
  functional_job_supported TEXT NOT NULL,
  emotional_job_supported TEXT NOT NULL,
  social_job_supported TEXT NOT NULL,
  strategic_job_supported TEXT NOT NULL,
  learning_job_supported TEXT NOT NULL,
  format_matches_job TEXT NOT NULL,
  examples_match_job TEXT NOT NULL,
  sections_match_job TEXT NOT NULL,
  next_step_matches_job TEXT NOT NULL,
  total_job_assumptions INTEGER NOT NULL,
  supported_job_assumptions INTEGER NOT NULL,
  success_criteria_defined TEXT NOT NULL,
  measurement_matches_job TEXT NOT NULL,
  content_supports_progress TEXT NOT NULL,
  audience_choice_preserved TEXT NOT NULL,
  alternatives_visible TEXT NOT NULL,
  claims_bounded TEXT NOT NULL,
  review_owner_present TEXT NOT NULL,
  last_review_date_present TEXT NOT NULL,
  revision_queue_checked TEXT NOT NULL,
  job_assumption_reviewed TEXT NOT NULL
);

CREATE TABLE editorial_review_queue (
  review_id TEXT PRIMARY KEY,
  record_id TEXT NOT NULL,
  issue_type TEXT NOT NULL,
  severity TEXT NOT NULL,
  review_note TEXT NOT NULL
);

.mode csv
.import --skip 1 data/jtbd_content_inventory.csv jtbd_content_inventory
.import --skip 1 data/editorial_review_queue.csv editorial_review_queue
