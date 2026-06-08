# catalyst_canvas_content_audit_analysis.R
# Professional base R workflow for content audits and framework governance.
# Designed as a Catalyst Canvas-style editorial diagnostics scaffold.

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
links <- read.csv(file.path(data_dir, "internal_links.csv"), stringsAsFactors = FALSE)
evidence <- read.csv(file.path(data_dir, "evidence_register.csv"), stringsAsFactors = FALSE)
review_queue <- read.csv(file.path(data_dir, "editorial_review_queue.csv"), stringsAsFactors = FALSE)
taxonomy <- read.csv(file.path(data_dir, "taxonomy_categories.csv"), stringsAsFactors = FALSE)

metadata_fields <- c(
  "excerpt",
  "tags",
  "github_url",
  "image_alt",
  "references",
  "last_reviewed",
  "series_context",
  "footer_navigation",
  "repository_manifest",
  "accessibility_notes"
)

# ------------------------------------------------------------
# Coverage summary
# ------------------------------------------------------------
coverage <- aggregate(
  slug ~ cluster + status,
  data = content,
  FUN = length
)

names(coverage) <- c("cluster", "status", "article_count")

cluster_totals <- aggregate(
  slug ~ cluster,
  data = content,
  FUN = length
)

names(cluster_totals) <- c("cluster", "total_articles")

published <- subset(coverage, status == "published")
names(published)[names(published) == "article_count"] <- "published_articles"

coverage_readiness <- merge(
  cluster_totals,
  published[, c("cluster", "published_articles")],
  by = "cluster",
  all.x = TRUE
)

coverage_readiness$published_articles[is.na(coverage_readiness$published_articles)] <- 0
coverage_readiness$coverage_rate <- round(
  coverage_readiness$published_articles / coverage_readiness$total_articles,
  4
)

coverage_readiness$coverage_status <- ifelse(
  coverage_readiness$coverage_rate >= 0.60,
  "healthy",
  "needs development"
)

# ------------------------------------------------------------
# Metadata readiness
# ------------------------------------------------------------
metadata_complete <- content[, metadata_fields] == "yes"
content$completed_metadata_fields <- rowSums(metadata_complete)
content$required_metadata_fields <- length(metadata_fields)
content$metadata_completion_rate <- round(
  content$completed_metadata_fields / content$required_metadata_fields,
  4
)

content$metadata_status <- ifelse(
  content$metadata_completion_rate >= 0.85,
  "ready",
  "needs metadata work"
)

metadata_report <- content[, c(
  "slug",
  "title",
  "status",
  "cluster",
  "completed_metadata_fields",
  "required_metadata_fields",
  "metadata_completion_rate",
  "metadata_status"
)]

# ------------------------------------------------------------
# Link health
# ------------------------------------------------------------
incoming <- as.data.frame(table(links$target_slug), stringsAsFactors = FALSE)
names(incoming) <- c("slug", "incoming_links")

outgoing <- as.data.frame(table(links$source_slug), stringsAsFactors = FALSE)
names(outgoing) <- c("slug", "outgoing_links")

link_health <- merge(content[, c("slug", "title", "status", "cluster")], incoming, by = "slug", all.x = TRUE)
link_health <- merge(link_health, outgoing, by = "slug", all.x = TRUE)

link_health$incoming_links[is.na(link_health$incoming_links)] <- 0
link_health$outgoing_links[is.na(link_health$outgoing_links)] <- 0
link_health$total_link_degree <- link_health$incoming_links + link_health$outgoing_links

link_health$network_role <- ifelse(
  link_health$total_link_degree >= 8,
  "hub",
  ifelse(
    link_health$total_link_degree >= 5,
    "bridge",
    ifelse(
      link_health$total_link_degree >= 3,
      "connector",
      ifelse(link_health$total_link_degree >= 1, "thinly linked", "orphaned")
    )
  )
)

link_health$link_status <- ifelse(
  link_health$status == "published" & link_health$total_link_degree < 3,
  "review",
  "acceptable"
)

link_health$link_score <- pmin(link_health$total_link_degree / 6, 1)

# ------------------------------------------------------------
# Evidence readiness
# ------------------------------------------------------------
evidence_count <- as.data.frame(table(evidence$slug), stringsAsFactors = FALSE)
names(evidence_count) <- c("slug", "evidence_records")

high_authority <- subset(evidence, authority_level == "high")
high_authority_count <- as.data.frame(table(high_authority$slug), stringsAsFactors = FALSE)
names(high_authority_count) <- c("slug", "high_authority_sources")

ready_evidence <- subset(evidence, review_status == "ready")
ready_evidence_count <- as.data.frame(table(ready_evidence$slug), stringsAsFactors = FALSE)
names(ready_evidence_count) <- c("slug", "ready_evidence_records")

