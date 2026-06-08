# catalyst_canvas_taxonomy_design_analysis.R
# Base R workflow for taxonomy design, category coverage,
# assignment completeness, tag counts, metadata readiness,
# category balance, and editorial governance.

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

articles <- read.csv(file.path(data_dir, "article_inventory.csv"), stringsAsFactors = FALSE)
categories <- read.csv(file.path(data_dir, "taxonomy_categories.csv"), stringsAsFactors = FALSE)
assignments <- read.csv(file.path(data_dir, "taxonomy_assignments.csv"), stringsAsFactors = FALSE)
metadata <- read.csv(file.path(data_dir, "taxonomy_metadata_inventory.csv"), stringsAsFactors = FALSE)

metadata_fields <- c(
  "primary_category",
  "secondary_categories",
  "article_role",
  "reader_stage",
  "governance_owner",
  "last_reviewed",
  "category_definition",
  "boundary_notes"
)

# ------------------------------------------------------------
# Metadata readiness
# ------------------------------------------------------------
metadata_complete <- metadata[, metadata_fields] == "yes"
metadata$completed_fields <- rowSums(metadata_complete)
metadata$required_fields <- length(metadata_fields)
metadata$taxonomy_metadata_completion <- round(metadata$completed_fields / metadata$required_fields, 4)
metadata$taxonomy_metadata_status <- ifelse(
  metadata$taxonomy_metadata_completion >= 0.85,
  "ready",
  "needs taxonomy metadata work"
)

metadata_report <- metadata[, c(
  "slug",
  "title",
  "status",
  "completed_fields",
  "required_fields",
  "taxonomy_metadata_completion",
  "taxonomy_metadata_status"
)]

# ------------------------------------------------------------
# Assignment summaries
# ------------------------------------------------------------
primary_assignments <- subset(assignments, assignment_type == "primary")
secondary_assignments <- subset(assignments, assignment_type == "secondary")
facet_assignments <- subset(assignments, assignment_type == "facet")

primary_counts_by_article <- as.data.frame(table(primary_assignments$slug), stringsAsFactors = FALSE)
names(primary_counts_by_article) <- c("slug", "primary_category_count")

secondary_counts_by_article <- as.data.frame(table(secondary_assignments$slug), stringsAsFactors = FALSE)
names(secondary_counts_by_article) <- c("slug", "secondary_category_count")

facet_counts_by_article <- as.data.frame(table(facet_assignments$slug), stringsAsFactors = FALSE)
names(facet_counts_by_article) <- c("slug", "facet_assignment_count")

article_assignment_report <- merge(
  articles[, c("slug", "title", "status", "article_role", "reader_stage", "tags", "review_owner")],
  primary_counts_by_article,
  by = "slug",
  all.x = TRUE
)

article_assignment_report <- merge(
  article_assignment_report,
  secondary_counts_by_article,
  by = "slug",
  all.x = TRUE
)

article_assignment_report <- merge(
  article_assignment_report,
  facet_counts_by_article,
  by = "slug",
  all.x = TRUE
)

article_assignment_report$primary_category_count[is.na(article_assignment_report$primary_category_count)] <- 0
article_assignment_report$secondary_category_count[is.na(article_assignment_report$secondary_category_count)] <- 0
article_assignment_report$facet_assignment_count[is.na(article_assignment_report$facet_assignment_count)] <- 0

article_assignment_report$tag_count <- sapply(
  strsplit(article_assignment_report$tags, "\\|"),
  function(x) length(x[nchar(trimws(x)) > 0])
)

article_assignment_report$assignment_status <- ifelse(
  article_assignment_report$primary_category_count == 1,
  "ready",
  ifelse(article_assignment_report$primary_category_count == 0, "missing primary category", "multiple primary categories")
)

article_readiness <- merge(
  article_assignment_report,
  metadata_report[, c("slug", "taxonomy_metadata_completion", "taxonomy_metadata_status")],
  by = "slug",
  all.x = TRUE
)

