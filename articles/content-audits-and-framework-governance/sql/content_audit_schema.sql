DROP TABLE IF EXISTS content_inventory;
DROP TABLE IF EXISTS internal_links;
DROP TABLE IF EXISTS taxonomy_categories;
DROP TABLE IF EXISTS evidence_register;
DROP TABLE IF EXISTS editorial_review_queue;

CREATE TABLE content_inventory (
  slug TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  status TEXT NOT NULL,
  cluster_name TEXT NOT NULL,
  article_type TEXT NOT NULL,
  excerpt TEXT NOT NULL,
  tags TEXT NOT NULL,
  github_url TEXT NOT NULL,
  image_alt TEXT NOT NULL,
  references_complete TEXT NOT NULL,
  last_reviewed TEXT NOT NULL,
  series_context TEXT NOT NULL,
  footer_navigation TEXT NOT NULL,
  repository_manifest TEXT NOT NULL,
  accessibility_notes TEXT NOT NULL,
  evidence_notes TEXT NOT NULL,
  limitations TEXT NOT NULL,
  governance_notes TEXT NOT NULL,
  last_reviewed_date TEXT,
  review_cycle_days INTEGER NOT NULL,
  duplicate_risk TEXT NOT NULL
);

CREATE TABLE internal_links (
  source_slug TEXT NOT NULL,
  target_slug TEXT NOT NULL,
  relationship_type TEXT NOT NULL,
  priority TEXT NOT NULL,
  status TEXT NOT NULL,
  last_reviewed TEXT NOT NULL
);

CREATE TABLE taxonomy_categories (
  category TEXT PRIMARY KEY,
  description TEXT NOT NULL,
  expected_role TEXT NOT NULL
);

CREATE TABLE evidence_register (
  slug TEXT NOT NULL,
  claim_type TEXT NOT NULL,
  source_type TEXT NOT NULL,
  authority_level TEXT NOT NULL,
  recency_risk TEXT NOT NULL,
  limitation_visible TEXT NOT NULL,
  review_status TEXT NOT NULL
);

CREATE TABLE editorial_review_queue (
  review_id TEXT PRIMARY KEY,
  slug TEXT NOT NULL,
  issue_type TEXT NOT NULL,
  severity TEXT NOT NULL,
  review_note TEXT NOT NULL
);

INSERT INTO content_inventory VALUES
('what-are-content-frameworks', 'What Are Content Frameworks?', 'published', 'Foundations', 'foundational', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', '2026-06-08', 730, 'low'),
('what-makes-a-powerful-content-framework', 'What Makes a Powerful Content Framework?', 'published', 'Foundations', 'foundational', 'yes', 'no', 'no', 'no', 'yes', 'no', 'yes', 'no', 'no', 'no', 'yes', 'yes', 'no', '2025-11-15', 730, 'medium'),
('internal-linking-as-framework-infrastructure', 'Internal Linking as Framework Infrastructure', 'published', 'Knowledge Architecture', 'method', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', '2026-06-08', 365, 'low'),
('content-audits-and-framework-governance', 'Content Audits and Framework Governance', 'published', 'Knowledge Architecture', 'governance', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', '2026-06-08', 180, 'low'),
('editorial-metadata-and-content-systems', 'Editorial Metadata and Content Systems', 'planned', 'Knowledge Architecture', 'technical', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', NULL, 180, 'medium');

INSERT INTO internal_links VALUES
('content-audits-and-framework-governance', 'internal-linking-as-framework-infrastructure', 'previous_article', 'high', 'active', '2026-06-08'),
('content-audits-and-framework-governance', 'editorial-metadata-and-content-systems', 'next_article', 'high', 'planned', '2026-06-08'),
('content-audits-and-framework-governance', 'pillar-pages-and-topic-clusters', 'knowledge_architecture', 'high', 'active', '2026-06-08'),
('internal-linking-as-framework-infrastructure', 'content-audits-and-framework-governance', 'next_article', 'high', 'active', '2026-06-08');

INSERT INTO taxonomy_categories VALUES
('Foundations', 'Definitions principles history and framework literacy', 'conceptual grounding'),
('Knowledge Architecture', 'Pillar pages topic clusters taxonomies metadata internal links audits and editorial systems', 'structural publishing logic'),
('Educational Research and Conceptual Frameworks', 'Learning scaffolds conceptual models evidence architecture and research communication', 'learning and evidence design');

INSERT INTO evidence_register VALUES
('content-audits-and-framework-governance', 'content_strategy', 'book', 'high', 'low', 'yes', 'ready'),
('content-audits-and-framework-governance', 'metadata_standards', 'official_standard', 'high', 'medium', 'yes', 'ready'),
('content-audits-and-framework-governance', 'accessibility', 'official_standard', 'high', 'medium', 'yes', 'ready');

INSERT INTO editorial_review_queue VALUES
('R001', 'what-makes-a-powerful-content-framework', 'metadata', 'medium', 'Repository link image metadata tags and footer navigation need completion'),
('R002', 'editorial-metadata-and-content-systems', 'status', 'medium', 'Planned next article is linked from published content and should be prioritized');
