# catalyst_canvas_structure_type_analysis.R
# Base R workflow for frameworks, templates, models, methods,
# workflows, structure classification, governance readiness,
# risk summaries, and catalog exports.

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

structures <- read.csv(file.path(data_dir, "content_structure_inventory.csv"), stringsAsFactors = FALSE)
article_map <- read.csv(file.path(data_dir, "content_framework_article_map.csv"), stringsAsFactors = FALSE)
metadata <- read.csv(file.path(data_dir, "metadata_inventory.csv"), stringsAsFactors = FALSE)
links <- read.csv(file.path(data_dir, "internal_links.csv"), stringsAsFactors = FALSE)
taxonomy <- read.csv(file.path(data_dir, "taxonomy_categories.csv"), stringsAsFactors = FALSE)
misuse_cases <- read.csv(file.path(data_dir, "structure_misuse_cases.csv"), stringsAsFactors = FALSE)

governance_fields <- c(
  "purpose_documented",
  "use_conditions_documented",
  "limitations_documented",
  "evidence_alignment_reviewed",
  "ethical_risk_reviewed",
  "owner_assigned",
  "review_cycle_defined"
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
# Structure scoring
# ------------------------------------------------------------
structures$framework_signal <- structures$organizes_reasoning + structures$defines_categories + structures$supports_interpretation
structures$template_signal <- structures$standardizes_fields + structures$standardizes_format + structures$repeatable_output
structures$model_signal <- structures$represents_relationships + structures$uses_assumptions + structures$explains_mechanism
structures$method_signal <- structures$defines_steps + structures$supports_repeatable_process + structures$produces_decision_rules
structures$workflow_signal <- structures$coordinates_handoffs + structures$tracks_status + structures$assigns_responsibility

signal_matrix <- structures[, c(
  "framework_signal",
  "template_signal",
  "model_signal",
  "method_signal",
  "workflow_signal"
)]

signal_names <- c("framework", "template", "model", "method", "workflow")
structures$inferred_type <- signal_names[max.col(signal_matrix, ties.method = "first")]
structures$type_match <- structures$declared_type == structures$observed_type
structures$inferred_match <- structures$inferred_type == structures$observed_type

governance_matrix <- structures[, governance_fields] == "yes"
structures$governance_completion <- round(rowSums(governance_matrix) / length(governance_fields), 4)

structures$review_status <- ifelse(
  structures$type_match == FALSE,
  "declared type mismatch",
  ifelse(
    structures$governance_completion < 0.85,
    "governance incomplete",
    ifelse(structures$risk_severity %in% c("high", "medium"), "risk review required", "ready for managed use")
  )
)

structure_report <- structures[, c(
  "structure_id",
  "structure_name",
  "declared_type",
  "observed_type",
  "inferred_type",
  "type_match",
  "inferred_match",
  "governance_completion",
  "review_status",
  "risk_severity",
  "risk_note",
  "framework_signal",
  "template_signal",
  "model_signal",
  "method_signal",
  "workflow_signal"
)]

observed_type_summary <- as.data.frame(table(structures$observed_type), stringsAsFactors = FALSE)
names(observed_type_summary) <- c("observed_type", "structure_count")

declared_type_summary <- as.data.frame(table(structures$declared_type), stringsAsFactors = FALSE)
names(declared_type_summary) <- c("declared_type", "structure_count")

risk_summary <- as.data.frame(table(structures$risk_severity), stringsAsFactors = FALSE)
names(risk_summary) <- c("risk_severity", "structure_count")

review_summary <- as.data.frame(table(structures$review_status), stringsAsFactors = FALSE)
names(review_summary) <- c("review_status", "structure_count")

governance_by_type <- aggregate(
  governance_completion ~ observed_type,
  data = structures,
  FUN = mean
)
names(governance_by_type) <- c("observed_type", "average_governance_completion")
governance_by_type$average_governance_completion <- round(governance_by_type$average_governance_completion, 4)

mismatch_report <- subset(
  structures,
  type_match == FALSE,
  select = c(
    "structure_id",
    "structure_name",
    "declared_type",
    "observed_type",
    "inferred_type",
    "risk_severity",
    "risk_note"
  )
)

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
# Coverage and link diagnostics
# ------------------------------------------------------------
coverage <- aggregate(
  title ~ cluster + status,
  data = article_map,
  FUN = length
)
names(coverage) <- c("cluster", "status", "article_count")

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

taxonomy_counts <- as.data.frame(table(article_map$cluster), stringsAsFactors = FALSE)
names(taxonomy_counts) <- c("category", "article_count")

taxonomy_report <- merge(taxonomy, taxonomy_counts, by = "category", all.x = TRUE)
taxonomy_report$article_count[is.na(taxonomy_report$article_count)] <- 0
taxonomy_report$taxonomy_status <- ifelse(taxonomy_report$article_count > 0, "active", "missing from sample")

# ------------------------------------------------------------
# Catalog export
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
write.csv(structure_report, file.path(tables_dir, "r_structure_classification_report.csv"), row.names = FALSE)
write.csv(observed_type_summary, file.path(tables_dir, "r_observed_structure_type_summary.csv"), row.names = FALSE)
write.csv(declared_type_summary, file.path(tables_dir, "r_declared_structure_type_summary.csv"), row.names = FALSE)
write.csv(risk_summary, file.path(tables_dir, "r_structure_risk_summary.csv"), row.names = FALSE)
write.csv(review_summary, file.path(tables_dir, "r_structure_review_summary.csv"), row.names = FALSE)
write.csv(governance_by_type, file.path(tables_dir, "r_governance_by_structure_type.csv"), row.names = FALSE)
write.csv(mismatch_report, file.path(tables_dir, "r_structure_type_mismatch_report.csv"), row.names = FALSE)
write.csv(metadata_report, file.path(tables_dir, "r_metadata_structure_readiness.csv"), row.names = FALSE)
write.csv(coverage, file.path(tables_dir, "r_article_map_coverage.csv"), row.names = FALSE)
write.csv(link_report, file.path(tables_dir, "r_internal_link_structure_report.csv"), row.names = FALSE)
write.csv(taxonomy_report, file.path(tables_dir, "r_taxonomy_structure_coverage.csv"), row.names = FALSE)
write.csv(misuse_cases, file.path(tables_dir, "r_structure_misuse_cases.csv"), row.names = FALSE)
write.csv(catalog, file.path(catalog_dir, "r_catalyst_canvas_structure_catalog.csv"), row.names = FALSE)

# ------------------------------------------------------------
# Figures
# ------------------------------------------------------------
png(file.path(figures_dir, "r_observed_structure_type_counts.png"), width = 1100, height = 750)
barplot(
  table(structures$observed_type),
  main = "Observed Structure Types",
  ylab = "Structure count"
)
dev.off()

png(file.path(figures_dir, "r_structure_review_status_counts.png"), width = 1100, height = 750)
barplot(
  table(structures$review_status),
  main = "Structure Review Status Counts",
  ylab = "Structure count"
)
dev.off()

png(file.path(figures_dir, "r_governance_completion_by_type.png"), width = 1200, height = 800)
barplot(
  governance_by_type$average_governance_completion,
  names.arg = governance_by_type$observed_type,
  las = 2,
  main = "Average Governance Completion by Structure Type",
  ylab = "Average governance completion"
)
dev.off()

# ------------------------------------------------------------
# Markdown report
# ------------------------------------------------------------
report_lines <- c(
  "# Catalyst Canvas Structure Type Analysis",
  "",
  "Article: Frameworks, Templates, and Models",
  "",
  "## Summary",
  "",
  paste0("- Structures reviewed: ", nrow(structures)),
  paste0("- Type mismatches: ", nrow(mismatch_report)),
  paste0("- High-risk structures: ", sum(structures$risk_severity == "high")),
  paste0("- Structures requiring review: ", sum(structures$review_status != "ready for managed use")),
  "",
  "## Outputs",
  "",
  "- `r_structure_classification_report.csv`",
  "- `r_observed_structure_type_summary.csv`",
  "- `r_declared_structure_type_summary.csv`",
  "- `r_structure_risk_summary.csv`",
  "- `r_structure_review_summary.csv`",
  "- `r_governance_by_structure_type.csv`",
  "- `r_structure_type_mismatch_report.csv`",
  "- `r_catalyst_canvas_structure_catalog.csv`",
  "",
  "These outputs are generated from synthetic data and demonstrate professional-grade structural-classification workflows."
)

writeLines(report_lines, file.path(reports_dir, "r_catalyst_canvas_structure_type_analysis.md"))

print("Catalyst Canvas R structure type analysis complete.")
print(observed_type_summary)
print(risk_summary)
print(review_summary)
