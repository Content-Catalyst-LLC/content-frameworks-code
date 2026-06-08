# editorial_metadata_content_system_analysis.R
# Professional base R workflow for metadata readiness and governance reporting.

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

metadata <- read.csv(file.path(data_dir, "editorial_metadata_inventory.csv"), stringsAsFactors = FALSE)
images <- read.csv(file.path(data_dir, "image_metadata_inventory.csv"), stringsAsFactors = FALSE)
references <- read.csv(file.path(data_dir, "reference_metadata.csv"), stringsAsFactors = FALSE)
repository_manifest <- read.csv(file.path(data_dir, "repository_manifest.csv"), stringsAsFactors = FALSE)
review_queue <- read.csv(file.path(data_dir, "editorial_review_queue.csv"), stringsAsFactors = FALSE)

required_fields <- c(
  "title",
  "seo_title",
  "slug",
  "series",
  "cluster",
  "article_type",
  "status",
  "description",
  "excerpt",
  "tags",
  "image_title",
  "image_filename",
  "alt_text",
  "caption",
  "image_description",
  "references",
  "repository_url",
  "repository_path",
  "previous_title",
  "previous_url",
  "article_map_title",
  "article_map_url",
  "next_title",
  "next_url",
  "last_reviewed"
)

completed_matrix <- metadata[, required_fields] != "" &
  metadata[, required_fields] != "no" &
  metadata[, required_fields] != "pending"

metadata$completed_fields <- rowSums(completed_matrix)
metadata$required_fields <- length(required_fields)
metadata$metadata_completion_rate <- round(metadata$completed_fields / metadata$required_fields, 4)

metadata$metadata_status <- ifelse(
  metadata$metadata_completion_rate >= 0.90,
  "ready",
  "needs metadata work"
)

# ------------------------------------------------------------
# Cluster readiness
# ------------------------------------------------------------
cluster_readiness <- aggregate(
  metadata_completion_rate ~ cluster,
  data = metadata,
  FUN = mean
)

names(cluster_readiness) <- c("cluster", "average_metadata_completion_rate")
cluster_readiness$average_metadata_completion_rate <- round(cluster_readiness$average_metadata_completion_rate, 4)

cluster_counts <- aggregate(slug ~ cluster, data = metadata, FUN = length)
names(cluster_counts) <- c("cluster", "article_count")

published_counts <- aggregate(
  slug ~ cluster,
  data = subset(metadata, status == "published"),
  FUN = length
)

names(published_counts) <- c("cluster", "published_count")

cluster_report <- merge(cluster_counts, cluster_readiness, by = "cluster", all.x = TRUE)
cluster_report <- merge(cluster_report, published_counts, by = "cluster", all.x = TRUE)
cluster_report$published_count[is.na(cluster_report$published_count)] <- 0
cluster_report$published_coverage_rate <- round(cluster_report$published_count / cluster_report$article_count, 4)

cluster_report$cluster_status <- ifelse(
  cluster_report$average_metadata_completion_rate >= 0.90,
  "ready",
  "review"
)

# ------------------------------------------------------------
# Status and article-type summaries
# ------------------------------------------------------------
status_summary <- as.data.frame(table(metadata$status), stringsAsFactors = FALSE)
names(status_summary) <- c("status", "article_count")

type_summary <- as.data.frame(table(metadata$article_type), stringsAsFactors = FALSE)
names(type_summary) <- c("article_type", "article_count")

# ------------------------------------------------------------
# Repository alignment
# ------------------------------------------------------------
metadata$expected_repository_path <- paste0("articles/", metadata$slug, "/")
metadata$repository_path_aligned <- metadata$repository_path == metadata$expected_repository_path

repository_report <- metadata[, c(
  "slug",
  "repository_url",
  "repository_path",
  "expected_repository_path",
  "repository_path_aligned"
)]

# ------------------------------------------------------------
# Footer navigation review
# ------------------------------------------------------------
metadata_ordered <- metadata[order(metadata$article_order), ]
metadata_ordered$expected_previous_title <- c(
  "Series Start",
  metadata_ordered$title[-nrow(metadata_ordered)]
)

metadata_ordered$expected_next_title <- c(
  metadata_ordered$title[-1],
  "Series End"
)

metadata_ordered$expected_previous_url <- c(
  "",
  paste0("/", metadata_ordered$slug[-nrow(metadata_ordered)], "/")
)

metadata_ordered$expected_next_url <- c(
  paste0("/", metadata_ordered$slug[-1], "/"),
  ""
)

metadata_ordered$previous_valid <- metadata_ordered$previous_title == metadata_ordered$expected_previous_title
metadata_ordered$next_valid <- metadata_ordered$next_title == metadata_ordered$expected_next_title
metadata_ordered$previous_url_valid <- metadata_ordered$previous_url == metadata_ordered$expected_previous_url
metadata_ordered$next_url_valid <- metadata_ordered$next_url == metadata_ordered$expected_next_url
metadata_ordered$article_map_valid <- metadata_ordered$article_map_url == "/content-frameworks/"

