# catalyst_canvas_framework_value_analysis.R
# Professional-grade base R workflow for Catalyst Canvas-style
# framework value analysis, article-map coverage, metadata
# readiness, and editorial governance summaries.

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

article_map <- read.csv(file.path(data_dir, "content_framework_article_map.csv"), stringsAsFactors = FALSE)
frameworks <- read.csv(file.path(data_dir, "framework_value_examples.csv"), stringsAsFactors = FALSE)
metadata <- read.csv(file.path(data_dir, "metadata_inventory.csv"), stringsAsFactors = FALSE)
links <- read.csv(file.path(data_dir, "internal_links.csv"), stringsAsFactors = FALSE)
taxonomy <- read.csv(file.path(data_dir, "taxonomy_categories.csv"), stringsAsFactors = FALSE)

value_dimensions <- c(
  "comprehension",
  "comparison",
  "retention",
  "action",
  "governance",
  "evidence_integrity",
  "audience_fit",
  "ethical_safety"
)

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
# Article coverage
# ------------------------------------------------------------
coverage <- aggregate(
  title ~ cluster + status,
  data = article_map,
  FUN = length
)

names(coverage) <- c("cluster", "status", "article_count")

cluster_totals <- aggregate(
  title ~ cluster,
  data = article_map,
  FUN = length
)

names(cluster_totals) <- c("cluster", "total_articles")

published <- subset(coverage, status == "published")
names(published)[names(published) == "article_count"] <- "published_articles"

coverage_wide <- merge(cluster_totals, published[, c("cluster", "published_articles")], by = "cluster", all.x = TRUE)
coverage_wide$published_articles[is.na(coverage_wide$published_articles)] <- 0
coverage_wide$coverage_rate <- round(coverage_wide$published_articles / coverage_wide$total_articles, 4)
coverage_wide$coverage_status <- ifelse(coverage_wide$coverage_rate >= 0.60, "healthy", "needs development")

# ------------------------------------------------------------
# Metadata readiness
# ------------------------------------------------------------
metadata_complete <- metadata[, metadata_fields] == "yes"
metadata$completed_fields <- rowSums(metadata_complete)
metadata$required_fields <- length(metadata_fields)
metadata$completion_rate <- round(metadata$completed_fields / metadata$required_fields, 4)
metadata$metadata_readiness <- ifelse(metadata$completion_rate >= 0.85, "ready", "needs metadata work")

metadata_report <- metadata[, c(
  "slug",
  "title",
  "status",
  "completed_fields",
  "required_fields",
  "completion_rate",
  "metadata_readiness"
)]

# ------------------------------------------------------------
# Framework value scores
# ------------------------------------------------------------
frameworks$value_score <- rowSums(frameworks[, value_dimensions])
frameworks$average_value_score <- round(frameworks$value_score / length(value_dimensions), 3)
frameworks$product_readiness <- ifelse(
  frameworks$value_score >= 32 &
    frameworks$evidence_integrity >= 4 &
    frameworks$ethical_safety >= 4,
  "ready",
  "review needed"
)

framework_value_report <- frameworks[, c(
  "framework_id",
  "framework_name",
  "domain",
  "primary_use",
  "value_score",
  "average_value_score",
  "product_readiness",
  "risk_severity",
  "risk_if_misused"
)]

domain_value_summary <- aggregate(
  value_score ~ domain,
  data = frameworks,
  FUN = mean
)

names(domain_value_summary) <- c("domain", "average_framework_value_score")
domain_value_summary$average_framework_value_score <- round(domain_value_summary$average_framework_value_score, 3)

risk_summary <- as.data.frame(table(frameworks$risk_severity), stringsAsFactors = FALSE)
names(risk_summary) <- c("risk_severity", "framework_count")

# ------------------------------------------------------------
# Internal-link summary
# ------------------------------------------------------------
outgoing <- as.data.frame(table(links$source_slug), stringsAsFactors = FALSE)
names(outgoing) <- c("slug", "outgoing_links")

incoming <- as.data.frame(table(links$target_slug), stringsAsFactors = FALSE)
names(incoming) <- c("slug", "incoming_links")

all_slugs <- data.frame(slug = sort(unique(c(article_map$slug, outgoing$slug, incoming$slug))), stringsAsFactors = FALSE)

link_report <- merge(all_slugs, outgoing, by = "slug", all.x = TRUE)
link_report <- merge(link_report, incoming, by = "slug", all.x = TRUE)
link_report$outgoing_links[is.na(link_report$outgoing_links)] <- 0
link_report$incoming_links[is.na(link_report$incoming_links)] <- 0
link_report$total_link_degree <- link_report$outgoing_links + link_report$incoming_links
link_report$network_role <- ifelse(
  link_report$total_link_degree >= 5,
  "hub",
  ifelse(link_report$total_link_degree >= 3, "connector", "thinly linked")
)

