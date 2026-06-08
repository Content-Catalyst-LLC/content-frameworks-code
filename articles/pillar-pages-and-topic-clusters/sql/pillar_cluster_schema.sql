DROP TABLE IF EXISTS pillar_cluster_articles;
DROP TABLE IF EXISTS internal_links;
DROP TABLE IF EXISTS metadata_inventory;
DROP TABLE IF EXISTS taxonomy_categories;

CREATE TABLE pillar_cluster_articles (
  article_id TEXT PRIMARY KEY,
  slug TEXT NOT NULL,
  title TEXT NOT NULL,
  cluster_name TEXT NOT NULL,
  status TEXT NOT NULL,
  article_role TEXT NOT NULL,
  priority TEXT NOT NULL,
  review_owner TEXT NOT NULL
);

CREATE TABLE internal_links (
  source_slug TEXT NOT NULL,
  target_slug TEXT NOT NULL,
  relationship_type TEXT NOT NULL,
  link_purpose TEXT NOT NULL,
  priority TEXT NOT NULL
);

CREATE TABLE metadata_inventory (
  slug TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  status TEXT NOT NULL,
  excerpt TEXT NOT NULL,
  tags TEXT NOT NULL,
  github_url TEXT NOT NULL,
  image_alt TEXT NOT NULL,
  references_complete TEXT NOT NULL,
  last_reviewed TEXT NOT NULL,
  series_context TEXT NOT NULL,
  footer_navigation TEXT NOT NULL
);

CREATE TABLE taxonomy_categories (
  category TEXT PRIMARY KEY,
  description TEXT NOT NULL,
  expected_role TEXT NOT NULL
);

INSERT INTO pillar_cluster_articles VALUES
('PC001', 'pillar-pages-and-topic-clusters', 'Pillar Pages and Topic Clusters', 'Knowledge Architecture', 'published', 'pillar', 'high', 'Knowledge architect'),
('PC002', 'narrative-pathways-and-knowledge-architecture', 'Narrative Pathways and Knowledge Architecture', 'Knowledge Architecture', 'published', 'method', 'high', 'Knowledge architect'),
('PC003', 'frameworks-for-digital-knowledge-systems', 'Frameworks for Digital Knowledge Systems', 'Knowledge Architecture', 'published', 'technical', 'high', 'Knowledge architect'),
('PC004', 'taxonomy-design-for-content-frameworks', 'Taxonomy Design for Content Frameworks', 'Knowledge Architecture', 'planned', 'method', 'high', 'Knowledge architect'),
('PC005', 'internal-linking-as-framework-infrastructure', 'Internal Linking as Framework Infrastructure', 'Knowledge Architecture', 'planned', 'technical', 'high', 'Knowledge architect'),
('PC006', 'content-audits-and-framework-governance', 'Content Audits and Framework Governance', 'Knowledge Architecture', 'planned', 'governance', 'high', 'Editorial governance lead'),
('PC007', 'editorial-metadata-and-content-systems', 'Editorial Metadata and Content Systems', 'Knowledge Architecture', 'planned', 'technical', 'high', 'Editorial systems lead'),
('PC011', 'the-history-of-framework-thinking-in-communication-and-strategy', 'The History of Framework Thinking in Communication and Strategy', 'Foundations', 'published', 'history', 'medium', 'Series editor');

INSERT INTO internal_links VALUES
('pillar-pages-and-topic-clusters', 'narrative-pathways-and-knowledge-architecture', 'pillar_to_cluster', 'send readers from pillar to narrative pathways', 'high'),
('pillar-pages-and-topic-clusters', 'frameworks-for-digital-knowledge-systems', 'pillar_to_cluster', 'send readers from pillar to digital knowledge systems', 'high'),
('pillar-pages-and-topic-clusters', 'taxonomy-design-for-content-frameworks', 'pillar_to_cluster', 'send readers from pillar to taxonomy design', 'high'),
('pillar-pages-and-topic-clusters', 'internal-linking-as-framework-infrastructure', 'pillar_to_cluster', 'send readers from pillar to internal linking', 'high'),
('pillar-pages-and-topic-clusters', 'content-audits-and-framework-governance', 'pillar_to_cluster', 'send readers from pillar to content audits', 'high'),
('pillar-pages-and-topic-clusters', 'editorial-metadata-and-content-systems', 'pillar_to_cluster', 'send readers from pillar to metadata systems', 'high'),
('narrative-pathways-and-knowledge-architecture', 'pillar-pages-and-topic-clusters', 'cluster_to_pillar', 'restore reader orientation', 'high'),
('frameworks-for-digital-knowledge-systems', 'pillar-pages-and-topic-clusters', 'cluster_to_pillar', 'restore reader orientation', 'high'),
('pillar-pages-and-topic-clusters', 'the-history-of-framework-thinking-in-communication-and-strategy', 'previous_article', 'series navigation', 'high');

INSERT INTO metadata_inventory VALUES
('pillar-pages-and-topic-clusters', 'Pillar Pages and Topic Clusters', 'published', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes'),
('narrative-pathways-and-knowledge-architecture', 'Narrative Pathways and Knowledge Architecture', 'published', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes'),
('frameworks-for-digital-knowledge-systems', 'Frameworks for Digital Knowledge Systems', 'published', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes'),
('taxonomy-design-for-content-frameworks', 'Taxonomy Design for Content Frameworks', 'planned', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no');

INSERT INTO taxonomy_categories VALUES
('Foundations', 'Definitions principles literacy distinctions and history', 'conceptual grounding'),
('Knowledge Architecture', 'Pillar pages topic clusters narrative pathways digital systems taxonomies metadata and links', 'structural publishing logic'),
('Framework Composition Scaling and Editorial Governance', 'Composition scaling limits maintenance drift and AI-assisted design', 'maintenance and critique');
