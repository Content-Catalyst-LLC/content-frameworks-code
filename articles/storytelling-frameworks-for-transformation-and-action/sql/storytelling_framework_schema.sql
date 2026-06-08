DROP TABLE IF EXISTS storytelling_framework_inventory;
DROP TABLE IF EXISTS editorial_review_queue;

CREATE TABLE storytelling_framework_inventory (
  asset_id TEXT PRIMARY KEY,
  asset_name TEXT NOT NULL,
  asset_type TEXT NOT NULL,
  story_purpose TEXT NOT NULL,
  audience TEXT NOT NULL,
  context_present TEXT NOT NULL,
  context_supported TEXT NOT NULL,
  actors_present TEXT NOT NULL,
  actors_supported TEXT NOT NULL,
  tension_present TEXT NOT NULL,
  tension_supported TEXT NOT NULL,
  sequence_present TEXT NOT NULL,
  sequence_supported TEXT NOT NULL,
  transformation_present TEXT NOT NULL,
  transformation_supported TEXT NOT NULL,
  action_present TEXT NOT NULL,
  action_supported TEXT NOT NULL,
  affected_people_have_agency TEXT NOT NULL,
  institutional_responsibility_visible TEXT NOT NULL,
  audience_agency_preserved TEXT NOT NULL,
  transformation_bounded TEXT NOT NULL,
  mechanism_visible TEXT NOT NULL,
  limitations_present TEXT NOT NULL,
  review_owner_present TEXT NOT NULL,
  consent_or_source_context_present TEXT NOT NULL,
  last_review_date_present TEXT NOT NULL,
  revision_queue_checked TEXT NOT NULL,
  uses_savior_framing TEXT NOT NULL,
  overdramatizes_tension TEXT NOT NULL,
  uses_unsupported_anecdote TEXT NOT NULL,
  uses_pressure_cta TEXT NOT NULL
);

CREATE TABLE editorial_review_queue (
  review_id TEXT PRIMARY KEY,
  record_id TEXT NOT NULL,
  issue_type TEXT NOT NULL,
  severity TEXT NOT NULL,
  review_note TEXT NOT NULL
);

.mode csv
.import --skip 1 data/storytelling_framework_inventory.csv storytelling_framework_inventory
.import --skip 1 data/editorial_review_queue.csv editorial_review_queue
