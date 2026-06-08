DROP TABLE IF EXISTS curriculum_pathway_inventory;
DROP TABLE IF EXISTS prerequisite_relationships;
DROP TABLE IF EXISTS learning_objectives;
DROP TABLE IF EXISTS editorial_review_queue;

CREATE TABLE curriculum_pathway_inventory (
  node_order INTEGER NOT NULL,
  node_slug TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  status TEXT NOT NULL,
  pathway_cluster TEXT NOT NULL,
  learning_stage TEXT NOT NULL,
  clear_headings TEXT NOT NULL,
  descriptive_links TEXT NOT NULL,
  alt_text TEXT NOT NULL,
  plain_language_summary TEXT NOT NULL,
  reflection_prompt TEXT NOT NULL,
  assessment_point TEXT NOT NULL,
  revision_prompt TEXT NOT NULL,
  application_example TEXT NOT NULL,
  transfer_task TEXT NOT NULL,
  repository_support TEXT NOT NULL
);

CREATE TABLE prerequisite_relationships (
  node_slug TEXT NOT NULL,
  prerequisite_slug TEXT NOT NULL,
  relationship_type TEXT NOT NULL,
  importance TEXT NOT NULL
);

CREATE TABLE learning_objectives (
  objective_id TEXT PRIMARY KEY,
  node_slug TEXT NOT NULL,
  objective_type TEXT NOT NULL,
  objective_text TEXT NOT NULL,
  required TEXT NOT NULL,
  support_material_present TEXT NOT NULL,
  assessment_present TEXT NOT NULL
);

CREATE TABLE editorial_review_queue (
  review_id TEXT PRIMARY KEY,
  record_id TEXT NOT NULL,
  issue_type TEXT NOT NULL,
  severity TEXT NOT NULL,
  review_note TEXT NOT NULL
);

.mode csv
.import --skip 1 data/curriculum_pathway_inventory.csv curriculum_pathway_inventory
.import --skip 1 data/prerequisite_relationships.csv prerequisite_relationships
.import --skip 1 data/learning_objectives.csv learning_objectives
.import --skip 1 data/editorial_review_queue.csv editorial_review_queue
