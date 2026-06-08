# catalyst_canvas_framework_history_analysis.R
# Base R workflow for historical framework analysis,
# lineage comparison, influence degree, transfer risk,
# governance readiness, and catalog exports.

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

frameworks <- read.csv(file.path(data_dir, "historical_framework_records.csv"), stringsAsFactors = FALSE)
influences <- read.csv(file.path(data_dir, "framework_influence_edges.csv"), stringsAsFactors = FALSE)
article_map <- read.csv(file.path(data_dir, "content_framework_article_map.csv"), stringsAsFactors = FALSE)
metadata <- read.csv(file.path(data_dir, "metadata_inventory.csv"), stringsAsFactors = FALSE)
links <- read.csv(file.path(data_dir, "internal_links.csv"), stringsAsFactors = FALSE)
taxonomy <- read.csv(file.path(data_dir, "taxonomy_categories.csv"), stringsAsFactors = FALSE)

governance_fields <- c(
  "purpose_documented",
  "use_conditions_documented",
  "limitations_documented",
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
# Historical framework scoring
# ------------------------------------------------------------
governance_matrix <- frameworks[, governance_fields] == "yes"
frameworks$governance_score <- round(rowSums(governance_matrix) / length(governance_fields), 4)

frameworks$transfer_review_status <- ifelse(
  frameworks$transferred_across_domains == "yes" & frameworks$use_conditions_documented != "yes",
  "transfer review required",
  ifelse(
    frameworks$risk_severity == "high",
    "high risk review required",
    ifelse(
      frameworks$governance_score < 0.8,
      "governance incomplete",
      ifelse(frameworks$risk_severity == "medium", "risk review recommended", "managed use")
    )
  )
)

history_report <- frameworks[, c(
  "framework_id",
  "framework_name",
  "period",
  "lineage",
  "domain",
  "structure_type",
  "primary_function",
  "transferred_across_domains",
  "governance_score",
  "transfer_review_status",
  "risk_severity",
  "risk_note"
)]

period_summary <- as.data.frame(table(frameworks$period), stringsAsFactors = FALSE)
names(period_summary) <- c("period", "framework_count")

lineage_summary <- as.data.frame(table(frameworks$lineage), stringsAsFactors = FALSE)
names(lineage_summary) <- c("lineage", "framework_count")

domain_summary <- as.data.frame(table(frameworks$domain), stringsAsFactors = FALSE)
names(domain_summary) <- c("domain", "framework_count")

structure_type_summary <- as.data.frame(table(frameworks$structure_type), stringsAsFactors = FALSE)
names(structure_type_summary) <- c("structure_type", "framework_count")

risk_summary <- as.data.frame(table(frameworks$risk_severity), stringsAsFactors = FALSE)
names(risk_summary) <- c("risk_severity", "framework_count")

review_summary <- as.data.frame(table(frameworks$transfer_review_status), stringsAsFactors = FALSE)
names(review_summary) <- c("transfer_review_status", "framework_count")

governance_by_lineage <- aggregate(
  governance_score ~ lineage,
  data = frameworks,
  FUN = mean
)
names(governance_by_lineage) <- c("lineage", "average_governance_score")
governance_by_lineage$average_governance_score <- round(governance_by_lineage$average_governance_score, 4)

# ------------------------------------------------------------
# Influence degree
# ------------------------------------------------------------
influence_outgoing <- as.data.frame(table(influences$source_framework_id), stringsAsFactors = FALSE)
names(influence_outgoing) <- c("framework_id", "outgoing_influences")

influence_incoming <- as.data.frame(table(influences$target_framework_id), stringsAsFactors = FALSE)
names(influence_incoming) <- c("framework_id", "incoming_influences")

influence_degree <- merge(
  data.frame(framework_id = unique(c(frameworks$framework_id, influence_outgoing$framework_id, influence_incoming$framework_id)), stringsAsFactors = FALSE),
  influence_outgoing,
  by = "framework_id",
  all.x = TRUE
)

influence_degree <- merge(influence_degree, influence_incoming, by = "framework_id", all.x = TRUE)
influence_degree$outgoing_influences[is.na(influence_degree$outgoing_influences)] <- 0
influence_degree$incoming_influences[is.na(influence_degree$incoming_influences)] <- 0
influence_degree$total_influence_degree <- influence_degree$outgoing_influences + influence_degree$incoming_influences

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
write.csv(history_report, file.path(tables_dir, "r_historical_framework_report.csv"), row.names = FALSE)
write.csv(period_summary, file.path(tables_dir, "r_framework_history_period_summary.csv"), row.names = FALSE)
write.csv(lineage_summary, file.path(tables_dir, "r_framework_history_lineage_summary.csv"), row.names = FALSE)
write.csv(domain_summary, file.path(tables_dir, "r_framework_history_domain_summary.csv"), row.names = FALSE)
write.csv(structure_type_summary, file.path(tables_dir, "r_framework_history_structure_type_summary.csv"), row.names = FALSE)
write.csv(risk_summary, file.path(tables_dir, "r_framework_history_risk_summary.csv"), row.names = FALSE)
write.csv(review_summary, file.path(tables_dir, "r_framework_history_review_summary.csv"), row.names = FALSE)
write.csv(governance_by_lineage, file.path(tables_dir, "r_governance_by_lineage.csv"), row.names = FALSE)
write.csv(influence_degree, file.path(tables_dir, "r_framework_influence_degree.csv"), row.names = FALSE)
write.csv(metadata_report, file.path(tables_dir, "r_metadata_history_readiness.csv"), row.names = FALSE)
write.csv(coverage, file.path(tables_dir, "r_article_map_coverage.csv"), row.names = FALSE)
write.csv(link_report, file.path(tables_dir, "r_internal_link_history_report.csv"), row.names = FALSE)
write.csv(taxonomy_report, file.path(tables_dir, "r_taxonomy_history_coverage.csv"), row.names = FALSE)
write.csv(catalog, file.path(catalog_dir, "r_catalyst_canvas_framework_history_catalog.csv"), row.names = FALSE)

# ------------------------------------------------------------
# Figures
# ------------------------------------------------------------
png(file.path(figures_dir, "r_framework_history_by_lineage.png"), width = 1200, height = 800)
barplot(
  table(frameworks$lineage),
  las = 2,
  main = "Historical Framework Records by Lineage",
  ylab = "Framework count"
)
dev.off()

png(file.path(figures_dir, "r_framework_history_risk_counts.png"), width = 1000, height = 700)
barplot(
  table(frameworks$risk_severity),
  main = "Historical Framework Risk Severity Counts",
  ylab = "Framework count"
)
dev.off()

png(file.path(figures_dir, "r_governance_by_lineage.png"), width = 1200, height = 800)
barplot(
  governance_by_lineage$average_governance_score,
  names.arg = governance_by_lineage$lineage,
  las = 2,
  main = "Average Governance Score by Historical Lineage",
  ylab = "Average governance score"
)
dev.off()

# ------------------------------------------------------------
# Markdown report
# ------------------------------------------------------------
report_lines <- c(
  "# Catalyst Canvas Framework History Analysis",
  "",
  "Article: The History of Framework Thinking in Communication and Strategy",
  "",
  "## Summary",
  "",
  paste0("- Historical framework records: ", nrow(frameworks)),
  paste0("- Influence edges: ", nrow(influences)),
  paste0("- Records requiring review: ", sum(frameworks$transfer_review_status != "managed use")),
  "",
  "## Outputs",
  "",
  "- `r_historical_framework_report.csv`",
  "- `r_framework_history_period_summary.csv`",
  "- `r_framework_history_lineage_summary.csv`",
  "- `r_framework_history_domain_summary.csv`",
  "- `r_framework_history_risk_summary.csv`",
  "- `r_governance_by_lineage.csv`",
  "- `r_framework_influence_degree.csv`",
  "- `r_catalyst_canvas_framework_history_catalog.csv`",
  "",
  "These outputs are generated from synthetic data and demonstrate professional-grade historical framework analysis workflows."
)

writeLines(report_lines, file.path(reports_dir, "r_catalyst_canvas_framework_history_analysis.md"))

print("Catalyst Canvas R framework history analysis complete.")
print(lineage_summary)
print(risk_summary)
print(review_summary)
