# Base R workflow for Framework Drift and Conceptual Decay diagnostics.

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)

if (length(file_arg) > 0) {
  script_path <- normalizePath(sub("^--file=", "", file_arg[1]), mustWork = TRUE)
  article_root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)
} else {
  article_root <- getwd()
}

setwd(article_root)

data_path <- file.path(article_root, "data", "framework_drift_items.csv")
tables_dir <- file.path(article_root, "outputs", "tables")
figures_dir <- file.path(article_root, "outputs", "figures")

if (!dir.exists(tables_dir)) dir.create(tables_dir, recursive = TRUE)
if (!dir.exists(figures_dir)) dir.create(figures_dir, recursive = TRUE)

items <- read.csv(data_path, stringsAsFactors = FALSE)

items$conceptual_integrity <- rowMeans(items[, c(
  "definition_consistency",
  "boundary_clarity",
  "evidence_currency",
  "metadata_consistency",
  "link_health",
  "governance_maturity"
)])

items$drift_risk <- pmin(
  1,
  (1 - items$conceptual_integrity) * 0.32 +
    items$reuse_pressure * 0.20 +
    items$stale_evidence_risk * 0.18 +
    items$dependency_complexity * 0.16 +
    (1 - items$platform_alignment) * 0.14
)

items$repair_priority_score <- pmin(
  1,
  items$drift_risk * 0.70 +
    items$audience_impact * 0.30
)

items$repair_priority <- ifelse(
  items$status == "revise" | items$repair_priority_score >= 0.55,
  "high",
  ifelse(
    items$status == "review" | items$repair_priority_score >= 0.40,
    "medium",
    "standard"
  )
)

items <- items[order(items$repair_priority_score, decreasing = TRUE), ]

write.csv(
  items,
  file.path(tables_dir, "framework_drift_summary.csv"),
  row.names = FALSE
)

repair_queue <- items[items$repair_priority != "standard", ]

write.csv(
  repair_queue,
  file.path(tables_dir, "framework_drift_repair_queue.csv"),
  row.names = FALSE
)

png(file.path(figures_dir, "framework_drift_risk.png"), width = 1200, height = 700)
barplot(
  items$drift_risk,
  names.arg = items$item,
  las = 2,
  ylab = "Drift risk",
  main = "Framework Drift Risk"
)
grid()
dev.off()

png(file.path(figures_dir, "framework_conceptual_integrity.png"), width = 1000, height = 700)
barplot(
  items$conceptual_integrity,
  names.arg = items$item,
  las = 2,
  ylab = "Conceptual integrity",
  main = "Framework Conceptual Integrity"
)
grid()
dev.off()

print(items[, c("item", "item_type", "conceptual_integrity", "drift_risk", "repair_priority_score", "repair_priority")])
