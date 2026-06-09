# Base R workflow for Scaling Knowledge Through Frameworks diagnostics.

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)

if (length(file_arg) > 0) {
  script_path <- normalizePath(sub("^--file=", "", file_arg[1]), mustWork = TRUE)
  article_root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)
} else {
  article_root <- getwd()
}

setwd(article_root)

data_path <- file.path(article_root, "data", "knowledge_scaling_items.csv")
tables_dir <- file.path(article_root, "outputs", "tables")
figures_dir <- file.path(article_root, "outputs", "figures")

if (!dir.exists(tables_dir)) dir.create(tables_dir, recursive = TRUE)
if (!dir.exists(figures_dir)) dir.create(figures_dir, recursive = TRUE)

items <- read.csv(data_path, stringsAsFactors = FALSE)

items$scalability_score <- rowMeans(items[, c(
  "modularity",
  "taxonomy_quality",
  "metadata_completeness",
  "link_coverage",
  "evidence_alignment",
  "reuse_readiness",
  "governance_maturity",
  "platform_readiness",
  "audience_pathway_clarity"
)])

items$maintenance_risk <- pmin(
  1,
  (1 - items$governance_maturity) * 0.30 +
    (1 - items$evidence_alignment) * 0.25 +
    (1 - items$link_coverage) * 0.20 +
    items$dependency_complexity * 0.25
)

items$review_priority_score <- pmin(
  1,
  (1 - items$scalability_score) * 0.50 +
    items$maintenance_risk * 0.50
)

items$review_priority <- ifelse(
  items$status == "revise" | items$review_priority_score >= 0.45,
  "high",
  ifelse(
    items$status == "review" | items$maintenance_risk >= 0.40,
    "medium",
    "standard"
  )
)

items <- items[order(items$review_priority_score, decreasing = TRUE), ]

write.csv(
  items,
  file.path(tables_dir, "knowledge_scaling_summary.csv"),
  row.names = FALSE
)

governance_queue <- items[items$review_priority != "standard", ]

write.csv(
  governance_queue,
  file.path(tables_dir, "knowledge_scaling_governance_queue.csv"),
  row.names = FALSE
)

png(file.path(figures_dir, "knowledge_scaling_maintenance_risk.png"), width = 1200, height = 700)
barplot(
  items$maintenance_risk,
  names.arg = items$item,
  las = 2,
  ylab = "Maintenance risk",
  main = "Knowledge Scaling Maintenance Risk"
)
grid()
dev.off()

png(file.path(figures_dir, "knowledge_scaling_scalability_score.png"), width = 1000, height = 700)
barplot(
  items$scalability_score,
  names.arg = items$item,
  las = 2,
  ylab = "Knowledge scalability score",
  main = "Knowledge Scalability Score"
)
grid()
dev.off()

print(items[, c("item", "asset_type", "scalability_score", "maintenance_risk", "review_priority_score", "review_priority")])