footer_report <- metadata_ordered[, c(
  "slug",
  "previous_title",
  "expected_previous_title",
  "previous_valid",
  "previous_url",
  "expected_previous_url",
  "previous_url_valid",
  "next_title",
  "expected_next_title",
  "next_valid",
  "next_url",
  "expected_next_url",
  "next_url_valid",
  "article_map_url",
  "article_map_valid"
)]

# ------------------------------------------------------------
# Image readiness
# ------------------------------------------------------------
image_fields <- c("image_title", "image_filename", "alt_text", "caption", "image_description")
images$image_completed_fields <- rowSums(images[, image_fields] != "" & images[, image_fields] != "pending")
images$image_required_fields <- length(image_fields)
images$image_metadata_score <- round(images$image_completed_fields / images$image_required_fields, 4)
images$image_metadata_status <- ifelse(images$image_metadata_score >= 0.80 & images$review_status == "ready", "ready", "review")

# ------------------------------------------------------------
# Reference metadata readiness
# ------------------------------------------------------------
reference_count <- as.data.frame(table(references$slug), stringsAsFactors = FALSE)
names(reference_count) <- c("slug", "reference_records")

high_authority <- subset(references, authority_level == "high")
high_authority_count <- as.data.frame(table(high_authority$slug), stringsAsFactors = FALSE)
names(high_authority_count) <- c("slug", "high_authority_sources")

ready_refs <- subset(references, review_status == "ready")
ready_ref_count <- as.data.frame(table(ready_refs$slug), stringsAsFactors = FALSE)
names(ready_ref_count) <- c("slug", "ready_reference_records")

reference_report <- merge(metadata[, c("slug", "title", "status")], reference_count, by = "slug", all.x = TRUE)
reference_report <- merge(reference_report, high_authority_count, by = "slug", all.x = TRUE)
reference_report <- merge(reference_report, ready_ref_count, by = "slug", all.x = TRUE)

reference_report$reference_records[is.na(reference_report$reference_records)] <- 0
reference_report$high_authority_sources[is.na(reference_report$high_authority_sources)] <- 0
reference_report$ready_reference_records[is.na(reference_report$ready_reference_records)] <- 0

reference_report$reference_readiness_score <- round(
  pmin(reference_report$reference_records / 3, 1) * 0.35 +
    pmin(reference_report$high_authority_sources / 2, 1) * 0.35 +
    ifelse(reference_report$reference_records > 0, reference_report$ready_reference_records / reference_report$reference_records, 0) * 0.30,
  4
)

reference_report$reference_status <- ifelse(
  reference_report$reference_readiness_score >= 0.67,
  "ready",
  "needs reference metadata review"
)

# ------------------------------------------------------------
# Repository manifest readiness
# ------------------------------------------------------------
manifest_fields <- c(
  "required_folders_present",
  "readme_present",
  "python_workflow_present",
  "r_workflow_present",
  "sql_schema_present",
  "outputs_present"
)

repository_manifest$manifest_completed_fields <- rowSums(repository_manifest[, manifest_fields] == "yes")
repository_manifest$manifest_required_fields <- length(manifest_fields)
repository_manifest$repository_manifest_score <- round(
  repository_manifest$manifest_completed_fields / repository_manifest$manifest_required_fields,
  4
)

repository_manifest$repository_workflow_ready <- repository_manifest$repository_manifest_score >= 0.80 &
  repository_manifest$manifest_status == "ready"

# ------------------------------------------------------------
# Freshness
# ------------------------------------------------------------
review_cycles <- data.frame(
  article_type = c("foundational", "methodological", "technical", "governance", "strategic", "critical", "capstone"),
  review_cycle_days = c(730, 365, 180, 180, 365, 365, 365),
  stringsAsFactors = FALSE
)

freshness <- merge(metadata[, c("slug", "title", "status", "article_type", "last_reviewed")], review_cycles, by = "article_type", all.x = TRUE)
freshness$last_reviewed_parsed <- as.Date(freshness$last_reviewed)
freshness$content_age_days <- as.numeric(Sys.Date() - freshness$last_reviewed_parsed)
freshness$content_age_days[is.na(freshness$content_age_days)] <- 9999
freshness$freshness_score <- round(pmax(0, pmin(1, 1 - (freshness$content_age_days / freshness$review_cycle_days))), 4)
freshness$freshness_status <- ifelse(freshness$content_age_days <= freshness$review_cycle_days, "fresh", "review overdue")

# ------------------------------------------------------------
# Governance queue
# ------------------------------------------------------------
metadata_queue <- subset(metadata, metadata_status == "needs metadata work" | repository_path_aligned == FALSE)
footer_queue <- subset(footer_report, previous_valid == FALSE | next_valid == FALSE | previous_url_valid == FALSE | next_url_valid == FALSE | article_map_valid == FALSE)

metadata_queue$queue_reason <- "metadata or repository alignment"
footer_queue$queue_reason <- "footer navigation mismatch"

