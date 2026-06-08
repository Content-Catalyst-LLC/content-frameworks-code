DROP TABLE IF EXISTS article_map;
DROP TABLE IF EXISTS framework_value;
DROP TABLE IF EXISTS metadata_inventory;
DROP TABLE IF EXISTS internal_links;

CREATE TABLE article_map (
  article_order INTEGER NOT NULL,
  title TEXT NOT NULL,
  status TEXT NOT NULL,
  cluster_name TEXT NOT NULL,
  slug TEXT PRIMARY KEY,
  series_context TEXT NOT NULL,
  footer_navigation TEXT NOT NULL,
  github_url TEXT NOT NULL
);

CREATE TABLE framework_value (
  framework_id TEXT PRIMARY KEY,
  framework_name TEXT NOT NULL,
  domain TEXT NOT NULL,
  primary_use TEXT NOT NULL,
  comprehension INTEGER NOT NULL,
  comparison INTEGER NOT NULL,
  retention INTEGER NOT NULL,
  action_score INTEGER NOT NULL,
  governance INTEGER NOT NULL,
  evidence_integrity INTEGER NOT NULL,
  audience_fit INTEGER NOT NULL,
  ethical_safety INTEGER NOT NULL,
  risk_severity TEXT NOT NULL,
  risk_if_misused TEXT NOT NULL
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

INSERT INTO article_map VALUES
(1, 'What Are Content Frameworks?', 'published', 'Foundations', 'what-are-content-frameworks', 'yes', 'yes', 'yes'),
(2, 'Why Frameworks Matter in Research Education and Strategic Communication', 'published', 'Foundations', 'why-frameworks-matter-in-research-education-and-strategic-communication', 'yes', 'yes', 'yes'),
(3, 'What Makes a Powerful Content Framework?', 'published', 'Foundations', 'what-makes-a-powerful-content-framework', 'yes', 'no', 'no'),
(4, 'Framework Literacy and the Structure of Usable Knowledge', 'planned', 'Foundations', 'framework-literacy-and-the-structure-of-usable-knowledge', 'no', 'no', 'no'),
(7, 'Pillar Pages and Topic Clusters', 'published', 'Knowledge Architecture', 'pillar-pages-and-topic-clusters', 'yes', 'yes', 'yes');

INSERT INTO framework_value VALUES
('FV001', 'Research Communication Framework', 'Research', 'Move from evidence to interpretation', 5, 4, 4, 3, 4, 5, 4, 5, 'medium', 'Findings may be overstated or uncertainty hidden'),
('FV002', 'Educational Scaffolding', 'Education', 'Sequence learning and reduce overload', 5, 3, 5, 4, 3, 4, 5, 4, 'medium', 'Learning pathways may become too rigid'),
('FV003', 'Message House', 'Strategic Communication', 'Align claims proof points and audience messages', 4, 4, 4, 5, 3, 4, 5, 3, 'medium', 'Talking points may replace evidence'),
('FV004', 'Article Map', 'Digital Publishing', 'Organize a knowledge series', 5, 5, 4, 4, 5, 4, 4, 5, 'low', 'Map may become outdated or overbuilt');

INSERT INTO metadata_inventory VALUES
('what-are-content-frameworks', 'What Are Content Frameworks?', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'published'),
('why-frameworks-matter-in-research-education-and-strategic-communication', 'Why Frameworks Matter in Research Education and Strategic Communication', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'published'),
('what-makes-a-powerful-content-framework', 'What Makes a Powerful Content Framework?', 'yes', 'no', 'no', 'no', 'yes', 'no', 'yes', 'no', 'published');

INSERT INTO internal_links VALUES
('why-frameworks-matter-in-research-education-and-strategic-communication', 'what-are-content-frameworks', 'previous_article', 'series navigation', 'high'),
('why-frameworks-matter-in-research-education-and-strategic-communication', 'what-makes-a-powerful-content-framework', 'next_article', 'series navigation', 'high'),
('why-frameworks-matter-in-research-education-and-strategic-communication', 'frameworks-for-research-communication', 'research_communication', 'connects framework value to research use', 'high'),
('why-frameworks-matter-in-research-education-and-strategic-communication', 'educational-scaffolding-and-the-design-of-learning-systems', 'education', 'connects framework value to learning design', 'high');
