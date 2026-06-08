DROP TABLE IF EXISTS historical_framework_records;
DROP TABLE IF EXISTS framework_influence_edges;
DROP TABLE IF EXISTS article_map;
DROP TABLE IF EXISTS metadata_inventory;
DROP TABLE IF EXISTS internal_links;

CREATE TABLE historical_framework_records (
  framework_id TEXT PRIMARY KEY,
  framework_name TEXT NOT NULL,
  period TEXT NOT NULL,
  lineage TEXT NOT NULL,
  domain TEXT NOT NULL,
  structure_type TEXT NOT NULL,
  primary_function TEXT NOT NULL,
  origin_summary TEXT NOT NULL,
  transferred_across_domains TEXT NOT NULL,
  purpose_documented TEXT NOT NULL,
  use_conditions_documented TEXT NOT NULL,
  limitations_documented TEXT NOT NULL,
  owner_assigned TEXT NOT NULL,
  review_cycle_defined TEXT NOT NULL,
  risk_severity TEXT NOT NULL,
  risk_note TEXT NOT NULL
);

CREATE TABLE framework_influence_edges (
  source_framework_id TEXT NOT NULL,
  target_framework_id TEXT NOT NULL,
  influence_type TEXT NOT NULL,
  description TEXT NOT NULL,
  strength TEXT NOT NULL
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

INSERT INTO historical_framework_records VALUES
('HF001', 'Classical Rhetorical Arrangement', 'ancient', 'rhetorical', 'Communication', 'framework', 'Structure persuasive speech', 'Organized speech into purposeful stages', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'medium', 'Can support public reasoning or manipulation depending on use'),
('HF003', 'Classification and Taxonomy', 'ancient_to_modern', 'logical_classificatory', 'Knowledge Organization', 'framework', 'Group and retrieve knowledge', 'Long tradition of ordering knowledge into categories', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'low', 'Can harden provisional categories into fixed boundaries'),
('HF006', 'SWOT Analysis', 'modern', 'strategic_managerial', 'Strategy', 'framework', 'Organize internal and external factors', 'Management analysis structure for planning', 'yes', 'yes', 'no', 'yes', 'yes', 'no', 'medium', 'Can become generic without evidence and prioritization'),
('HF008', 'AIDA', 'modern', 'advertising_persuasive_sequence', 'Advertising', 'framework', 'Sequence audience response', 'Advertising sequence from attention to action', 'yes', 'yes', 'no', 'yes', 'yes', 'no', 'high', 'Can encourage manipulation when agency and context are ignored'),
('HF009', 'Information Architecture', 'late_modern', 'information_architecture', 'Digital Publishing', 'framework', 'Organize digital knowledge environments', 'Practice of structuring labels navigation and search', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'low', 'Can overfit to navigation while missing conceptual depth'),
('HF013', 'AI Generated Article Map', 'active', 'ai_assisted', 'AI-Assisted Workflows', 'workflow', 'Generate candidate content structures', 'AI-assisted generation of outlines taxonomies and article maps', 'yes', 'no', 'no', 'no', 'no', 'no', 'high', 'Can scale generic structures without evidence or governance');

INSERT INTO framework_influence_edges VALUES
('HF001', 'HF008', 'sequence_influence', 'Rhetorical arrangement influenced persuasive sequence structures', 'high'),
('HF003', 'HF009', 'classification_influence', 'Taxonomy traditions influenced information architecture', 'high'),
('HF009', 'HF013', 'digital_architecture_influence', 'Information architecture influenced AI-assisted article-map generation', 'medium');

INSERT INTO article_map VALUES
(5, 'Frameworks Templates and Models', 'published', 'Foundations', 'frameworks-templates-and-models', 'yes', 'yes'),
(6, 'The History of Framework Thinking in Communication and Strategy', 'published', 'Foundations', 'the-history-of-framework-thinking-in-communication-and-strategy', 'yes', 'yes'),
(7, 'Pillar Pages and Topic Clusters', 'published', 'Knowledge Architecture', 'pillar-pages-and-topic-clusters', 'yes', 'yes');

INSERT INTO metadata_inventory VALUES
('the-history-of-framework-thinking-in-communication-and-strategy', 'The History of Framework Thinking in Communication and Strategy', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'published');

INSERT INTO internal_links VALUES
('the-history-of-framework-thinking-in-communication-and-strategy', 'frameworks-templates-and-models', 'previous_article', 'series navigation', 'high'),
('the-history-of-framework-thinking-in-communication-and-strategy', 'pillar-pages-and-topic-clusters', 'next_article', 'series navigation', 'high'),
('the-history-of-framework-thinking-in-communication-and-strategy', 'framework-governance-and-editorial-maintenance', 'governance', 'connects history to framework maintenance', 'high');