evidence_report <- content[, c("slug", "title", "status", "cluster", "references", "evidence_notes", "limitations")]
evidence_report <- merge(evidence_report, evidence_count, by = "slug", all.x = TRUE)
evidence_report <- merge(evidence_report, high_authority_count, by = "slug", all.x = TRUE)
evidence_report <- merge(evidence_report, ready_evidence_count, by = "slug", all.x = TRUE)

evidence_report$evidence_records[is.na(evidence_report$evidence_records)] <- 0
evidence_report$high_authority_sources[is.na(evidence_report$high_authority_sources)] <- 0
evidence_report$ready_evidence_records[is.na(evidence_report$ready_evidence_records)] <- 0

evidence_report$field_score <- (
  (evidence_report$references == "yes") +
    (evidence_report$evidence_notes == "yes") +
    (evidence_report$limitations == "yes")
) / 3

evidence_report$register_support <- pmin(evidence_report$evidence_records / 3, 1)
evidence_report$authority_support <- pmin(evidence_report$high_authority_sources / 2, 1)
evidence_report$readiness_support <- ifelse(
  evidence_report$evidence_records > 0,
  pmin(evidence_report$ready_evidence_records / evidence_report$evidence_records, 1),
  0
)

evidence_report$evidence_readiness_score <- round(
  0.40 * evidence_report$field_score +
    0.25 * evidence_report$register_support +
    0.20 * evidence_report$authority_support +
    0.15 * evidence_report$readiness_support,
  4
)

evidence_report$evidence_status <- ifelse(
  evidence_report$evidence_readiness_score >= 0.67,
  "ready",
  "needs evidence review"
)

# ------------------------------------------------------------
# Freshness
# ------------------------------------------------------------
today <- Sys.Date()
content$last_reviewed_parsed <- as.Date(content$last_reviewed_date)
content$content_age_days <- as.numeric(today - content$last_reviewed_parsed)
content$content_age_days[is.na(content$content_age_days)] <- 9999

content$freshness_score <- pmax(
  0,
  pmin(1, 1 - (content$content_age_days / content$review_cycle_days))
)

content$freshness_status <- ifelse(
  content$content_age_days <= content$review_cycle_days,
  "fresh",
  "review overdue"
)

freshness_report <- content[, c(
  "slug",
  "title",
  "status",
  "article_type",
  "last_reviewed_date",
  "review_cycle_days",
  "content_age_days",
  "freshness_score",
  "freshness_status"
)]

# ------------------------------------------------------------
# Accessibility readiness
# ------------------------------------------------------------
content$accessibility_readiness_score <- round(
  (
    (content$image_alt == "yes") +
      (content$accessibility_notes == "yes") +
      (content$footer_navigation == "yes") +
      (content$series_context == "yes")
  ) / 4,
  4
)

content$accessibility_status <- ifelse(
  content$accessibility_readiness_score >= 0.75,
  "ready",
  "needs accessibility review"
)

accessibility_report <- content[, c(
  "slug",
  "title",
  "status",
  "accessibility_readiness_score",
  "accessibility_status"
)]

# ------------------------------------------------------------
# Taxonomy coverage
# ------------------------------------------------------------
taxonomy_counts <- as.data.frame(table(content$cluster), stringsAsFactors = FALSE)
names(taxonomy_counts) <- c("category", "article_count")

taxonomy_report <- merge(taxonomy, taxonomy_counts, by = "category", all.x = TRUE)
taxonomy_report$article_count[is.na(taxonomy_report$article_count)] <- 0
taxonomy_report$taxonomy_status <- ifelse(taxonomy_report$article_count > 0, "active", "missing from sample")

# ------------------------------------------------------------
# Framework health
# ------------------------------------------------------------
health <- merge(
  metadata_report[, c("slug", "metadata_completion_rate")],
  link_health[, c("slug", "link_score")],
  by = "slug",
  all.x = TRUE
)

health <- merge(
  health,
  evidence_report[, c("slug", "evidence_readiness_score")],
  by = "slug",
  all.x = TRUE
)

health <- merge(
  health,
  freshness_report[, c("slug", "freshness_score")],
  by = "slug",
  all.x = TRUE
)

health <- merge(
  health,
  accessibility_report[, c("slug", "accessibility_readiness_score")],
  by = "slug",
  all.x = TRUE
)

health <- merge(
  health,
  content[, c("slug", "title", "status", "cluster", "article_type", "governance_notes", "duplicate_risk")],
  by = "slug",
  all.x = TRUE
)

health$governance_score <- ifelse(
  health$governance_notes == "yes",
  1,
  ifelse(health$status == "published", 0.5, 0.25)
)

health$framework_health_score <- round(
  0.20 * health$metadata_completion_rate +
    0.18 * health$link_score +
    0.20 * health$evidence_readiness_score +
    0.17 * health$freshness_score +
    0.15 * health$governance_score +
    0.10 * health$accessibility_readiness_score,
  4
)

health$health_status <- ifelse(
  health$framework_health_score >= 0.78,
  "ready",
  "governance review"
)

# ------------------------------------------------------------
# Governance queue
# ------------------------------------------------------------
automated_queue <- subset(
  health,
  health_status == "governance review" | duplicate_risk %in% c("medium", "high")
)

