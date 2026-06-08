# catalyst_canvas_digital_knowledge_system_analysis.R
# Base R workflow for digital knowledge system coverage,
# metadata readiness, internal-link degree, repository readiness,
# system-health scoring, and editorial governance.

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

content <- read.csv(file.path(data_dir, "content_inventory.csv"), stringsAsFactors = FALSE)
metadata <- read.csv(file.path(data_dir, "metadata_inventory.csv"), stringsAsFactors = FALSE)
links <- read.csv(file.path(data_dir, "internal_links.csv"), stringsAsFactors = FALSE)
repositories <- read.csv(file.path(data_dir, "repository_inventory.csv"), stringsAsFactors = FALSE)
taxonomy <- read.csv(file.path(data_dir, "taxonomy_categories.csv"), stringsAsFactors = FALSE)

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

repository_fields <- c(
  "repository_exists",
  "readme_exists",
  "python_workflow",
  "r_workflow",
  "sql_schema",
  "workflow_outputs_exist",
  "governance_docs"
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
# Link diagnostics
# ------------------------------------------------------------
outgoing <- as.data.frame(table(links$source_slug), stringsAsFactors = FALSE)
names(outgoing) <- c("slug", "outgoing_links")

incoming <- as.data.frame(table(links$target_slug), stringsAsFactors = FALSE)
names(incoming) <- c("slug", "incoming_links")

link_report <- merge(
  content[, c("slug", "title", "cluster", "status", "content_type", "article_role")],
  outgoing,
  by = "slug",
  all.x = TRUE
)

link_report <- merge(link_report, incoming, by = "slug", all.x = TRUE)
link_report$outgoing_links[is.na(link_report$outgoing_links)] <- 0
link_report$incoming_links[is.na(link_report$incoming_links)] <- 0
link_report$total_link_degree <- link_report$outgoing_links + link_report$incoming_links

link_report$link_status <- ifelse(
  link_report$total_link_degree >= 4,
  "well connected",
  ifelse(link_report$total_link_degree >= 2, "connected", "link review required")
)

# ------------------------------------------------------------
# Repository readiness
# ------------------------------------------------------------
repo_complete <- repositories[, repository_fields] == "yes"
repositories$repository_score <- round(rowSums(repo_complete) / length(repository_fields), 4)
repositories$repository_status <- ifelse(
  repositories$repository_score >= 0.75,
  "ready",
  ifelse(repositories$repository_score >= 0.50, "developing", "review required")
)

repository_report <- repositories[, c(
  "slug",
  "repository_url",
  "repository_score",
  "repository_status"
)]

# ------------------------------------------------------------
# Taxonomy coverage
# ------------------------------------------------------------
taxonomy_counts <- as.data.frame(table(content$cluster), stringsAsFactors = FALSE)
names(taxonomy_counts) <- c("category", "content_count")

taxonomy_report <- merge(taxonomy, taxonomy_counts, by = "category", all.x = TRUE)
taxonomy_report$content_count[is.na(taxonomy_report$content_count)] <- 0
taxonomy_report$taxonomy_status <- ifelse(taxonomy_report$content_count > 0, "active", "missing from sample")

# ------------------------------------------------------------
# Joined system health report
# ------------------------------------------------------------
system_report <- merge(
  content,
  metadata_report[, c("slug", "metadata_completion", "metadata_status")],
  by = "slug",
  all.x = TRUE
)

system_report <- merge(
  system_report,
  link_report[, c("slug", "outgoing_links", "incoming_links", "total_link_degree", "link_status")],
  by = "slug",
  all.x = TRUE
)

system_report <- merge(
  system_report,
  repository_report,
  by = "slug",
  all.x = TRUE
)

system_report$metadata_completion[is.na(system_report$metadata_completion)] <- 0
system_report$total_link_degree[is.na(system_report$total_link_degree)] <- 0
system_report$repository_score[is.na(system_report$repository_score)] <- 0

system_report$coverage_score <- ifelse(
  system_report$status == "published",
  1,
  ifelse(system_report$status == "planned", 0.5, 0.25)
)

system_report$link_score <- pmin(system_report$total_link_degree / 4, 1)
system_report$review_score <- ifelse(system_report$review_current == "yes", 1, 0)
system_report$taxonomy_score <- ifelse(system_report$cluster %in% taxonomy$category, 1, 0)

system_report$system_health_score <- round(
  (
    system_report$coverage_score +
    system_report$metadata_completion +
    system_report$link_score +
    system_report$repository_score +
    system_report$review_score +
    system_report$taxonomy_score
  ) / 6,
  4
)

system_report$system_health_status <- ifelse(
  system_report$system_health_score >= 0.75,
  "ready",
  ifelse(system_report$system_health_score >= 0.55, "developing", "review required")
)

# ------------------------------------------------------------
# Coverage summaries
# ------------------------------------------------------------
cluster_summary <- aggregate(
  slug ~ cluster + status,
  data = content,
  FUN = length
)
names(cluster_summary) <- c("cluster", "status", "content_count")

content_type_summary <- as.data.frame(table(content$content_type), stringsAsFactors = FALSE)
names(content_type_summary) <- c("content_type", "content_count")

article_role_summary <- as.data.frame(table(content$article_role), stringsAsFactors = FALSE)
names(article_role_summary) <- c("article_role", "article_count")

link_type_summary <- as.data.frame(table(links$relationship_type), stringsAsFactors = FALSE)
names(link_type_summary) <- c("relationship_type", "link_count")

# ------------------------------------------------------------
# Governance queue
# ------------------------------------------------------------
governance_queue <- subset(
  system_report,
  system_health_status == "review required" |
    metadata_status == "needs metadata work" |
    link_status == "link review required" |
    repository_status == "review required"
)

governance_queue <- governance_queue[, c(
  "slug",
  "title",
  "status",
  "cluster",
  "metadata_status",
  "link_status",
  "repository_status",
  "system_health_status",
  "review_owner"
)]

# ------------------------------------------------------------
# Catalog export
# ------------------------------------------------------------
catalog <- system_report
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
  "content_type",
  "article_role",
  "metadata_completion",
  "metadata_status",
  "total_link_degree",
  "link_status",
  "repository_score",
  "repository_status",
  "system_health_score",
  "system_health_status",
  "github_path"
)]

