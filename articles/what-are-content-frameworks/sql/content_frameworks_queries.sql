.headers on
.mode csv

SELECT cluster_name, status, COUNT(*) AS article_count
FROM articles
GROUP BY cluster_name, status
ORDER BY cluster_name, status;

SELECT domain, COUNT(*) AS framework_count
FROM framework_library
GROUP BY domain
ORDER BY framework_count DESC, domain ASC;

SELECT source_slug, COUNT(*) AS outgoing_link_count
FROM internal_links
GROUP BY source_slug
ORDER BY outgoing_link_count DESC;