# ------------------------------------------------------------
# Catalog export
# ------------------------------------------------------------
catalog <- metadata[, c(
  "series",
  "slug",
  "title",
  "cluster",
  "article_type",
  "status",
  "metadata_completion_rate",
  "metadata_status",
  "repository_path",
  "article_map_url"
)]

# ------------------------------------------------------------
# Write outputs
# ------------------------------------------------------------
write.csv(
  metadata[, c(
    "slug",
    "title",
    "status",
    "cluster",
    "article_type",
    "completed_fields",
    "required_fields",
    "metadata_completion_rate",
    "metadata_status"
  )],
  file.path(tables_dir, "r_metadata_readiness_report.csv"),
  row.names = FALSE
)

write.csv(cluster_report, file.path(tables_dir, "r_cluster_metadata_readiness.csv"), row.names = FALSE)
write.csv(status_summary, file.path(tables_dir, "r_status_summary.csv"), row.names = FALSE)
write.csv(type_summary, file.path(tables_dir, "r_article_type_summary.csv"), row.names = FALSE)
write.csv(repository_report, file.path(tables_dir, "r_repository_alignment_report.csv"), row.names = FALSE)
write.csv(footer_report, file.path(tables_dir, "r_footer_navigation_validation.csv"), row.names = FALSE)
write.csv(images, file.path(tables_dir, "r_image_metadata_report.csv"), row.names = FALSE)
write.csv(reference_report, file.path(tables_dir, "r_reference_metadata_report.csv"), row.names = FALSE)
write.csv(repository_manifest, file.path(tables_dir, "r_repository_manifest_report.csv"), row.names = FALSE)
write.csv(freshness, file.path(tables_dir, "r_review_cycle_report.csv"), row.names = FALSE)
write.csv(metadata_queue, file.path(tables_dir, "r_metadata_governance_queue.csv"), row.names = FALSE)
write.csv(footer_queue, file.path(tables_dir, "r_footer_governance_queue.csv"), row.names = FALSE)
write.csv(catalog, file.path(catalog_dir, "r_editorial_metadata_catalog_export.csv"), row.names = FALSE)

# ------------------------------------------------------------
# Figures
# ------------------------------------------------------------
png(file.path(figures_dir, "r_metadata_completion_by_article.png"), width = 1300, height = 850)
barplot(
  metadata$metadata_completion_rate,
  names.arg = metadata$slug,
  las = 2,
  main = "Metadata Completion Rate by Article",
  ylab = "Completion rate"
)
dev.off()

png(file.path(figures_dir, "r_cluster_metadata_readiness.png"), width = 1100, height = 750)
barplot(
  cluster_report$average_metadata_completion_rate,
  names.arg = cluster_report$cluster,
  las = 2,
  main = "Average Metadata Completion by Cluster",
  ylab = "Average completion rate"
)
dev.off()

png(file.path(figures_dir, "r_status_distribution.png"), width = 1000, height = 700)
barplot(
  status_summary$article_count,
  names.arg = status_summary$status,
  main = "Article Status Distribution",
  ylab = "Article count"
)
dev.off()

png(file.path(figures_dir, "r_reference_readiness.png"), width = 1200, height = 800)
barplot(
  reference_report$reference_readiness_score,
  names.arg = reference_report$slug,
  las = 2,
  main = "Reference Metadata Readiness",
  ylab = "Readiness score"
)
dev.off()

# ------------------------------------------------------------
# Markdown report
# ------------------------------------------------------------
summary_lines <- c(
  "# Editorial Metadata and Content Systems: R Audit",
  "",
  "## Summary",
  "",
  paste0("- Metadata records: ", nrow(metadata)),
  paste0("- Manual review queue records: ", nrow(review_queue)),
  paste0("- Metadata governance queue records: ", nrow(metadata_queue)),
  paste0("- Footer governance queue records: ", nrow(footer_queue)),
  paste0("- Average completion rate: ", round(mean(metadata$metadata_completion_rate), 4)),
  "",
  "## Generated outputs",
  "",
  "- `r_metadata_readiness_report.csv`",
  "- `r_cluster_metadata_readiness.csv`",
  "- `r_status_summary.csv`",
  "- `r_article_type_summary.csv`",
  "- `r_repository_alignment_report.csv`",
  "- `r_footer_navigation_validation.csv`",
  "- `r_image_metadata_report.csv`",
  "- `r_reference_metadata_report.csv`",
  "- `r_repository_manifest_report.csv`",
  "- `r_review_cycle_report.csv`",
  "- `r_metadata_governance_queue.csv`",
  "- `r_editorial_metadata_catalog_export.csv`",
  "",
  "These outputs support editorial metadata governance and content-system maintenance."
)

writeLines(
  summary_lines,
  file.path(reports_dir, "r_editorial_metadata_content_system_report.md")
)

print("Editorial metadata content-system R audit complete.")
print(cluster_report)
print(status_summary)
