# Base R workflow for The Limits of Framework Thinking diagnostics.

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)

if (length(file_arg) > 0) {
  script_path <- normalizePath(sub("^--file=", "", file_arg[1]), mustWork = TRUE)
  article_root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)
} else {
  article_root <- getwd()
}

setwd(article_root)

data_path <- file.path(article_root, "data", "framework_limits_items.csv")
tables_dir <- file.path(article_root, "outputs", "tables")
figures_dir <- file.path(article_root, "outputs", "figures")

if (!dir.exists(tables_dir)) dir.create(tables_dir, recursive = TRUE)
if (!dir.exists(figures_dir)) dir.create(figures_dir, recursive = TRUE)

items <- read.csv(data_path, stringsAsFactors = FALSE)

items$usefulness_score <- rowMeans(items[, c(
  "clarity",
  "fit",
  "evidence_alignment",
  "assumption_transparency",
  "governance_readiness"
)])

items$distortion_risk <- pmin(
  1,
  items$oversimplification_risk * 0.22 +
    items$false_precision_risk * 0.22 +
    items$context_loss * 0.20 +
    items$audience_burden * 0.18 +
    items$value_opacity * 0.18
)

items$review_priority_score <- pmin(
  1,
  (1 - items$usefulness_score) * 0.50 +
    items$distortion_risk * 0.50
)

items$review_priority <- ifelse(
  items$status == "revise" | items$review_priority_score >= 0.45,
  "high",
  ifelse(
    items$status == "review" | items$distortion_risk >= 0.40,
    "medium",
    "standard"
  )
)

items <- items[order(items$review_priority_score, decreasing = TRUE), ]

write.csv(
  items,
  file.path(tables_dir, "framework_limits_summary.csv"),
  row.names = FALSE
)

governance_queue <- items[items$review_priority != "standard", ]

write.csv(
  governance_queue,
  file.path(tables_dir, "framework_limits_governance_queue.csv"),
  row.names = FALSE
)

png(file.path(figures_dir, "framework_limits_distortion_risk.png"), width = 1200, height = 700)
barplot(
  items$distortion_risk,
  names.arg = items$item,
  las = 2,
  ylab = "Distortion risk",
  main = "Framework Limits: Distortion Risk"
)
grid()
dev.off()

png(file.path(figures_dir, "framework_limits_usefulness_score.png"), width = 1000, height = 700)
barplot(
  items$usefulness_score,
  names.arg = items$item,
  las = 2,
  ylab = "Framework usefulness score",
  main = "Framework Limits: Usefulness Score"
)
grid()
dev.off()

print(items[, c("item", "framework_type", "usefulness_score", "distortion_risk", "review_priority_score", "review_priority")])
