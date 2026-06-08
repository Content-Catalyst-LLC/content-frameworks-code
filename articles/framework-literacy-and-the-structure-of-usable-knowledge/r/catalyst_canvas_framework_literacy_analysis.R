# catalyst_canvas_framework_literacy_analysis.R
# Base R workflow for framework literacy, blind-spot review,
# use-condition clarity, ethical safety, governance readiness,
# metadata readiness, and domain analysis.

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

frameworks <- read.csv(file.path(data_dir, "framework_literacy_records.csv"), stringsAsFactors = FALSE)
article_map <- read.csv(file.path(data_dir, "content_framework_article_map.csv"), stringsAsFactors = FALSE)
metadata <- read.csv(file.path(data_dir, "metadata_inventory.csv"), stringsAsFactors = FALSE)
links <- read.csv(file.path(data_dir, "internal_links.csv"), stringsAsFactors = FALSE)
taxonomy <- read.csv(file.path(data_dir, "taxonomy_categories.csv"), stringsAsFactors = FALSE)
use_conditions <- read.csv(file.path(data_dir, "framework_use_conditions.csv"), stringsAsFactors = FALSE)

literacy_dimensions <- c(
  "assumption_awareness",
  "blind_spot_recognition",
  "boundary_clarity",
  "use_condition_clarity",
  "evidence_alignment",
  "ethical_safety",
  "audience_fit",
  "domain_fit",
  "adaptability",
  "governance_readiness"
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
# Framework literacy scoring
# ------------------------------------------------------------
frameworks$literacy_score <- rowSums(frameworks[, literacy_dimensions])
frameworks$average_literacy_score <- round(frameworks$literacy_score / length(literacy_dimensions), 3)

frameworks$readiness_status <- ifelse(
  frameworks$literacy_score >= 40 &
    frameworks$blind_spot_recognition >= 4 &
    frameworks$use_condition_clarity >= 4 &
    frameworks$evidence_alignment >= 4 &
    frameworks$ethical_safety >= 4 &
    frameworks$governance_readiness >= 4,
  "framework-literate use ready",
  "review required"
)

framework_literacy_report <- frameworks[, c(
  "framework_id",
  "framework_name",
  "domain",
  "primary_use",
  "literacy_score",
  "average_literacy_score",
  "readiness_status",
  "risk_severity",
  "primary_blind_spot"
)]

domain_summary <- aggregate(
  literacy_score ~ domain,
  data = frameworks,
  FUN = mean
)

names(domain_summary) <- c("domain", "average_literacy_score")
domain_summary$average_literacy_score <- round(domain_summary$average_literacy_score, 3)

risk_summary <- as.data.frame(table(frameworks$risk_severity), stringsAsFactors = FALSE)
names(risk_summary) <- c("risk_severity", "framework_count")

readiness_summary <- as.data.frame(table(frameworks$readiness_status), stringsAsFactors = FALSE)
names(readiness_summary) <- c("readiness_status", "framework_count")

blind_spot_summary <- as.data.frame(table(frameworks$primary_blind_spot), stringsAsFactors = FALSE)
names(blind_spot_summary) <- c("primary_blind_spot", "framework_count")

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

use_condition_report <- use_conditions
use_condition_report$has_avoid_condition <- nchar(use_condition_report$avoid_when) > 0
use_condition_report$has_review_owner <- nchar(use_condition_report$review_owner) > 0

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
write.csv(framework_literacy_report, file.path(tables_dir, "r_framework_literacy_report.csv"), row.names = FALSE)
write.csv(domain_summary, file.path(tables_dir, "r_framework_literacy_domain_summary.csv"), row.names = FALSE)
write.csv(risk_summary, file.path(tables_dir, "r_framework_literacy_risk_summary.csv"), row.names = FALSE)
write.csv(readiness_summary, file.path(tables_dir, "r_framework_literacy_readiness_summary.csv"), row.names = FALSE)
write.csv(blind_spot_summary, file.path(tables_dir, "r_framework_blind_spot_summary.csv"), row.names = FALSE)
write.csv(metadata_report, file.path(tables_dir, "r_metadata_literacy_readiness.csv"), row.names = FALSE)
write.csv(coverage, file.path(tables_dir, "r_article_map_coverage.csv"), row.names = FALSE)
write.csv(link_report, file.path(tables_dir, "r_internal_link_literacy_report.csv"), row.names = FALSE)
write.csv(taxonomy_report, file.path(tables_dir, "r_taxonomy_literacy_coverage.csv"), row.names = FALSE)
write.csv(use_condition_report, file.path(tables_dir, "r_framework_use_condition_report.csv"), row.names = FALSE)
write.csv(catalog, file.path(catalog_dir, "r_catalyst_canvas_framework_literacy_catalog.csv"), row.names = FALSE)

# ------------------------------------------------------------
# Figures
# ------------------------------------------------------------
png(file.path(figures_dir, "r_framework_literacy_by_domain.png"), width = 1200, height = 800)
barplot(
  domain_summary$average_literacy_score,
  names.arg = domain_summary$domain,
  las = 2,
  main = "Average Framework Literacy Score by Domain",
  ylab = "Average literacy score"
)
dev.off()

png(file.path(figures_dir, "r_framework_literacy_readiness_counts.png"), width = 1000, height = 700)
barplot(
  table(frameworks$readiness_status),
  main = "Framework Literacy Readiness Counts",
  ylab = "Framework count"
)
dev.off()

png(file.path(figures_dir, "r_framework_literacy_risk_counts.png"), width = 1000, height = 700)
barplot(
  table(frameworks$risk_severity),
  main = "Framework Literacy Risk Severity Counts",
  ylab = "Framework count"
)
dev.off()

# ------------------------------------------------------------
# Markdown report
# ------------------------------------------------------------
report_lines <- c(
  "# Catalyst Canvas Framework Literacy Analysis",
  "",
  "Article: Framework Literacy and the Structure of Usable Knowledge",
  "",
  "## Summary",
  "",
  paste0("- Framework records: ", nrow(frameworks)),
  paste0("- Frameworks ready for framework-literate use: ", sum(frameworks$readiness_status == "framework-literate use ready")),
  paste0("- Frameworks requiring review: ", sum(frameworks$readiness_status == "review required")),
  "",
  "## Outputs",
  "",
  "- `r_framework_literacy_report.csv`",
  "- `r_framework_literacy_domain_summary.csv`",
  "- `r_framework_literacy_risk_summary.csv`",
  "- `r_framework_literacy_readiness_summary.csv`",
  "- `r_framework_blind_spot_summary.csv`",
  "- `r_metadata_literacy_readiness.csv`",
  "- `r_internal_link_literacy_report.csv`",
  "- `r_catalyst_canvas_framework_literacy_catalog.csv`",
  "",
  "These outputs are generated from synthetic data and demonstrate professional-grade framework-literacy workflows."
)

writeLines(report_lines, file.path(reports_dir, "r_catalyst_canvas_framework_literacy_analysis.md"))

print("Catalyst Canvas R framework literacy analysis complete.")
print(domain_summary)
print(risk_summary)
print(readiness_summary)
