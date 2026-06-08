DROP TABLE IF EXISTS pathway_article_inventory;
DROP TABLE IF EXISTS internal_links;
DROP TABLE IF EXISTS narrative_pathway_definitions;
DROP TABLE IF EXISTS metadata_inventory;

CREATE TABLE pathway_article_inventory (
  article_id TEXT PRIMARY KEY,
  slug TEXT NOT NULL,
  title TEXT NOT NULL,
  cluster_name TEXT NOT NULL,
  status TEXT NOT NULL,
  article_role TEXT NOT NULL,
  pathway_role TEXT NOT NULL,
  reader_state TEXT NOT NULL,
  has_series_context TEXT NOT NULL,
  links_to_article_map TEXT NOT NULL,
  has_transition_links TEXT NOT NULL,
  has_next_step TEXT NOT NULL,
  review_owner TEXT NOT NULL
);

CREATE TABLE internal_links (
  source_slug TEXT NOT NULL,
  target_slug TEXT NOT NULL,
  relationship_type TEXT NOT NULL,
  transition_purpose TEXT NOT NULL,
  priority TEXT NOT NULL
);

CREATE TABLE narrative_pathway_definitions (
  pathway_id TEXT PRIMARY KEY,
  pathway_name TEXT NOT NULL,
  pathway_type TEXT NOT NULL,
  reader_state TEXT NOT NULL,
  required_article_slugs TEXT NOT NULL,
  pathway_goal TEXT NOT NULL,
  review_owner TEXT NOT NULL
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

INSERT INTO pathway_article_inventory VALUES
('NP001', 'what-are-content-frameworks', 'What Are Content Frameworks', 'Foundations', 'published', 'definition', 'foundation', 'beginner', 'yes', 'yes', 'yes', 'yes', 'Series editor'),
('NP004', 'framework-literacy-and-the-structure-of-usable-knowledge', 'Framework Literacy and the Structure of Usable Knowledge', 'Foundations', 'published', 'critique', 'critical_pathway', 'returning_reader', 'yes', 'yes', 'yes', 'yes', 'Series editor'),
('NP007', 'pillar-pages-and-topic-clusters', 'Pillar Pages and Topic Clusters', 'Knowledge Architecture', 'published', 'pillar', 'architecture', 'beginner', 'yes', 'yes', 'yes', 'yes', 'Knowledge architect'),
('NP008', 'narrative-pathways-and-knowledge-architecture', 'Narrative Pathways and Knowledge Architecture', 'Knowledge Architecture', 'published', 'method', 'pathway_design', 'practitioner', 'yes', 'yes', 'yes', 'yes', 'Knowledge architect'),
('NP009', 'frameworks-for-digital-knowledge-systems', 'Frameworks for Digital Knowledge Systems', 'Knowledge Architecture', 'published', 'technical', 'digital_systems', 'practitioner', 'yes', 'yes', 'yes', 'yes', 'Knowledge architect'),
('NP010', 'taxonomy-design-for-content-frameworks', 'Taxonomy Design for Content Frameworks', 'Knowledge Architecture', 'planned', 'method', 'taxonomy_design', 'editor', 'no', 'no', 'no', 'no', 'Knowledge architect');

INSERT INTO internal_links VALUES
('pillar-pages-and-topic-clusters', 'narrative-pathways-and-knowledge-architecture', 'next_article', 'moves from content structure to reader movement', 'high'),
('narrative-pathways-and-knowledge-architecture', 'pillar-pages-and-topic-clusters', 'previous_article', 'connects pathways back to pillar-cluster architecture', 'high'),
('narrative-pathways-and-knowledge-architecture', 'frameworks-for-digital-knowledge-systems', 'next_article', 'moves from reader pathways to digital system architecture', 'high'),
('narrative-pathways-and-knowledge-architecture', 'what-are-content-frameworks', 'prerequisite', 'connects pathway design to framework definition', 'medium'),
('narrative-pathways-and-knowledge-architecture', 'framework-literacy-and-the-structure-of-usable-knowledge', 'critical_bridge', 'connects pathway design to responsible framework use', 'medium'),
('frameworks-for-digital-knowledge-systems', 'narrative-pathways-and-knowledge-architecture', 'previous_article', 'connects digital systems back to pathway logic', 'high');

INSERT INTO narrative_pathway_definitions VALUES
('PW001', 'Foundational Content Frameworks Pathway', 'foundational', 'beginner', 'what-are-content-frameworks|framework-literacy-and-the-structure-of-usable-knowledge', 'Move readers from definition to literacy', 'Series editor'),
('PW002', 'Knowledge Architecture Pathway', 'learning', 'practitioner', 'pillar-pages-and-topic-clusters|narrative-pathways-and-knowledge-architecture|frameworks-for-digital-knowledge-systems|taxonomy-design-for-content-frameworks', 'Move readers from pillar-cluster structure to pathways digital systems and taxonomy', 'Knowledge architect');

INSERT INTO metadata_inventory VALUES
('pillar-pages-and-topic-clusters', 'Pillar Pages and Topic Clusters', 'published', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes'),
('narrative-pathways-and-knowledge-architecture', 'Narrative Pathways and Knowledge Architecture', 'published', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes'),
('frameworks-for-digital-knowledge-systems', 'Frameworks for Digital Knowledge Systems', 'published', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes'),
('taxonomy-design-for-content-frameworks', 'Taxonomy Design for Content Frameworks', 'planned', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no');
