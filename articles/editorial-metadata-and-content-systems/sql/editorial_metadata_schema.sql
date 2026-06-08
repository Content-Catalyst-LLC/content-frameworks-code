DROP TABLE IF EXISTS editorial_metadata_inventory;
DROP TABLE IF EXISTS image_metadata_inventory;
DROP TABLE IF EXISTS reference_metadata;
DROP TABLE IF EXISTS repository_manifest;
DROP TABLE IF EXISTS editorial_review_queue;

CREATE TABLE editorial_metadata_inventory (
  article_order INTEGER NOT NULL,
  title TEXT NOT NULL,
  seo_title TEXT NOT NULL,
  slug TEXT PRIMARY KEY,
  series TEXT NOT NULL,
  cluster_name TEXT NOT NULL,
  article_type TEXT NOT NULL,
  status TEXT NOT NULL,
  description TEXT NOT NULL,
  excerpt TEXT NOT NULL,
  tags TEXT NOT NULL,
  image_title TEXT NOT NULL,
  image_filename TEXT NOT NULL,
  alt_text TEXT NOT NULL,
  caption TEXT NOT NULL,
  image_description TEXT NOT NULL,
  references_complete TEXT NOT NULL,
  repository_url TEXT NOT NULL,
  repository_path TEXT NOT NULL,
  previous_title TEXT NOT NULL,
  previous_url TEXT,
  article_map_title TEXT NOT NULL,
  article_map_url TEXT NOT NULL,
  next_title TEXT NOT NULL,
  next_url TEXT,
  last_reviewed TEXT NOT NULL
);

CREATE TABLE image_metadata_inventory (
  slug TEXT NOT NULL,
  image_title TEXT NOT NULL,
  image_filename TEXT NOT NULL,
  alt_text TEXT,
  caption TEXT,
  image_description TEXT,
  style_notes TEXT,
  review_status TEXT NOT NULL
);

CREATE TABLE reference_metadata (
  source_id TEXT PRIMARY KEY,
  slug TEXT NOT NULL,
  source_title TEXT NOT NULL,
  source_type TEXT NOT NULL,
  authority_level TEXT NOT NULL,
  recency_risk TEXT NOT NULL,
  claim_supported TEXT NOT NULL,
  review_status TEXT NOT NULL
);

CREATE TABLE repository_manifest (
  slug TEXT PRIMARY KEY,
  repository_url TEXT NOT NULL,
  repository_path TEXT NOT NULL,
  required_folders_present TEXT NOT NULL,
  readme_present TEXT NOT NULL,
  python_workflow_present TEXT NOT NULL,
  r_workflow_present TEXT NOT NULL,
  sql_schema_present TEXT NOT NULL,
  outputs_present TEXT NOT NULL,
  manifest_status TEXT NOT NULL
);

CREATE TABLE editorial_review_queue (
  review_id TEXT PRIMARY KEY,
  slug TEXT NOT NULL,
  issue_type TEXT NOT NULL,
  severity TEXT NOT NULL,
  review_note TEXT NOT NULL
);

