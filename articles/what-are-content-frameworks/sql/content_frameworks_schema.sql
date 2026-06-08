DROP TABLE IF EXISTS articles;
DROP TABLE IF EXISTS framework_library;
DROP TABLE IF EXISTS internal_links;

CREATE TABLE articles (
  article_order INTEGER NOT NULL,
  title TEXT NOT NULL,
  status TEXT NOT NULL,
  cluster_name TEXT NOT NULL,
  slug TEXT PRIMARY KEY
);

CREATE TABLE framework_library (
  framework_id TEXT PRIMARY KEY,
  framework_name TEXT NOT NULL,
  domain TEXT NOT NULL,
  primary_function TEXT NOT NULL,
  framework_type TEXT NOT NULL,
  risk_if_misused TEXT NOT NULL
);

CREATE TABLE internal_links (
  source_slug TEXT NOT NULL,
  target_slug TEXT NOT NULL,
  relationship_type TEXT NOT NULL,
  link_purpose TEXT NOT NULL
);

INSERT INTO articles VALUES
(1, 'What Are Content Frameworks?', 'published', 'Foundations', 'what-are-content-frameworks'),
(2, 'Why Frameworks Matter in Research Education and Strategic Communication', 'published', 'Foundations', 'why-frameworks-matter-in-research-education-and-strategic-communication'),
(3, 'What Makes a Powerful Content Framework?', 'published', 'Foundations', 'what-makes-a-powerful-content-framework'),
(4, 'Framework Literacy and the Structure of Usable Knowledge', 'planned', 'Foundations', 'framework-literacy-and-the-structure-of-usable-knowledge');

INSERT INTO framework_library VALUES
('CF001', 'Pillar Page and Topic Cluster', 'Digital Publishing', 'Organize related articles around a central explanatory hub', 'knowledge_architecture', 'Over-optimization for search instead of reader understanding'),
('CF002', 'Message House', 'Strategic Communication', 'Structure central claims supporting pillars and proof points', 'message_architecture', 'Repetition of talking points without evidence or audience nuance'),
('CF003', 'Educational Scaffolding', 'Education', 'Sequence knowledge from foundational to advanced understanding', 'learning_design', 'Overly rigid learning pathways that ignore learner diversity');

INSERT INTO internal_links VALUES
('what-are-content-frameworks', 'why-frameworks-matter-in-research-education-and-strategic-communication', 'next_article', 'series navigation'),
('what-are-content-frameworks', 'what-makes-a-powerful-content-framework', 'related_foundation', 'deepens quality criteria'),
('what-are-content-frameworks', 'pillar-pages-and-topic-clusters', 'knowledge_architecture', 'connects frameworks to article maps');
