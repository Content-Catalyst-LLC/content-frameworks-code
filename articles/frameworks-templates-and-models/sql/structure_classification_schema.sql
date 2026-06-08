DROP TABLE IF EXISTS content_structure_inventory;
DROP TABLE IF EXISTS article_map;
DROP TABLE IF EXISTS metadata_inventory;
DROP TABLE IF EXISTS internal_links;
DROP TABLE IF EXISTS structure_misuse_cases;

CREATE TABLE content_structure_inventory (
  structure_id TEXT PRIMARY KEY,
  structure_name TEXT NOT NULL,
  declared_type TEXT NOT NULL,
  observed_type TEXT NOT NULL,
  domain TEXT NOT NULL,
  purpose TEXT NOT NULL,
  organizes_reasoning INTEGER NOT NULL,
  defines_categories INTEGER NOT NULL,
  supports_interpretation INTEGER NOT NULL,
  standardizes_fields INTEGER NOT NULL,
  standardizes_format INTEGER NOT NULL,
  repeatable_output INTEGER NOT NULL,
  represents_relationships INTEGER NOT NULL,
  uses_assumptions INTEGER NOT NULL,
  explains_mechanism INTEGER NOT NULL,
  defines_steps INTEGER NOT NULL,
  supports_repeatable_process INTEGER NOT NULL,
  produces_decision_rules INTEGER NOT NULL,
  coordinates_handoffs INTEGER NOT NULL,
  tracks_status INTEGER NOT NULL,
  assigns_responsibility INTEGER NOT NULL,
  purpose_documented TEXT NOT NULL,
  use_conditions_documented TEXT NOT NULL,
  limitations_documented TEXT NOT NULL,
  evidence_alignment_reviewed TEXT NOT NULL,
  ethical_risk_reviewed TEXT NOT NULL,
  owner_assigned TEXT NOT NULL,
  review_cycle_defined TEXT NOT NULL,
  risk_severity TEXT NOT NULL,
  risk_note TEXT NOT NULL
);

CREATE TABLE article_map (
  article_order INTEGER NOT NULL,
  title TEXT NOT NULL,
  status TEXT NOT NULL,
  cluster_name TEXT NOT NULL,
  slug TEXT PRIMARY KEY,
  github_url TEXT NOT NULL,
  footer_navigation TEXT NOT NULL
);

CREATE TABLE metadata_inventory (
  slug TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  excerpt TEXT NOT NULL,
  tags TEXT NOT NULL,
  github_url TEXT NOT NULL,
  image_alt TEXT NOT NULL,
  references_complete TEXT NOT NULL,
  last_reviewed TEXT NOT NULL,
  series_context TEXT NOT NULL,
  footer_navigation TEXT NOT NULL,
  status TEXT NOT NULL
);

CREATE TABLE internal_links (
  source_slug TEXT NOT NULL,
  target_slug TEXT NOT NULL,
  relationship_type TEXT NOT NULL,
  link_purpose TEXT NOT NULL,
  priority TEXT NOT NULL
);

CREATE TABLE structure_misuse_cases (
  case_id TEXT PRIMARY KEY,
  structure_id TEXT NOT NULL,
  misuse_pattern TEXT NOT NULL,
  likely_consequence TEXT NOT NULL,
  recommended_review TEXT NOT NULL
);

INSERT INTO content_structure_inventory VALUES
('ST001', 'Content Framework Article Map', 'framework', 'framework', 'Knowledge Architecture', 'Organize article sequence and conceptual progression', 1,1,1,0,0,0,1,1,0,0,0,0,0,0,0,'yes','yes','yes','yes','yes','yes','yes','low','May create artificial boundaries if not reviewed'),
('ST002', 'Article Metadata Block', 'template', 'template', 'Editorial Systems', 'Standardize article metadata fields', 0,0,0,1,1,1,0,0,0,0,0,0,0,1,0,'yes','yes','yes','yes','yes','yes','yes','low','May become mechanical if excerpt quality is not reviewed'),
('ST003', 'Internal Link Graph', 'model', 'model', 'Knowledge Architecture', 'Represent relationships among articles', 0,0,1,0,0,0,1,1,1,0,0,0,0,0,0,'yes','yes','yes','yes','yes','yes','yes','low','Graph centrality may overvalue popular nodes'),
('ST004', 'Content Audit Sheet', 'template', 'method', 'Editorial Governance', 'Evaluate content quality and maintenance needs', 0,1,1,1,1,1,0,0,0,1,1,1,0,1,1,'yes','no','yes','yes','yes','yes','no','medium','Template is being used as a method without clear procedure'),
('ST010', 'AI Outline Prompt', 'template', 'framework', 'AI-Assisted Workflows', 'Generate candidate article structures', 1,1,1,1,1,1,0,1,0,1,1,0,0,0,0,'no','no','no','no','no','no','no','high','AI-generated structure may be treated as framework without review');

INSERT INTO article_map VALUES
(4, 'Framework Literacy and the Structure of Usable Knowledge', 'published', 'Foundations', 'framework-literacy-and-the-structure-of-usable-knowledge', 'yes', 'yes'),
(5, 'Frameworks Templates and Models', 'published', 'Foundations', 'frameworks-templates-and-models', 'yes', 'yes'),
(6, 'The History of Framework Thinking in Communication and Strategy', 'planned', 'Foundations', 'the-history-of-framework-thinking-in-communication-and-strategy', 'no', 'no');

INSERT INTO metadata_inventory VALUES
('frameworks-templates-and-models', 'Frameworks Templates and Models', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'published'),
('the-history-of-framework-thinking-in-communication-and-strategy', 'The History of Framework Thinking in Communication and Strategy', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'planned');

INSERT INTO internal_links VALUES
('frameworks-templates-and-models', 'framework-literacy-and-the-structure-of-usable-knowledge', 'previous_article', 'series navigation', 'high'),
('frameworks-templates-and-models', 'the-history-of-framework-thinking-in-communication-and-strategy', 'next_article', 'series navigation', 'high'),
('frameworks-templates-and-models', 'content-audits-and-framework-governance', 'methods', 'connects methods to content audit governance', 'high');

INSERT INTO structure_misuse_cases VALUES
('MC001', 'ST004', 'template mistaken for method', 'Audit results become inconsistent because procedure is undefined', 'Document audit method and decision rules'),
('MC004', 'ST010', 'AI outline mistaken for framework', 'Generated structure may be used without fit evidence or governance', 'Require framework review before publication');
