-- Content Frameworks SQL schema
-- Educational schema for pillars, articles, clusters, frameworks, templates, links, references, and editorial status.

CREATE TABLE IF NOT EXISTS content_pillars (
    pillar_id INTEGER PRIMARY KEY,
    pillar_name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    parent_space TEXT
);

CREATE TABLE IF NOT EXISTS articles (
    article_id INTEGER PRIMARY KEY,
    pillar_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    article_type TEXT NOT NULL,
    status TEXT NOT NULL,
    excerpt TEXT,
    repository_url TEXT,
    FOREIGN KEY (pillar_id) REFERENCES content_pillars(pillar_id)
);

CREATE TABLE IF NOT EXISTS topic_clusters (
    cluster_id INTEGER PRIMARY KEY,
    pillar_id INTEGER NOT NULL,
    cluster_name TEXT NOT NULL,
    description TEXT NOT NULL,
    sequence_order INTEGER NOT NULL,
    FOREIGN KEY (pillar_id) REFERENCES content_pillars(pillar_id)
);

CREATE TABLE IF NOT EXISTS article_cluster_map (
    article_id INTEGER NOT NULL,
    cluster_id INTEGER NOT NULL,
    PRIMARY KEY (article_id, cluster_id),
    FOREIGN KEY (article_id) REFERENCES articles(article_id),
    FOREIGN KEY (cluster_id) REFERENCES topic_clusters(cluster_id)
);

CREATE TABLE IF NOT EXISTS frameworks (
    framework_id INTEGER PRIMARY KEY,
    framework_name TEXT NOT NULL,
    framework_type TEXT NOT NULL,
    primary_function TEXT NOT NULL,
    ethical_caution TEXT
);

CREATE TABLE IF NOT EXISTS article_framework_map (
    article_id INTEGER NOT NULL,
    framework_id INTEGER NOT NULL,
    PRIMARY KEY (article_id, framework_id),
    FOREIGN KEY (article_id) REFERENCES articles(article_id),
    FOREIGN KEY (framework_id) REFERENCES frameworks(framework_id)
);

CREATE TABLE IF NOT EXISTS internal_links (
    link_id INTEGER PRIMARY KEY,
    source_article_id INTEGER NOT NULL,
    target_article_id INTEGER NOT NULL,
    relationship_type TEXT NOT NULL,
    FOREIGN KEY (source_article_id) REFERENCES articles(article_id),
    FOREIGN KEY (target_article_id) REFERENCES articles(article_id)
);

CREATE TABLE IF NOT EXISTS references_table (
    reference_id INTEGER PRIMARY KEY,
    article_id INTEGER NOT NULL,
    citation_text TEXT NOT NULL,
    url TEXT,
    source_type TEXT NOT NULL,
    FOREIGN KEY (article_id) REFERENCES articles(article_id)
);

CREATE TABLE IF NOT EXISTS editorial_metadata (
    metadata_id INTEGER PRIMARY KEY,
    article_id INTEGER NOT NULL,
    word_count INTEGER,
    has_excerpt BOOLEAN NOT NULL,
    has_image_metadata BOOLEAN NOT NULL,
    has_repository_link BOOLEAN NOT NULL,
    last_reviewed TEXT,
    FOREIGN KEY (article_id) REFERENCES articles(article_id)
);

INSERT INTO content_pillars
(pillar_id, pillar_name, slug, description, parent_space)
VALUES
(1, 'Content Frameworks', 'content-frameworks', 'Structured models for organizing, communicating, and scaling complex ideas.', 'Strategic Ideation');

INSERT INTO frameworks
(framework_id, framework_name, framework_type, primary_function, ethical_caution)
VALUES
(1, 'Pillar-Cluster Architecture', 'Knowledge Architecture', 'Organize central topics and supporting articles.', 'Avoid overbuilding rigid taxonomies.'),
(2, 'AIDA', 'Persuasive Sequence', 'Sequence attention, interest, desire, and action.', 'Avoid treating all communication as conversion.'),
(3, 'PAS', 'Persuasive Sequence', 'Frame problem, intensify stakes, and offer resolution.', 'Avoid manipulative agitation.'),
(4, 'Jobs to Be Done', 'Audience Need', 'Clarify the progress people seek in context.', 'Avoid reducing human motives to utility alone.'),
(5, 'Message House', 'Message Architecture', 'Organize claims, pillars, evidence, and audience-specific messaging.', 'Avoid over-simplifying contested ideas.');