article_readiness$editorial_status <- ifelse(
  article_readiness$status == "published" &
    article_readiness$assignment_status == "ready" &
    article_readiness$taxonomy_metadata_completion >= 0.85 &
    article_readiness$tag_count <= 8,
  "ready",
  ifelse(article_readiness$status == "planned", "planned", "review required")
)

# ------------------------------------------------------------
# Category coverage
# ------------------------------------------------------------
primary_counts_by_category <- as.data.frame(table(primary_assignments$category_id), stringsAsFactors = FALSE)
names(primary_counts_by_category) <- c("category_id", "primary_item_count")

secondary_counts_by_category <- as.data.frame(table(secondary_assignments$category_id), stringsAsFactors = FALSE)
names(secondary_counts_by_category) <- c("category_id", "secondary_item_count")

facet_counts_by_category <- as.data.frame(table(facet_assignments$category_id), stringsAsFactors = FALSE)
names(facet_counts_by_category) <- c("category_id", "facet_item_count")

category_coverage <- merge(categories, primary_counts_by_category, by = "category_id", all.x = TRUE)
category_coverage <- merge(category_coverage, secondary_counts_by_category, by = "category_id", all.x = TRUE)
category_coverage <- merge(category_coverage, facet_counts_by_category, by = "category_id", all.x = TRUE)

category_coverage$primary_item_count[is.na(category_coverage$primary_item_count)] <- 0
category_coverage$secondary_item_count[is.na(category_coverage$secondary_item_count)] <- 0
category_coverage$facet_item_count[is.na(category_coverage$facet_item_count)] <- 0

category_coverage$total_assignment_count <- category_coverage$primary_item_count +
  category_coverage$secondary_item_count +
  category_coverage$facet_item_count

category_coverage$coverage_status <- ifelse(
  category_coverage$status == "deprecated",
  "deprecated",
  ifelse(category_coverage$primary_item_count >= 2, "active", "thin category review")
)

# ------------------------------------------------------------
# Balance and summary statistics
# ------------------------------------------------------------
category_counts <- category_coverage$primary_item_count
mean_count <- mean(category_counts)
sd_count <- sd(category_counts)

taxonomy_balance_score <- ifelse(
  mean_count > 0,
  round(1 - (sd_count / mean_count), 4),
  0
)

article_role_summary <- as.data.frame(table(articles$article_role), stringsAsFactors = FALSE)
names(article_role_summary) <- c("article_role", "article_count")

reader_stage_summary <- as.data.frame(table(articles$reader_stage), stringsAsFactors = FALSE)
names(reader_stage_summary) <- c("reader_stage", "article_count")

category_type_summary <- as.data.frame(table(categories$category_type), stringsAsFactors = FALSE)
names(category_type_summary) <- c("category_type", "category_count")

relationship_summary <- as.data.frame(table(categories$relationship_type), stringsAsFactors = FALSE)
names(relationship_summary) <- c("relationship_type", "category_count")

assignment_type_summary <- as.data.frame(table(assignments$assignment_type), stringsAsFactors = FALSE)
names(assignment_type_summary) <- c("assignment_type", "assignment_count")

# ------------------------------------------------------------
# Governance queue
# ------------------------------------------------------------
governance_queue <- subset(
  article_readiness,
  editorial_status == "review required" |
    assignment_status != "ready" |
    taxonomy_metadata_status == "needs taxonomy metadata work" |
    tag_count > 8
)

governance_queue <- governance_queue[, c(
  "slug",
  "title",
  "status",
  "article_role",
  "reader_stage",
  "primary_category_count",
  "secondary_category_count",
  "facet_assignment_count",
  "tag_count",
  "taxonomy_metadata_status",
  "editorial_status",
  "review_owner"
)]

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
  "status",
  "article_role",
  "reader_stage",
  "primary_category_count",
  "secondary_category_count",
  "facet_assignment_count",
  "tag_count",
  "taxonomy_metadata_completion",
  "taxonomy_metadata_status",
  "editorial_status",
  "github_path"
)]