automated_queue <- automated_queue[
  order(automated_queue$framework_health_score, automated_queue$cluster),
]

# ------------------------------------------------------------
# Catalog export
# ------------------------------------------------------------
catalog <- health[, c(
  "slug",
  "title",
  "status",
  "cluster",
  "article_type",
  "framework_health_score",
  "health_status",
  "duplicate_risk"
)]

catalog$catalog_product <- "Catalyst Canvas"
catalog$series <- "Content Frameworks"
catalog$github_path <- paste0("articles/", catalog$slug, "/")

catalog <- catalog[, c(
  "catalog_product",
  "series",
  "slug",
  "title",
  "status",
  "cluster",
  "article_type",
  "framework_health_score",
  "health_status",
  "duplicate_risk",
  "github_path"
)]

# ------------------------------------------------------------
# Write tables
# ------------------------------------------------------------
write.csv(coverage, file.path(tables_dir, "r_coverage_status_summary.csv"), row.names = FALSE)
write.csv(coverage_readiness, file.path(tables_dir, "r_cluster_coverage_readiness.csv"), row.names = FALSE)
write.csv(metadata_report, file.path(tables_dir, "r_metadata_readiness_report.csv"), row.names = FALSE)
write.csv(link_health, file.path(tables_dir, "r_internal_link_health_report.csv"), row.names = FALSE)
write.csv(evidence_report, file.path(tables_dir, "r_evidence_readiness_report.csv"), row.names = FALSE)
write.csv(freshness_report, file.path(tables_dir, "r_freshness_review_report.csv"), row.names = FALSE)
write.csv(accessibility_report, file.path(tables_dir, "r_accessibility_readiness_report.csv"), row.names = FALSE)
write.csv(taxonomy_report, file.path(tables_dir, "r_taxonomy_coverage_report.csv"), row.names = FALSE)
write.csv(health, file.path(tables_dir, "r_framework_health_report.csv"), row.names = FALSE)
write.csv(automated_queue, file.path(tables_dir, "r_governance_review_queue.csv"), row.names = FALSE)
write.csv(catalog, file.path(catalog_dir, "r_catalyst_canvas_content_audit_catalog.csv"), row.names = FALSE)

# ------------------------------------------------------------
# Figures
# ------------------------------------------------------------
png(file.path(figures_dir, "r_framework_health_scores.png"), width = 1300, height = 850)
barplot(
  health$framework_health_score,
  names.arg = health$slug,
  las = 2,
  main = "Framework Health Score by Article",
  ylab = "Health score"
)
dev.off()

png(file.path(figures_dir, "r_cluster_coverage_rates.png"), width = 1100, height = 750)
barplot(
  coverage_readiness$coverage_rate,
  names.arg = coverage_readiness$cluster,
  las = 2,
  main = "Published Coverage Rate by Cluster",
  ylab = "Coverage rate"
)
dev.off()

png(file.path(figures_dir, "r_metadata_completion_rates.png"), width = 1300, height = 850)
barplot(
  metadata_report$metadata_completion_rate,
  names.arg = metadata_report$slug,
  las = 2,
  main = "Metadata Completion Rate by Article",
  ylab = "Completion rate"
)
dev.off()

png(file.path(figures_dir, "r_internal_link_health_scores.png"), width = 1300, height = 850)
barplot(
  link_health$link_score,
  names.arg = link_health$slug,
  las = 2,
  main = "Internal Link Health Score by Article",
  ylab = "Link score"
)
dev.off()

# ------------------------------------------------------------
# Markdown report
# ------------------------------------------------------------
summary_lines <- c(
  "# Catalyst Canvas Content Audit and Governance Analysis",
  "",
  "Article: Content Audits and Framework Governance",
  "",
  "## Summary",
  "",
  paste0("- Article records: ", nrow(content)),
  paste0("- Internal-link records: ", nrow(links)),
  paste0("- Evidence records: ", nrow(evidence)),
  paste0("- Manual review queue items: ", nrow(review_queue)),
  paste0("- Automated governance review items: ", nrow(automated_queue)),
  "",
  "## Generated outputs",
  "",
  "- `r_coverage_status_summary.csv`",
  "- `r_cluster_coverage_readiness.csv`",
  "- `r_metadata_readiness_report.csv`",
  "- `r_internal_link_health_report.csv`",
  "- `r_evidence_readiness_report.csv`",
  "- `r_freshness_review_report.csv`",
  "- `r_accessibility_readiness_report.csv`",
  "- `r_framework_health_report.csv`",
  "- `r_governance_review_queue.csv`",
  "- `r_catalyst_canvas_content_audit_catalog.csv`",
  "",
  "These outputs support professional content audits and framework governance review."
)

writeLines(
  summary_lines,
  file.path(reports_dir, "r_content_audit_governance_report.md")
)

print("Catalyst Canvas R content audit complete.")
print(coverage_readiness)
print(health)
