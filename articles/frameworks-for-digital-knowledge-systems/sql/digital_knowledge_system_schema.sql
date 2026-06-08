DROP TABLE IF EXISTS content_inventory;
DROP TABLE IF EXISTS metadata_inventory;
DROP TABLE IF EXISTS taxonomy_categories;
DROP TABLE IF EXISTS internal_links;
DROP TABLE IF EXISTS repository_inventory;

CREATE TABLE content_inventory (
  content_id TEXT PRIMARY KEY,
  slug TEXT NOT NULL,
  title TEXT NOT NULL,
  cluster_name TEXT NOT NULL,
  status TEXT NOT NULL,
  content_type TEXT NOT NULL,
  article_role TEXT NOT NULL,
  review_current TEXT NOT NULL,
  review_owner TEXT NOT NULL,
  public_use_level TEXT NOT NULL
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
  expected_role TEXT NOT NULL,
  governance_owner TEXT NOT NULL
);

CREATE TABLE internal_links (
  source_slug TEXT NOT NULL,
  target_slug TEXT NOT NULL,
  relationship_type TEXT NOT NULL,
  link_purpose TEXT NOT NULL,
  priority TEXT NOT NULL
);

CREATE TABLE repository_inventory (
  slug TEXT PRIMARY KEY,
  repository_url TEXT NOT NULL,
  repository_exists TEXT NOT NULL,
  readme_exists TEXT NOT NULL,
  python_workflow TEXT NOT NULL,
  r_workflow TEXT NOT NULL,
  sql_schema TEXT NOT NULL,
  workflow_outputs_exist TEXT NOT NULL,
  governance_docs TEXT NOT NULL
);

INSERT INTO content_inventory VALUES
('DKS002', 'pillar-pages-and-topic-clusters', 'Pillar Pages and Topic Clusters', 'Knowledge Architecture', 'published', 'article', 'pillar', 'yes', 'Knowledge architect', 'public'),
('DKS003', 'narrative-pathways-and-knowledge-architecture', 'Narrative Pathways and Knowledge Architecture', 'Knowledge Architecture', 'published', 'article', 'method', 'yes', 'Knowledge architect', 'public'),
('DKS004', 'frameworks-for-digital-knowledge-systems', 'Frameworks for Digital Knowledge Systems', 'Knowledge Architecture', 'published', 'article', 'technical', 'yes', 'Knowledge architect', 'public'),
('DKS005', 'taxonomy-design-for-content-frameworks', 'Taxonomy Design for Content Frameworks', 'Knowledge Architecture', 'planned', 'article', 'method', 'no', 'Knowledge architect', 'public'),
('DKS006', 'internal-linking-as-framework-infrastructure', 'Internal Linking as Framework Infrastructure', 'Knowledge Architecture', 'planned', 'article', 'technical', 'no', 'Knowledge architect', 'public'),
('DKS007', 'content-audits-and-framework-governance', 'Content Audits and Framework Governance', 'Knowledge Architecture', 'planned', 'article', 'governance', 'no', 'Editorial governance lead', 'editorial');

INSERT INTO metadata_inventory VALUES
('pillar-pages-and-topic-clusters', 'Pillar Pages and Topic Clusters', 'published', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes'),
('narrative-pathways-and-knowledge-architecture', 'Narrative Pathways and Knowledge Architecture', 'published', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes'),
('frameworks-for-digital-knowledge-systems', 'Frameworks for Digital Knowledge Systems', 'published', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes'),
('taxonomy-design-for-content-frameworks', 'Taxonomy Design for Content Frameworks', 'planned', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no');

INSERT INTO taxonomy_categories VALUES
('Foundations', 'Definitions principles literacy distinctions and history', 'conceptual grounding', 'Series editor'),
('Knowledge Architecture', 'Pillar pages topic clusters narrative pathways digital systems taxonomies metadata and links', 'structural publishing logic', 'Knowledge architect'),
('Framework Composition Scaling and Editorial Governance', 'Composition scaling limits maintenance drift and AI-assisted design', 'maintenance and critique', 'Editorial governance lead');

INSERT INTO internal_links VALUES
('frameworks-for-digital-knowledge-systems', 'narrative-pathways-and-knowledge-architecture', 'previous_article', 'series navigation', 'high'),
('frameworks-for-digital-knowledge-systems', 'taxonomy-design-for-content-frameworks', 'next_article', 'series navigation', 'high'),
('frameworks-for-digital-knowledge-systems', 'pillar-pages-and-topic-clusters', 'prerequisite', 'connects digital systems to pillar-cluster architecture', 'high'),
('frameworks-for-digital-knowledge-systems', 'editorial-metadata-and-content-systems', 'metadata_bridge', 'connects digital systems to metadata systems', 'high'),
('frameworks-for-digital-knowledge-systems', 'internal-linking-as-framework-infrastructure', 'technical_bridge', 'connects system architecture to internal-link infrastructure', 'high'),
('narrative-pathways-and-knowledge-architecture', 'frameworks-for-digital-knowledge-systems', 'next_article', 'moves from pathways to digital systems', 'high');

INSERT INTO repository_inventory VALUES
('pillar-pages-and-topic-clusters', 'https://github.com/Content-Catalyst-LLC/content-frameworks-code/tree/main/articles/pillar-pages-and-topic-clusters', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes'),
('narrative-pathways-and-knowledge-architecture', 'https://github.com/Content-Catalyst-LLC/content-frameworks-code/tree/main/articles/narrative-pathways-and-knowledge-architecture', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes'),
('frameworks-for-digital-knowledge-systems', 'https://github.com/Content-Catalyst-LLC/content-frameworks-code/tree/main/articles/frameworks-for-digital-knowledge-systems', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes'),
('taxonomy-design-for-content-frameworks', 'https://github.com/Content-Catalyst-LLC/content-frameworks-code/tree/main/articles/taxonomy-design-for-content-frameworks', 'no', 'no', 'no', 'no', 'no', 'no', 'no');
