# Base R workflow for Framework Governance and Editorial Maintenance diagnostics.

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)

if (length(file_arg) > 0) {
  script_path <- normalizePath(sub("^--file=", "", file_arg[1]), mustWork = TRUE)
  article_root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)
} else {
  article_root <- getwd()
}

setwd(article_root)

data_path <- file.path(article_root, "data", "framework_governance_items.csv")
tables_dir <- file.path(article_root, "outputs", "tables")
figures_dir <- file.path(article_root, "outputs", "figures")

if (!dir.exists(tables_dir)) dir.create(tables_dir, recursive = TRUE)
if (!dir.exists(figures_dir)) dir.create(figures_dir, recursive = TRUE)

items <- read.csv(data_path, stringsAsFactors = FALSE)

items$governance_maturity <- rowMeans(items[, c(
  "ownership_clarity",
  "review_cycle_strength",
  "metadata_completeness",
  "evidence_status",
  "link_health",
  "taxonomy_alignment",
  "platform_readiness"
)])

items$maintenance_risk <- pmin(
  1,
  (1 - items$governance_maturity) * 0.34 +
    items$stale_evidence_risk * 0.22 +
    (1 - items$link_health) * 0.16 +
    (1 - items$platform_readiness) * 0.12 +
    items$dependency_complexity * 0.16
)

items$review_priority_score <- pmin(
  1,
  items$maintenance_risk * 0.70 +
    items$audience_impact * 0.30
)

items$review_priority <- ifelse(
  items$status == "revise" | items$review_priority_score >= 0.55,
  "high",
  ifelse(
    items$status == "review" | items$review_priority_score >= 0.40,
    "medium",
    "standard"
  )
)

items <- items[order(items$review_priority_score, decreasing = TRUE), ]

write.csv(
  items,
  file.path(tables_dir, "framework_governance_summary.csv"),
  row.names = FALSE
)

governance_queue <- items[items$review_priority != "standard", ]

write.csv(
  governance_queue,
  file.path(tables_dir, "framework_governance_queue.csv"),
  row.names = FALSE
)

png(file.path(figures_dir, "framework_governance_maintenance_risk.png"), width = 1200, height = 700)
barplot(
  items$maintenance_risk,
  names.arg = items$item,
  las = 2,
  ylab = "Maintenance risk",
  main = "Framework Governance Maintenance Risk"
)
grid()
dev.off()

png(file.path(figures_dir, "framework_governance_maturity.png"), width = 1000, height = 700)
barplot(
  items$governance_maturity,
  names.arg = items$item,
  las = 2,
  ylab = "Governance maturity",
  main = "Framework Governance Maturity"
)
grid()
dev.off()

print(items[, c("item", "item_type", "governance_maturity", "maintenance_risk", "review_priority_score", "review_priority")])