# ------------------------------------------------------------
# Write outputs
# ------------------------------------------------------------
write.csv(article_readiness, file.path(tables_dir, "r_taxonomy_article_readiness.csv"), row.names = FALSE)
write.csv(category_coverage, file.path(tables_dir, "r_taxonomy_category_coverage.csv"), row.names = FALSE)
write.csv(metadata_report, file.path(tables_dir, "r_taxonomy_metadata_readiness.csv"), row.names = FALSE)
write.csv(article_role_summary, file.path(tables_dir, "r_taxonomy_article_role_summary.csv"), row.names = FALSE)
write.csv(reader_stage_summary, file.path(tables_dir, "r_taxonomy_reader_stage_summary.csv"), row.names = FALSE)
write.csv(category_type_summary, file.path(tables_dir, "r_taxonomy_category_type_summary.csv"), row.names = FALSE)
write.csv(relationship_summary, file.path(tables_dir, "r_taxonomy_relationship_summary.csv"), row.names = FALSE)
write.csv(assignment_type_summary, file.path(tables_dir, "r_taxonomy_assignment_type_summary.csv"), row.names = FALSE)
write.csv(governance_queue, file.path(tables_dir, "r_taxonomy_governance_queue.csv"), row.names = FALSE)
write.csv(catalog, file.path(catalog_dir, "r_catalyst_canvas_taxonomy_catalog.csv"), row.names = FALSE)

# ------------------------------------------------------------
# Figures
# ------------------------------------------------------------
png(file.path(figures_dir, "r_category_primary_item_counts.png"), width = 1200, height = 800)
barplot(
  category_coverage$primary_item_count,
  names.arg = category_coverage$category_name,
  las = 2,
  main = "Primary Item Count by Taxonomy Category",
  ylab = "Primary item count"
)
dev.off()

png(file.path(figures_dir, "r_taxonomy_metadata_completion.png"), width = 1300, height = 850)
barplot(
  article_readiness$taxonomy_metadata_completion,
  names.arg = article_readiness$slug,
  las = 2,
  main = "Taxonomy Metadata Completion by Article",
  ylab = "Taxonomy metadata completion"
)
dev.off()

png(file.path(figures_dir, "r_article_tag_counts.png"), width = 1300, height = 850)
barplot(
  article_readiness$tag_count,
  names.arg = article_readiness$slug,
  las = 2,
  main = "Tag Count by Article",
  ylab = "Tag count"
)
dev.off()

png(file.path(figures_dir, "r_assignment_type_counts.png"), width = 1000, height = 700)
barplot(
  table(assignments$assignment_type),
  main = "Taxonomy Assignment Types",
  ylab = "Assignment count"
)
dev.off()

# ------------------------------------------------------------
# Markdown report
# ------------------------------------------------------------
report_lines <- c(
  "# Catalyst Canvas Taxonomy Design Analysis",
  "",
  "Article: Taxonomy Design for Content Frameworks",
  "",
  "## Summary",
  "",
  paste0("- Articles reviewed: ", nrow(articles)),
  paste0("- Categories reviewed: ", nrow(categories)),
  paste0("- Assignments reviewed: ", nrow(assignments)),
  paste0("- Taxonomy balance score: ", taxonomy_balance_score),
  paste0("- Articles requiring review: ", nrow(governance_queue)),
  "",
  "## Outputs",
  "",
  "- `r_taxonomy_article_readiness.csv`",
  "- `r_taxonomy_category_coverage.csv`",
  "- `r_taxonomy_metadata_readiness.csv`",
  "- `r_taxonomy_governance_queue.csv`",
  "- `r_catalyst_canvas_taxonomy_catalog.csv`",
  "",
  "These outputs are generated from synthetic data and demonstrate professional-grade taxonomy design workflows."
)

writeLines(
  report_lines,
  file.path(reports_dir, "r_catalyst_canvas_taxonomy_design_analysis.md")
)

print("Catalyst Canvas R taxonomy design analysis complete.")
print(category_coverage[, c("category_id", "category_name", "primary_item_count", "coverage_status")])
print(article_readiness[, c("slug", "assignment_status", "taxonomy_metadata_status", "editorial_status")])
