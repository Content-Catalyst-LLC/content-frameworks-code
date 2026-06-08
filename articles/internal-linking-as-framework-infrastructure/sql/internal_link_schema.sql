DROP TABLE IF EXISTS article_inventory;
DROP TABLE IF EXISTS internal_links;
DROP TABLE IF EXISTS link_type_catalog;
DROP TABLE IF EXISTS editorial_review_queue;

CREATE TABLE article_inventory (
  slug TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  status TEXT NOT NULL,
  cluster_name TEXT NOT NULL,
  article_type TEXT NOT NULL,
  series_context TEXT NOT NULL,
  footer_navigation TEXT NOT NULL,
  github_url TEXT NOT NULL
);

CREATE TABLE internal_links (
  source_slug TEXT NOT NULL,
  target_slug TEXT NOT NULL,
  relationship_type TEXT NOT NULL,
  anchor_text TEXT NOT NULL,
  priority TEXT NOT NULL,
  status TEXT NOT NULL,
  last_reviewed TEXT NOT NULL
);

CREATE TABLE link_type_catalog (
  relationship_type TEXT PRIMARY KEY,
  description TEXT NOT NULL,
  governance_use TEXT NOT NULL
);

CREATE TABLE editorial_review_queue (
  review_id TEXT PRIMARY KEY,
  identifier TEXT NOT NULL,
  issue_type TEXT NOT NULL,
  severity TEXT NOT NULL,
  review_note TEXT NOT NULL
);

INSERT INTO article_inventory VALUES
('content-frameworks', 'Content Frameworks', 'published', 'Article Map', 'pillar_map', 'yes', 'yes', 'yes'),
('what-are-content-frameworks', 'What Are Content Frameworks?', 'published', 'Foundations', 'foundational', 'yes', 'yes', 'yes'),
('pillar-pages-and-topic-clusters', 'Pillar Pages and Topic Clusters', 'published', 'Knowledge Architecture', 'method', 'yes', 'yes', 'yes'),
('internal-linking-as-framework-infrastructure', 'Internal Linking as Framework Infrastructure', 'published', 'Knowledge Architecture', 'method', 'yes', 'yes', 'yes'),
('content-audits-and-framework-governance', 'Content Audits and Framework Governance', 'planned', 'Knowledge Architecture', 'governance', 'no', 'no', 'no');

INSERT INTO internal_links VALUES
('content-frameworks', 'internal-linking-as-framework-infrastructure', 'topic_cluster', 'Internal Linking as Framework Infrastructure', 'high', 'active', '2026-06-08'),
('internal-linking-as-framework-infrastructure', 'content-frameworks', 'series_navigation', 'Content Frameworks article map', 'high', 'active', '2026-06-08'),
('internal-linking-as-framework-infrastructure', 'pillar-pages-and-topic-clusters', 'prerequisite', 'pillar pages and topic clusters', 'high', 'active', '2026-06-08'),
('internal-linking-as-framework-infrastructure', 'content-audits-and-framework-governance', 'governance', 'content audits and framework governance', 'high', 'planned', '2026-06-08'),
('pillar-pages-and-topic-clusters', 'internal-linking-as-framework-infrastructure', 'method', 'internal linking as framework infrastructure', 'high', 'active', '2026-06-08');

INSERT INTO link_type_catalog VALUES
('series_navigation', 'Previous next or article-map relationship', 'Required for footer and sequence checks'),
('prerequisite', 'Points to background knowledge needed before the current article', 'Supports learning progression'),
('method', 'Points to a practical method or workflow', 'Supports applied use'),
('governance', 'Connects content to maintenance audit metadata or review', 'Supports editorial stewardship'),
('topic_cluster', 'Connects articles within a shared cluster', 'Supports cluster coherence');

INSERT INTO editorial_review_queue VALUES
('R001', 'what-are-content-frameworks', 'anchor_text', 'medium', 'Replace vague anchor text with descriptive destination label'),
('R002', 'content-audits-and-framework-governance', 'status', 'medium', 'Planned next article is linked from published article and should be prioritized');