# ------------------------------------------------------------
# Taxonomy coverage
# ------------------------------------------------------------
taxonomy_counts <- as.data.frame(table(article_map$cluster), stringsAsFactors = FALSE)
names(taxonomy_counts) <- c("category", "article_count")

taxonomy_report <- merge(taxonomy, taxonomy_counts, by = "category", all.x = TRUE)
taxonomy_report$article_count[is.na(taxonomy_report$article_count)] <- 0
taxonomy_report$taxonomy_status <- ifelse(taxonomy_report$article_count > 0, "active", "missing from sample")

# ------------------------------------------------------------
# Catalyst Canvas catalog export
# ------------------------------------------------------------
catalog <- merge(article_map, metadata_report[, c("slug", "completion_rate", "metadata_readiness")], by = "slug", all.x = TRUE)
catalog <- merge(catalog, link_report[, c("slug", "total_link_degree", "network_role")], by = "slug", all.x = TRUE)
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
  "completion_rate",
  "metadata_readiness",
  "total_link_degree",
  "network_role",
  "github_path"
)]

# ------------------------------------------------------------
# Write outputs
# ------------------------------------------------------------
write.csv(coverage, file.path(tables_dir, "r_article_map_status_summary.csv"), row.names = FALSE)
write.csv(coverage_wide, file.path(tables_dir, "r_cluster_coverage_readiness.csv"), row.names = FALSE)
write.csv(metadata_report, file.path(tables_dir, "r_metadata_readiness_report.csv"), row.names = FALSE)
write.csv(framework_value_report, file.path(tables_dir, "r_framework_value_report.csv"), row.names = FALSE)
write.csv(domain_value_summary, file.path(tables_dir, "r_domain_value_summary.csv"), row.names = FALSE)
write.csv(risk_summary, file.path(tables_dir, "r_framework_risk_summary.csv"), row.names = FALSE)
write.csv(link_report, file.path(tables_dir, "r_internal_link_report.csv"), row.names = FALSE)
write.csv(taxonomy_report, file.path(tables_dir, "r_taxonomy_coverage_report.csv"), row.names = FALSE)
write.csv(catalog, file.path(catalog_dir, "r_catalyst_canvas_catalog_export.csv"), row.names = FALSE)

# ------------------------------------------------------------
# Figures
# ------------------------------------------------------------
png(file.path(figures_dir, "r_article_status_counts.png"), width = 1100, height = 750)
barplot(
  table(article_map$status),
  main = "Content Frameworks Article Status Counts",
  ylab = "Article count"
)
dev.off()

png(file.path(figures_dir, "r_framework_value_by_domain.png"), width = 1200, height = 800)
barplot(
  domain_value_summary$average_framework_value_score,
  names.arg = domain_value_summary$domain,
  las = 2,
  main = "Average Framework Value Score by Domain",
  ylab = "Average value score"
)
dev.off()

png(file.path(figures_dir, "r_internal_link_degree.png"), width = 1200, height = 800)
barplot(
  link_report$total_link_degree,
  names.arg = link_report$slug,
  las = 2,
  main = "Internal Link Degree by Article",
  ylab = "Total link degree"
)
dev.off()

# ------------------------------------------------------------
# Markdown report
# ------------------------------------------------------------
report_lines <- c(
  "# Catalyst Canvas R Framework Value Analysis",
  "",
  "Article: Why Frameworks Matter in Research, Education, and Strategic Communication",
  "",
  "## Summary",
  "",
  paste0("- Article records: ", nrow(article_map)),
  paste0("- Framework records: ", nrow(frameworks)),
  paste0("- Internal links: ", nrow(links)),
  paste0("- Taxonomy categories: ", nrow(taxonomy)),
  "",
  "## Outputs",
  "",
  "- `r_article_map_status_summary.csv`",
  "- `r_cluster_coverage_readiness.csv`",
  "- `r_metadata_readiness_report.csv`",
  "- `r_framework_value_report.csv`",
  "- `r_domain_value_summary.csv`",
  "- `r_internal_link_report.csv`",
  "- `r_taxonomy_coverage_report.csv`",
  "- `r_catalyst_canvas_catalog_export.csv`",
  "",
  "These outputs are generated from synthetic data and demonstrate product-grade editorial intelligence workflows."
)

writeLines(report_lines, file.path(reports_dir, "r_catalyst_canvas_framework_value_analysis.md"))

print("Catalyst Canvas R framework value analysis complete.")
print(coverage_wide)
print(domain_value_summary)
