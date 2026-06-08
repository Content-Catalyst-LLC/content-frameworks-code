DROP TABLE IF EXISTS framework_quality;
DROP TABLE IF EXISTS metadata_inventory;
DROP TABLE IF EXISTS article_map;
DROP TABLE IF EXISTS internal_links;

CREATE TABLE framework_quality (
  framework_id TEXT PRIMARY KEY,
  framework_name TEXT NOT NULL,
  domain TEXT NOT NULL,
  primary_use TEXT NOT NULL,
  clarity INTEGER NOT NULL,
  coherence INTEGER NOT NULL,
  transferability INTEGER NOT NULL,
  adaptability INTEGER NOT NULL,
  explanatory_depth INTEGER NOT NULL,
  domain_fit INTEGER NOT NULL,
  audience_fit INTEGER NOT NULL,
  evidence_alignment INTEGER NOT NULL,
  ethical_safety INTEGER NOT NULL,
  governability INTEGER NOT NULL,
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

INSERT INTO framework_quality VALUES
('FQ001', 'Research Communication Framework', 'Research', 'Move from evidence to interpretation', 5, 5, 4, 4, 5, 5, 4, 5, 5, 4, 'low', 'Strong if uncertainty and limits remain visible'),
('FQ002', 'Educational Scaffolding', 'Education', 'Sequence learning from foundation to application', 5, 4, 4, 4, 4, 5, 5, 4, 4, 4, 'medium', 'Can become too rigid if learner differences are ignored'),
('FQ003', 'Message House', 'Strategic Communication', 'Align claims proof points and audience messages', 4, 4, 4, 3, 3, 4, 5, 4, 3, 3, 'medium', 'Can become talking points without evidence or agency'),
('FQ004', 'Article Map', 'Digital Publishing', 'Organize a knowledge series', 5, 5, 5, 4, 4, 5, 4, 4, 5, 5, 'low', 'Can become stale without governance'),
('FQ006', 'Persuasive Sequence Framework', 'Communication', 'Sequence attention interest desire and action', 4, 3, 4, 3, 2, 3, 4, 3, 2, 2, 'high', 'High manipulation risk if urgency replaces agency');

INSERT INTO article_map VALUES
(1, 'What Are Content Frameworks?', 'published', 'Foundations', 'what-are-content-frameworks', 'yes', 'yes'),
(2, 'Why Frameworks Matter in Research Education and Strategic Communication', 'published', 'Foundations', 'why-frameworks-matter-in-research-education-and-strategic-communication', 'yes', 'yes'),
(3, 'What Makes a Powerful Content Framework?', 'published', 'Foundations', 'what-makes-a-powerful-content-framework', 'yes', 'yes'),
(4, 'Framework Literacy and the Structure of Usable Knowledge', 'planned', 'Foundations', 'framework-literacy-and-the-structure-of-usable-knowledge', 'no', 'no');

INSERT INTO metadata_inventory VALUES
('what-are-content-frameworks', 'What Are Content Frameworks?', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'published'),
('why-frameworks-matter-in-research-education-and-strategic-communication', 'Why Frameworks Matter in Research Education and Strategic Communication', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'published'),
('what-makes-a-powerful-content-framework', 'What Makes a Powerful Content Framework', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'published');

INSERT INTO internal_links VALUES
('what-makes-a-powerful-content-framework', 'why-frameworks-matter-in-research-education-and-strategic-communication', 'previous_article', 'series navigation', 'high'),
('what-makes-a-powerful-content-framework', 'framework-literacy-and-the-structure-of-usable-knowledge', 'next_article', 'series navigation', 'high'),
('what-makes-a-powerful-content-framework', 'what-are-content-frameworks', 'foundation', 'connects quality criteria to definition', 'high'),
('what-makes-a-powerful-content-framework', 'content-audits-and-framework-governance', 'governance', 'connects quality to maintenance', 'high');