INSERT INTO editorial_metadata_inventory VALUES
(12, 'Content Audits and Framework Governance', 'Content Audits and Framework Governance: How to Maintain Knowledge Systems', 'content-audits-and-framework-governance', 'Content Frameworks', 'Knowledge Architecture', 'governance', 'published', 'Article on audits governance and maintenance systems', 'yes', 'content audits; framework governance; metadata', 'Content Audits and Framework Governance', 'content-audits-and-framework-governance.jpg', 'Restrained editorial illustration of audit tables and governance records', 'Content audits and governance keep knowledge systems maintained', 'Image description complete', 'yes', 'https://github.com/Content-Catalyst-LLC/content-frameworks-code/tree/main/articles/content-audits-and-framework-governance', 'articles/content-audits-and-framework-governance/', 'Internal Linking as Framework Infrastructure', '/internal-linking-as-framework-infrastructure/', 'Content Frameworks', '/content-frameworks/', 'Editorial Metadata and Content Systems', '/editorial-metadata-and-content-systems/', '2026-06-08'),
(13, 'Editorial Metadata and Content Systems', 'Editorial Metadata and Content Systems: How Content Records Support Governance', 'editorial-metadata-and-content-systems', 'Content Frameworks', 'Knowledge Architecture', 'technical', 'published', 'Technical article on metadata fields status tracking references excerpts image metadata and repository links', 'yes', 'metadata; editorial systems; content governance', 'Editorial Metadata and Content Systems', 'editorial-metadata-and-content-systems.jpg', 'Restrained editorial illustration of metadata records and content-system infrastructure', 'Editorial metadata turns content frameworks into maintainable systems', 'Image description complete', 'yes', 'https://github.com/Content-Catalyst-LLC/content-frameworks-code/tree/main/articles/editorial-metadata-and-content-systems', 'articles/editorial-metadata-and-content-systems/', 'Content Audits and Framework Governance', '/content-audits-and-framework-governance/', 'Content Frameworks', '/content-frameworks/', 'Educational Scaffolding and the Design of Learning Systems', '/educational-scaffolding-and-the-design-of-learning-systems/', '2026-06-08'),
(14, 'Educational Scaffolding and the Design of Learning Systems', 'Educational Scaffolding and the Design of Learning Systems', 'educational-scaffolding-and-the-design-of-learning-systems', 'Content Frameworks', 'Educational Research and Conceptual Frameworks', 'methodological', 'published', 'Article on sequencing knowledge for cumulative learning', 'yes', 'educational scaffolding; learning systems; framework design', 'Educational Scaffolding and the Design of Learning Systems', 'educational-scaffolding-and-the-design-of-learning-systems.jpg', 'Restrained editorial illustration of learning system scaffolding', 'Educational scaffolding supports cumulative understanding', 'Image description complete', 'yes', 'https://github.com/Content-Catalyst-LLC/content-frameworks-code/tree/main/articles/educational-scaffolding-and-the-design-of-learning-systems', 'articles/educational-scaffolding-and-the-design-of-learning-systems/', 'Editorial Metadata and Content Systems', '/editorial-metadata-and-content-systems/', 'Content Frameworks', '/content-frameworks/', 'Conceptual Models in Communication', '/conceptual-models-in-communication/', '2026-06-08');

INSERT INTO image_metadata_inventory VALUES
('editorial-metadata-and-content-systems', 'Editorial Metadata and Content Systems', 'editorial-metadata-and-content-systems.jpg', 'Restrained editorial illustration of metadata records article cards taxonomy fields content-system ledgers repository links review notes and organized publishing infrastructure without text or labels', 'Editorial metadata turns content frameworks into maintainable systems by describing articles links images references repositories statuses and review obligations', 'A serious editorial illustration representing editorial metadata as structured publishing infrastructure', 'Restrained institutional editorial style with no labels or text', 'ready');

INSERT INTO reference_metadata VALUES
('REF001', 'editorial-metadata-and-content-systems', 'DCMI Metadata Terms', 'official_standard', 'high', 'medium', 'Metadata fields and interoperability', 'ready'),
('REF002', 'editorial-metadata-and-content-systems', 'Schema.org Vocabulary', 'official_vocabulary', 'high', 'medium', 'Structured data and machine-readable content records', 'ready'),
('REF003', 'editorial-metadata-and-content-systems', 'WCAG 2.2', 'official_standard', 'high', 'medium', 'Accessibility requirements and non-text content', 'ready');

INSERT INTO repository_manifest VALUES
('editorial-metadata-and-content-systems', 'https://github.com/Content-Catalyst-LLC/content-frameworks-code/tree/main/articles/editorial-metadata-and-content-systems', 'articles/editorial-metadata-and-content-systems/', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'ready');

INSERT INTO editorial_review_queue VALUES
('R001', 'editorial-metadata-and-content-systems', 'publication', 'low', 'Confirm final WordPress attachment ID after upload'),
('R002', 'editorial-metadata-and-content-systems', 'repository', 'low', 'Confirm GitHub folder appears after push');
