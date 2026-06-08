DROP TABLE IF EXISTS article_inventory;
DROP TABLE IF EXISTS taxonomy_categories;
DROP TABLE IF EXISTS taxonomy_assignments;
DROP TABLE IF EXISTS taxonomy_metadata_inventory;

CREATE TABLE article_inventory (
  article_id TEXT PRIMARY KEY,
  slug TEXT NOT NULL,
  title TEXT NOT NULL,
  status TEXT NOT NULL,
  article_role TEXT NOT NULL,
  reader_stage TEXT NOT NULL,
  tags TEXT NOT NULL,
  review_owner TEXT NOT NULL
);

CREATE TABLE taxonomy_categories (
  category_id TEXT PRIMARY KEY,
  category_name TEXT NOT NULL,
  parent_category_id TEXT,
  category_type TEXT NOT NULL,
  relationship_type TEXT NOT NULL,
  status TEXT NOT NULL,
  category_definition TEXT NOT NULL,
  boundary_notes TEXT NOT NULL,
  governance_owner TEXT NOT NULL
);

CREATE TABLE taxonomy_assignments (
  assignment_id TEXT PRIMARY KEY,
  slug TEXT NOT NULL,
  category_id TEXT NOT NULL,
  assignment_type TEXT NOT NULL,
  assignment_confidence REAL NOT NULL,
  assignment_reason TEXT NOT NULL,
  review_status TEXT NOT NULL
);

CREATE TABLE taxonomy_metadata_inventory (
  slug TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  status TEXT NOT NULL,
  primary_category TEXT NOT NULL,
  secondary_categories TEXT NOT NULL,
  article_role TEXT NOT NULL,
  reader_stage TEXT NOT NULL,
  governance_owner TEXT NOT NULL,
  last_reviewed TEXT NOT NULL,
  category_definition TEXT NOT NULL,
  boundary_notes TEXT NOT NULL
);

INSERT INTO article_inventory VALUES
('TD007', 'pillar-pages-and-topic-clusters', 'Pillar Pages and Topic Clusters', 'published', 'pillar', 'foundation', 'pillar pages|topic clusters|knowledge architecture|internal linking', 'Knowledge architect'),
('TD008', 'narrative-pathways-and-knowledge-architecture', 'Narrative Pathways and Knowledge Architecture', 'published', 'method', 'intermediate', 'narrative pathways|knowledge architecture|reader pathways|internal links', 'Knowledge architect'),
('TD009', 'frameworks-for-digital-knowledge-systems', 'Frameworks for Digital Knowledge Systems', 'published', 'technical', 'intermediate', 'digital knowledge systems|metadata|taxonomy|repositories|governance', 'Knowledge architect'),
('TD010', 'taxonomy-design-for-content-frameworks', 'Taxonomy Design for Content Frameworks', 'published', 'method', 'intermediate', 'taxonomy design|categories|metadata|tags|governance|knowledge architecture', 'Knowledge architect'),
('TD011', 'internal-linking-as-framework-infrastructure', 'Internal Linking as Framework Infrastructure', 'planned', 'technical', 'intermediate', 'internal linking|semantic links|reader pathways|knowledge architecture', 'Knowledge architect'),
('TD012', 'content-audits-and-framework-governance', 'Content Audits and Framework Governance', 'planned', 'governance', 'advanced', 'content audits|governance|metadata|maintenance', 'Editorial governance lead');

INSERT INTO taxonomy_categories VALUES
('CAT001', 'Foundations', NULL, 'topic', 'broader', 'active', 'Definitions principles literacy distinctions and history', 'Includes foundational definitions history and conceptual distinctions', 'Series editor'),
('CAT002', 'Knowledge Architecture', NULL, 'topic', 'broader', 'active', 'Pillar pages topic clusters narrative pathways digital systems taxonomies metadata and links', 'Includes structural publishing logic', 'Knowledge architect'),
('CAT008', 'Framework Composition Scaling and Editorial Governance', NULL, 'topic', 'broader', 'active', 'Composition scaling limits maintenance drift and AI-assisted design', 'Includes governance scaling drift maintenance and AI-assisted design', 'Editorial governance lead'),
('CAT010', 'Method Article', NULL, 'article_role', 'related', 'active', 'Article that explains a practical or analytical method', 'Used for method and process articles', 'Knowledge architect'),
('CAT011', 'Technical Article', NULL, 'article_role', 'related', 'active', 'Article with implementation systems or computational focus', 'Used for code metadata schemas or system design', 'Editorial systems lead'),
('CAT012', 'Governance Article', NULL, 'article_role', 'related', 'active', 'Article focused on maintenance accountability and review', 'Used for governance audit and editorial maintenance articles', 'Editorial governance lead'),
('CAT013', 'Deprecated Internal Pathways Label', NULL, 'topic', 'related', 'deprecated', 'Deprecated early label that should not be used', 'Legacy term retained only for audit demonstration', 'Editorial governance lead');

INSERT INTO taxonomy_assignments VALUES
('A009', 'pillar-pages-and-topic-clusters', 'CAT002', 'primary', 0.97, 'Knowledge architecture pillar-cluster article', 'approved'),
('A010', 'narrative-pathways-and-knowledge-architecture', 'CAT002', 'primary', 0.97, 'Knowledge architecture pathway article', 'approved'),
('A011', 'narrative-pathways-and-knowledge-architecture', 'CAT010', 'facet', 0.88, 'Method article for pathway design', 'approved'),
('A012', 'frameworks-for-digital-knowledge-systems', 'CAT002', 'primary', 0.96, 'Digital knowledge systems belong to knowledge architecture', 'approved'),
('A013', 'frameworks-for-digital-knowledge-systems', 'CAT011', 'facet', 0.90, 'Technical systems article', 'approved'),
('A014', 'taxonomy-design-for-content-frameworks', 'CAT002', 'primary', 0.98, 'Taxonomy design belongs to knowledge architecture', 'approved'),
('A015', 'taxonomy-design-for-content-frameworks', 'CAT010', 'facet', 0.92, 'Method article for taxonomy design', 'approved'),
('A016', 'internal-linking-as-framework-infrastructure', 'CAT002', 'primary', 0.95, 'Internal linking belongs to knowledge architecture', 'needs_review'),
('A017', 'internal-linking-as-framework-infrastructure', 'CAT011', 'facet', 0.89, 'Technical infrastructure article', 'needs_review'),
('A018', 'content-audits-and-framework-governance', 'CAT008', 'primary', 0.91, 'Governance and maintenance article', 'needs_review'),
('A019', 'content-audits-and-framework-governance', 'CAT012', 'facet', 0.94, 'Governance article', 'needs_review');

INSERT INTO taxonomy_metadata_inventory VALUES
('pillar-pages-and-topic-clusters', 'Pillar Pages and Topic Clusters', 'published', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes'),
('narrative-pathways-and-knowledge-architecture', 'Narrative Pathways and Knowledge Architecture', 'published', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes'),
('frameworks-for-digital-knowledge-systems', 'Frameworks for Digital Knowledge Systems', 'published', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes'),
('taxonomy-design-for-content-frameworks', 'Taxonomy Design for Content Frameworks', 'published', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes'),
('internal-linking-as-framework-infrastructure', 'Internal Linking as Framework Infrastructure', 'planned', 'yes', 'yes', 'yes', 'yes', 'yes', 'no', 'yes', 'yes');
