# catalyst_canvas_pillar_cluster_analysis.R
# Base R workflow for pillar pages, topic clusters,
# article coverage, internal-link diagnostics, metadata readiness,
# and editorial governance.

if (!exists("article_root")) {
  article_root <- getwd()
}

data_dir <- file.path(article_root, "data")
tables_dir <- file.path(article_root, "outputs", "tables")
figures_dir <- file.path(article_root, "outputs", "figures")
reports_dir <- file.path(article_root, "outputs", "reports")
catalog_dir <- file.path(article_root, "outputs", "catalog_exports")

dir.create(tables_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(figures_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(reports_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(catalog_dir, recursive = TRUE, showWarnings = FALSE)

articles <- read.csv(file.path(data_dir, "pillar_cluster_articles.csv"), stringsAsFactors = FALSE)
links <- read.csv(file.path(data_dir, "internal_links.csv"), stringsAsFactors = FALSE)
metadata <- read.csv(file.path(data_dir, "metadata_inventory.csv"), stringsAsFactors = FALSE)
taxonomy <- read.csv(file.path(data_dir, "taxonomy_categories.csv"), stringsAsFactors = FALSE)

pillar_slug <- "pillar-pages-and-topic-clusters"

metadata_fields <- c(
  "excerpt",
  "tags",
  "github_url",
  "image_alt",
  "references",
  "last_reviewed",
  "series_context",
  "footer_navigation"
)

# ------------------------------------------------------------
# Cluster coverage
# ------------------------------------------------------------
cluster_total <- aggregate(
  slug ~ cluster,
  data = articles,
  FUN = length
)
names(cluster_total) <- c("cluster", "total_articles")

published_articles <- subset(articles, status == "published")

cluster_published <- aggregate(
  slug ~ cluster,
  data = published_articles,
  FUN = length
)
names(cluster_published) <- c("cluster", "published_articles")

cluster_summary <- merge(cluster_total, cluster_published, by = "cluster", all.x = TRUE)
cluster_summary$published_articles[is.na(cluster_summary$published_articles)] <- 0
cluster_summary$planned_articles <- cluster_summary$total_articles - cluster_summary$published_articles
cluster_summary$cluster_readiness <- round(cluster_summary$published_articles / cluster_summary$total_articles, 4)

cluster_summary$cluster_status <- ifelse(
  cluster_summary$cluster_readiness >= 0.75,
  "mature",
  ifelse(cluster_summary$cluster_readiness >= 0.40, "developing", "early stage")
)

# ------------------------------------------------------------
# Internal-link degree
# ------------------------------------------------------------
outgoing <- as.data.frame(table(links$source_slug), stringsAsFactors = FALSE)
names(outgoing) <- c("slug", "outgoing_links")

incoming <- as.data.frame(table(links$target_slug), stringsAsFactors = FALSE)
names(incoming) <- c("slug", "incoming_links")

link_report <- merge(articles[, c("slug", "title", "cluster", "status", "article_role")], outgoing, by = "slug", all.x = TRUE)
link_report <- merge(link_report, incoming, by = "slug", all.x = TRUE)
link_report$outgoing_links[is.na(link_report$outgoing_links)] <- 0
link_report$incoming_links[is.na(link_report$incoming_links)] <- 0
link_report$total_link_degree <- link_report$outgoing_links + link_report$incoming_links

link_report$network_role <- ifelse(
  link_report$slug == pillar_slug,
  "pillar",
  ifelse(
    link_report$total_link_degree >= 5,
    "cluster hub",
    ifelse(link_report$total_link_degree >= 2, "connected article", "thinly linked article")
  )
)

# ------------------------------------------------------------
# Metadata readiness
# ------------------------------------------------------------
metadata_complete <- metadata[, metadata_fields] == "yes"
metadata$completed_fields <- rowSums(metadata_complete)
metadata$required_fields <- length(metadata_fields)
metadata$metadata_completion <- round(metadata$completed_fields / metadata$required_fields, 4)
metadata$metadata_status <- ifelse(metadata$metadata_completion >= 0.85, "ready", "needs metadata work")

metadata_report <- metadata[, c(
  "slug",
  "title",
  "status",
  "completed_fields",
  "required_fields",
  "metadata_completion",
  "metadata_status"
)]

# ------------------------------------------------------------
# Article readiness
# ------------------------------------------------------------
article_readiness <- merge(
  link_report,
  metadata_report[, c("slug", "metadata_completion", "metadata_status")],
  by = "slug",
  all.x = TRUE
)

article_readiness$editorial_status <- ifelse(
  article_readiness$status == "published" &
    article_readiness$metadata_completion >= 0.85 &
    article_readiness$total_link_degree >= 2,
  "ready",
  ifelse(article_readiness$status == "planned", "planned", "review required")
)

# ------------------------------------------------------------
# Taxonomy coverage
# ------------------------------------------------------------
taxonomy_counts <- as.data.frame(table(articles$cluster), stringsAsFactors = FALSE)
names(taxonomy_counts) <- c("category", "article_count")

taxonomy_report <- merge(taxonomy, taxonomy_counts, by = "category", all.x = TRUE)
taxonomy_report$article_count[is.na(taxonomy_report$article_count)] <- 0
taxonomy_report$taxonomy_status <- ifelse(taxonomy_report$article_count > 0, "active", "missing from sample")

# ------------------------------------------------------------
# Pillar coverage density
# ------------------------------------------------------------
pillar_outgoing <- subset(links, source_slug == pillar_slug & relationship_type == "pillar_to_cluster")
knowledge_cluster_articles <- subset(articles, slug != pillar_slug & cluster == "Knowledge Architecture")
pillar_coverage_density <- ifelse(
  nrow(knowledge_cluster_articles) > 0,
  round(nrow(pillar_outgoing) / nrow(knowledge_cluster_articles), 4),
  0
)

# ------------------------------------------------------------
# Catalog export
# ------------------------------------------------------------
catalog <- article_readiness
catalog$catalog_product <- "Catalyst Canvas"
catalog$series <- "Content Frameworks"
catalog$github_path <- paste0("articles/", catalog$slug, "/")

catalog <- catalog[, c(
  "catalog_product",
  "series",
  "slug",
  "title",
  "cluster",
  "status",
  "article_role",
  "network_role",
  "metadata_completion",
  "metadata_status",
  "editorial_status",
  "github_path"
)]

# ------------------------------------------------------------
# Write outputs
# ------------------------------------------------------------
write.csv(cluster_summary, file.path(tables_dir, "r_pillar_cluster_coverage_summary.csv"), row.names = FALSE)
write.csv(link_report, file.path(tables_dir, "r_pillar_cluster_link_report.csv"), row.names = FALSE)
write.csv(metadata_report, file.path(tables_dir, "r_pillar_cluster_metadata_readiness.csv"), row.names = FALSE)
write.csv(article_readiness, file.path(tables_dir, "r_pillar_cluster_article_readiness.csv"), row.names = FALSE)
write.csv(taxonomy_report, file.path(tables_dir, "r_taxonomy_pillar_cluster_coverage.csv"), row.names = FALSE)
write.csv(catalog, file.path(catalog_dir, "r_catalyst_canvas_pillar_cluster_catalog.csv"), row.names = FALSE)

# ------------------------------------------------------------
# Figures
# ------------------------------------------------------------
png(file.path(figures_dir, "r_cluster_readiness.png"), width = 1200, height = 800)
barplot(
  cluster_summary$cluster_readiness,
  names.arg = cluster_summary$cluster,
  las = 2,
  main = "Cluster Readiness by Topic Group",
  ylab = "Published / total articles"
)
dev.off()

png(file.path(figures_dir, "r_article_link_degree.png"), width = 1300, height = 850)
barplot(
  article_readiness$total_link_degree,
  names.arg = article_readiness$slug,
  las = 2,
  main = "Article Link Degree in Pillar-Cluster System",
  ylab = "Total link degree"
)
dev.off()

png(file.path(figures_dir, "r_metadata_completion.png"), width = 1300, height = 850)
barplot(
  article_readiness$metadata_completion,
  names.arg = article_readiness$slug,
  las = 2,
  main = "Metadata Completion by Article",
  ylab = "Metadata completion"
)
dev.off()

# ------------------------------------------------------------
# Markdown report
# ------------------------------------------------------------
report_lines <- c(
  "# Catalyst Canvas Pillar-Cluster Analysis",
  "",
  "Article: Pillar Pages and Topic Clusters",
  "",
  "## Summary",
  "",
  paste0("- Articles reviewed: ", nrow(articles)),
  paste0("- Internal links reviewed: ", nrow(links)),
  paste0("- Topic clusters: ", nrow(cluster_summary)),
  paste0("- Pillar coverage density: ", pillar_coverage_density),
  paste0("- Articles requiring review: ", sum(article_readiness$editorial_status == "review required")),
  "",
  "## Outputs",
  "",
  "- `r_pillar_cluster_coverage_summary.csv`",
  "- `r_pillar_cluster_link_report.csv`",
  "- `r_pillar_cluster_metadata_readiness.csv`",
  "- `r_pillar_cluster_article_readiness.csv`",
  "- `r_taxonomy_pillar_cluster_coverage.csv`",
  "- `r_catalyst_canvas_pillar_cluster_catalog.csv`",
  "",
  "These outputs are generated from synthetic data and demonstrate professional-grade pillar-cluster workflows."
)

writeLines(report_lines, file.path(reports_dir, "r_catalyst_canvas_pillar_cluster_analysis.md"))

print("Catalyst Canvas R pillar-cluster analysis complete.")
print(cluster_summary)
print(article_readiness[, c("slug", "network_role", "metadata_status", "editorial_status")])