# ------------------------------------------------------------
# Write outputs
# ------------------------------------------------------------
write.csv(metadata_report, file.path(tables_dir, "r_digital_knowledge_metadata_readiness.csv"), row.names = FALSE)
write.csv(link_report, file.path(tables_dir, "r_digital_knowledge_link_report.csv"), row.names = FALSE)
write.csv(repository_report, file.path(tables_dir, "r_digital_knowledge_repository_readiness.csv"), row.names = FALSE)
write.csv(taxonomy_report, file.path(tables_dir, "r_digital_knowledge_taxonomy_coverage.csv"), row.names = FALSE)
write.csv(system_report, file.path(tables_dir, "r_digital_knowledge_system_health.csv"), row.names = FALSE)
write.csv(cluster_summary, file.path(tables_dir, "r_digital_knowledge_cluster_summary.csv"), row.names = FALSE)
write.csv(content_type_summary, file.path(tables_dir, "r_digital_knowledge_content_type_summary.csv"), row.names = FALSE)
write.csv(article_role_summary, file.path(tables_dir, "r_digital_knowledge_article_role_summary.csv"), row.names = FALSE)
write.csv(link_type_summary, file.path(tables_dir, "r_digital_knowledge_link_type_summary.csv"), row.names = FALSE)
write.csv(governance_queue, file.path(tables_dir, "r_digital_knowledge_governance_queue.csv"), row.names = FALSE)
write.csv(catalog, file.path(catalog_dir, "r_catalyst_canvas_digital_knowledge_catalog.csv"), row.names = FALSE)

# ------------------------------------------------------------
# Figures
# ------------------------------------------------------------
png(file.path(figures_dir, "r_system_health_by_article.png"), width = 1300, height = 850)
barplot(
  system_report$system_health_score,
  names.arg = system_report$slug,
  las = 2,
  main = "Digital Knowledge System Health by Content Item",
  ylab = "System health score"
)
dev.off()

png(file.path(figures_dir, "r_metadata_completion_by_article.png"), width = 1300, height = 850)
barplot(
  system_report$metadata_completion,
  names.arg = system_report$slug,
  las = 2,
  main = "Metadata Completion by Content Item",
  ylab = "Metadata completion"
)
dev.off()

png(file.path(figures_dir, "r_link_degree_by_article.png"), width = 1300, height = 850)
barplot(
  system_report$total_link_degree,
  names.arg = system_report$slug,
  las = 2,
  main = "Internal-Link Degree by Content Item",
  ylab = "Total link degree"
)
dev.off()

png(file.path(figures_dir, "r_content_type_counts.png"), width = 1000, height = 700)
barplot(
  table(content$content_type),
  main = "Content Type Distribution",
  ylab = "Content count"
)
dev.off()

png(file.path(figures_dir, "r_repository_readiness.png"), width = 1300, height = 850)
barplot(
  repositories$repository_score,
  names.arg = repositories$slug,
  las = 2,
  main = "Repository Readiness by Content Item",
  ylab = "Repository readiness score"
)
dev.off()

# ------------------------------------------------------------
# Markdown report
# ------------------------------------------------------------
report_lines <- c(
  "# Catalyst Canvas Digital Knowledge System Analysis",
  "",
  "Article: Frameworks for Digital Knowledge Systems",
  "",
  "## Summary",
  "",
  paste0("- Content items reviewed: ", nrow(content)),
  paste0("- Internal links reviewed: ", nrow(links)),
  paste0("- Repository records reviewed: ", nrow(repositories)),
  paste0("- Items requiring review: ", nrow(governance_queue)),
  "",
  "## Outputs",
  "",
  "- `r_digital_knowledge_system_health.csv`",
  "- `r_digital_knowledge_metadata_readiness.csv`",
  "- `r_digital_knowledge_link_report.csv`",
  "- `r_digital_knowledge_repository_readiness.csv`",
  "- `r_digital_knowledge_taxonomy_coverage.csv`",
  "- `r_catalyst_canvas_digital_knowledge_catalog.csv`",
  "",
  "These outputs are generated from synthetic data and demonstrate professional-grade digital knowledge-system workflows."
)

writeLines(
  report_lines,
  file.path(reports_dir, "r_catalyst_canvas_digital_knowledge_system_analysis.md")
)

print("Catalyst Canvas R digital knowledge system analysis complete.")
print(system_report[, c("slug", "metadata_status", "link_status", "repository_status", "system_health_status")])
