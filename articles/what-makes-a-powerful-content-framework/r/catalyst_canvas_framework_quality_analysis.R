# catalyst_canvas_framework_quality_analysis.R
# Base R workflow for framework quality, maturity, risk, and
# governance diagnostics for a Catalyst Canvas-style product layer.

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

frameworks <- read.csv(file.path(data_dir, "framework_quality_scores.csv"), stringsAsFactors = FALSE)
article_map <- read.csv(file.path(data_dir, "content_framework_article_map.csv"), stringsAsFactors = FALSE)
metadata <- read.csv(file.path(data_dir, "metadata_inventory.csv"), stringsAsFactors = FALSE)
links <- read.csv(file.path(data_dir, "internal_links.csv"), stringsAsFactors = FALSE)
taxonomy <- read.csv(file.path(data_dir, "taxonomy_categories.csv"), stringsAsFactors = FALSE)

quality_dimensions <- c(
  "clarity",
  "coherence",
  "transferability",
  "adaptability",
  "explanatory_depth",
  "domain_fit",
  "audience_fit",
  "evidence_alignment",
  "ethical_safety",
  "governability"
)

readiness_dimensions <- c(
  "evidence_alignment",
  "ethical_safety",
  "governability"
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
# Framework quality and maturity
# ------------------------------------------------------------
frameworks$quality_score <- rowSums(frameworks[, quality_dimensions])
frameworks$average_quality <- round(frameworks$quality_score / length(quality_dimensions), 3)
frameworks$readiness_score <- round(rowMeans(frameworks[, readiness_dimensions]), 3)

frameworks$maturity_level <- ifelse(
  frameworks$quality_score >= 44 & frameworks$readiness_score >= 4.0,
  "product-ready",
  ifelse(
    frameworks$quality_score >= 36,
    "strong but review",
    ifelse(frameworks$quality_score >= 28, "developing", "not ready")
  )
)

frameworks$governance_status <- ifelse(
  frameworks$evidence_alignment < 4,
  "evidence review required",
  ifelse(
    frameworks$ethical_safety < 4,
    "ethical review required",
    ifelse(frameworks$governability < 4, "governance plan required", "ready for managed use")
  )
)

framework_quality_report <- frameworks[, c(
  "framework_id",
  "framework_name",
  "domain",
  "primary_use",
  "quality_score",
  "average_quality",
  "readiness_score",
  "maturity_level",
  "governance_status",
  "risk_severity",
  "risk_note"
)]

domain_summary <- aggregate(
  quality_score ~ domain,
  data = frameworks,
  FUN = mean
)

names(domain_summary) <- c("domain", "average_quality_score")
domain_summary$average_quality_score <- round(domain_summary$average_quality_score, 3)

maturity_summary <- as.data.frame(table(frameworks$maturity_level), stringsAsFactors = FALSE)
names(maturity_summary) <- c("maturity_level", "framework_count")

risk_summary <- as.data.frame(table(frameworks$risk_severity), stringsAsFactors = FALSE)
names(risk_summary) <- c("risk_severity", "framework_count")

governance_summary <- as.data.frame(table(frameworks$governance_status), stringsAsFactors = FALSE)
names(governance_summary) <- c("governance_status", "framework_count")

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
# Article-map coverage
# ------------------------------------------------------------
coverage <- aggregate(
  title ~ cluster + status,
  data = article_map,
  FUN = length
)

names(coverage) <- c("cluster", "status", "article_count")

# ------------------------------------------------------------
# Link diagnostics
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
write.csv(framework_quality_report, file.path(tables_dir, "r_framework_quality_report.csv"), row.names = FALSE)
write.csv(domain_summary, file.path(tables_dir, "r_domain_quality_summary.csv"), row.names = FALSE)
write.csv(maturity_summary, file.path(tables_dir, "r_maturity_summary.csv"), row.names = FALSE)
write.csv(risk_summary, file.path(tables_dir, "r_risk_summary.csv"), row.names = FALSE)
write.csv(governance_summary, file.path(tables_dir, "r_governance_summary.csv"), row.names = FALSE)
write.csv(metadata_report, file.path(tables_dir, "r_metadata_readiness_report.csv"), row.names = FALSE)
write.csv(coverage, file.path(tables_dir, "r_article_map_coverage.csv"), row.names = FALSE)
write.csv(link_report, file.path(tables_dir, "r_internal_link_quality_report.csv"), row.names = FALSE)
write.csv(taxonomy_report, file.path(tables_dir, "r_taxonomy_quality_coverage.csv"), row.names = FALSE)
write.csv(catalog, file.path(catalog_dir, "r_catalyst_canvas_framework_quality_catalog.csv"), row.names = FALSE)

# ------------------------------------------------------------
# Figures
# ------------------------------------------------------------
png(file.path(figures_dir, "r_framework_quality_by_domain.png"), width = 1200, height = 800)
barplot(
  domain_summary$average_quality_score,
  names.arg = domain_summary$domain,
  las = 2,
  main = "Average Framework Quality Score by Domain",
  ylab = "Average quality score"
)
dev.off()

png(file.path(figures_dir, "r_framework_maturity_counts.png"), width = 1000, height = 700)
barplot(
  table(frameworks$maturity_level),
  main = "Framework Maturity Counts",
  ylab = "Framework count"
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
  "# Catalyst Canvas Framework Quality Analysis",
  "",
  "Article: What Makes a Powerful Content Framework?",
  "",
  "## Summary",
  "",
  paste0("- Framework records: ", nrow(frameworks)),
  paste0("- Product-ready frameworks: ", sum(frameworks$maturity_level == "product-ready")),
  paste0("- Frameworks requiring governance review: ", sum(frameworks$governance_status != "ready for managed use")),
  "",
  "## Outputs",
  "",
  "- `r_framework_quality_report.csv`",
  "- `r_domain_quality_summary.csv`",
  "- `r_maturity_summary.csv`",
  "- `r_risk_summary.csv`",
  "- `r_governance_summary.csv`",
  "- `r_metadata_readiness_report.csv`",
  "- `r_internal_link_quality_report.csv`",
  "- `r_catalyst_canvas_framework_quality_catalog.csv`",
  "",
  "These outputs are generated from synthetic data and demonstrate professional-grade editorial intelligence workflows."
)

writeLines(report_lines, file.path(reports_dir, "r_catalyst_canvas_framework_quality_analysis.md"))

print("Catalyst Canvas R framework quality analysis complete.")
print(domain_summary)
print(maturity_summary)
print(governance_summary)
