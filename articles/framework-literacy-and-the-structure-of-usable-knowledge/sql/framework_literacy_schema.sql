DROP TABLE IF EXISTS framework_literacy;
DROP TABLE IF EXISTS article_map;
DROP TABLE IF EXISTS metadata_inventory;
DROP TABLE IF EXISTS internal_links;
DROP TABLE IF EXISTS framework_use_conditions;

CREATE TABLE framework_literacy (
  framework_id TEXT PRIMARY KEY,
  framework_name TEXT NOT NULL,
  domain TEXT NOT NULL,
  primary_use TEXT NOT NULL,
  assumption_awareness INTEGER NOT NULL,
  blind_spot_recognition INTEGER NOT NULL,
  boundary_clarity INTEGER NOT NULL,
  use_condition_clarity INTEGER NOT NULL,
  evidence_alignment INTEGER NOT NULL,
  ethical_safety INTEGER NOT NULL,
  audience_fit INTEGER NOT NULL,
  domain_fit INTEGER NOT NULL,
  adaptability INTEGER NOT NULL,
  governance_readiness INTEGER NOT NULL,
  risk_severity TEXT NOT NULL,
  primary_blind_spot TEXT NOT NULL
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

CREATE TABLE framework_use_conditions (
  condition_id TEXT PRIMARY KEY,
  framework_id TEXT NOT NULL,
  use_condition TEXT NOT NULL,
  avoid_when TEXT NOT NULL,
  review_owner TEXT NOT NULL
);

INSERT INTO framework_literacy VALUES
('FL001', 'Research Communication Framework', 'Research', 'Move from evidence to interpretation', 5, 5, 5, 5, 5, 5, 4, 5, 4, 5, 'low', 'May underrepresent lived experience if evidence hierarchy is too narrow'),
('FL003', 'Message House', 'Strategic Communication', 'Align claims proof points and audience messages', 4, 3, 4, 3, 4, 3, 5, 4, 3, 3, 'medium', 'May hide uncertainty dissent or audience agency'),
('FL004', 'Article Map', 'Digital Publishing', 'Organize a knowledge series', 5, 4, 5, 5, 4, 5, 4, 5, 5, 5, 'low', 'May create artificial boundaries between related domains'),
('FL006', 'Persuasive Sequence Framework', 'Communication', 'Sequence attention interest desire and action', 3, 2, 3, 2, 3, 2, 4, 3, 3, 2, 'high', 'May manipulate urgency and reduce audience agency'),
('FL009', 'Taxonomy Design Framework', 'Knowledge Architecture', 'Define categories boundaries and semantic relationships', 5, 4, 5, 5, 4, 5, 4, 5, 5, 5, 'low', 'May harden provisional categories into fixed boundaries');

INSERT INTO article_map VALUES
(1, 'What Are Content Frameworks?', 'published', 'Foundations', 'what-are-content-frameworks', 'yes', 'yes'),
(2, 'Why Frameworks Matter in Research Education and Strategic Communication', 'published', 'Foundations', 'why-frameworks-matter-in-research-education-and-strategic-communication', 'yes', 'yes'),
(3, 'What Makes a Powerful Content Framework?', 'published', 'Foundations', 'what-makes-a-powerful-content-framework', 'yes', 'yes'),
(4, 'Framework Literacy and the Structure of Usable Knowledge', 'published', 'Foundations', 'framework-literacy-and-the-structure-of-usable-knowledge', 'yes', 'yes'),
(5, 'Frameworks Templates and Models', 'planned', 'Foundations', 'frameworks-templates-and-models', 'no', 'no');

INSERT INTO metadata_inventory VALUES
('framework-literacy-and-the-structure-of-usable-knowledge', 'Framework Literacy and the Structure of Usable Knowledge', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'published'),
('frameworks-templates-and-models', 'Frameworks Templates and Models', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'planned');

INSERT INTO internal_links VALUES
('framework-literacy-and-the-structure-of-usable-knowledge', 'what-makes-a-powerful-content-framework', 'previous_article', 'series navigation', 'high'),
('framework-literacy-and-the-structure-of-usable-knowledge', 'frameworks-templates-and-models', 'next_article', 'series navigation', 'high'),
('framework-literacy-and-the-structure-of-usable-knowledge', 'taxonomy-design-for-content-frameworks', 'boundary_clarity', 'connects literacy to taxonomy boundaries', 'high'),
('framework-literacy-and-the-structure-of-usable-knowledge', 'content-audits-and-framework-governance', 'governance', 'connects literacy to review workflows', 'high');

INSERT INTO framework_use_conditions VALUES
('UC001', 'FL001', 'Use when explaining evidence interpretation uncertainty and limits', 'Avoid when source evidence is incomplete or contested beyond article scope', 'Research editor'),
('UC003', 'FL006', 'Use only with explicit agency and context safeguards', 'Avoid when fear urgency or scarcity would bypass judgment', 'Ethics reviewer'),
('UC005', 'FL009', 'Use when categories are documented and revisable', 'Avoid when taxonomy will freeze contested or evolving concepts', 'Knowledge architect');
