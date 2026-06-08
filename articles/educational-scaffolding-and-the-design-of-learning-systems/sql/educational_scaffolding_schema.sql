DROP TABLE IF EXISTS learning_path_inventory;
DROP TABLE IF EXISTS prerequisite_relationships;
DROP TABLE IF EXISTS scaffold_feature_catalog;
DROP TABLE IF EXISTS editorial_review_queue;

CREATE TABLE learning_path_inventory (
  article_order INTEGER NOT NULL,
  slug TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  status TEXT NOT NULL,
  concept_cluster TEXT NOT NULL,
  learning_stage TEXT NOT NULL,
  orientation_support TEXT NOT NULL,
  worked_examples TEXT NOT NULL,
  feedback_prompts TEXT NOT NULL,
  transfer_support TEXT NOT NULL,
  cognitive_load_risk TEXT NOT NULL,
  alt_text TEXT NOT NULL,
  clear_headings TEXT NOT NULL,
  descriptive_links TEXT NOT NULL,
  summary_support TEXT NOT NULL
);

CREATE TABLE prerequisite_relationships (
  article_slug TEXT NOT NULL,
  prerequisite_slug TEXT NOT NULL,
  relationship_type TEXT NOT NULL,
  importance TEXT NOT NULL
);

CREATE TABLE scaffold_feature_catalog (
  feature TEXT PRIMARY KEY,
  description TEXT NOT NULL,
  governance_use TEXT NOT NULL
);

CREATE TABLE editorial_review_queue (
  review_id TEXT PRIMARY KEY,
  slug TEXT NOT NULL,
  issue_type TEXT NOT NULL,
  severity TEXT NOT NULL,
  review_note TEXT NOT NULL
);

INSERT INTO learning_path_inventory VALUES
(1, 'what-are-content-frameworks', 'What Are Content Frameworks?', 'published', 'Foundations', 'orientation', 'yes', 'yes', 'yes', 'yes', 'low', 'yes', 'yes', 'yes', 'yes'),
(2, 'why-frameworks-matter-in-research-education-and-strategic-communication', 'Why Frameworks Matter in Research Education and Strategic Communication', 'published', 'Foundations', 'foundation', 'yes', 'yes', 'yes', 'yes', 'low', 'yes', 'yes', 'yes', 'yes'),
(13, 'editorial-metadata-and-content-systems', 'Editorial Metadata and Content Systems', 'published', 'Knowledge Architecture', 'method', 'yes', 'yes', 'yes', 'yes', 'medium', 'yes', 'yes', 'yes', 'yes'),
(14, 'educational-scaffolding-and-the-design-of-learning-systems', 'Educational Scaffolding and the Design of Learning Systems', 'published', 'Educational Research and Conceptual Frameworks', 'method', 'yes', 'yes', 'yes', 'yes', 'low', 'yes', 'yes', 'yes', 'yes'),
(15, 'conceptual-models-in-communication', 'Conceptual Models in Communication', 'published', 'Educational Research and Conceptual Frameworks', 'foundation', 'yes', 'yes', 'yes', 'yes', 'medium', 'yes', 'yes', 'yes', 'yes'),
(17, 'curriculum-pathways-and-framework-design', 'Curriculum Pathways and Framework Design', 'planned', 'Educational Research and Conceptual Frameworks', 'transfer', 'yes', 'no', 'no', 'yes', 'medium', 'no', 'yes', 'yes', 'no');

INSERT INTO prerequisite_relationships VALUES
('why-frameworks-matter-in-research-education-and-strategic-communication', 'what-are-content-frameworks', 'foundation', 'high'),
('editorial-metadata-and-content-systems', 'content-audits-and-framework-governance', 'prerequisite', 'medium'),
('educational-scaffolding-and-the-design-of-learning-systems', 'what-are-content-frameworks', 'foundation', 'high'),
('educational-scaffolding-and-the-design-of-learning-systems', 'editorial-metadata-and-content-systems', 'system_support', 'medium'),
('conceptual-models-in-communication', 'educational-scaffolding-and-the-design-of-learning-systems', 'prerequisite', 'medium'),
('curriculum-pathways-and-framework-design', 'educational-scaffolding-and-the-design-of-learning-systems', 'prerequisite', 'high');

INSERT INTO scaffold_feature_catalog VALUES
('orientation_support', 'Helps learners understand where they are in the knowledge system', 'Required for article maps pillar pages and learning pathways'),
('prerequisite_links', 'Connects advanced articles to needed prior concepts', 'Required for complex topics'),
('worked_examples', 'Shows how a concept or method works step by step', 'Supports practice and transfer'),
('feedback_prompts', 'Helps learners check understanding', 'Supports learning loops and revision'),
('transfer_support', 'Shows how a framework can be adapted responsibly', 'Supports independent use'),
('cognitive_load_review', 'Flags articles that may overwhelm readers', 'Supports editorial revision'),
('accessibility_support', 'Ensures headings alt text links and summaries support diverse learners', 'Supports inclusive learning design');

INSERT INTO editorial_review_queue VALUES
('R001', 'frameworks-for-digital-knowledge-systems', 'cognitive_load', 'medium', 'Technical article has high cognitive-load risk and should receive more summaries or guided examples'),
('R002', 'curriculum-pathways-and-framework-design', 'coverage', 'medium', 'Planned transfer article should be completed to strengthen educational framework cluster'),
('R003', 'educational-scaffolding-and-the-design-of-learning-systems', 'publication', 'low', 'Confirm final WordPress attachment ID and repository URL after publication');
