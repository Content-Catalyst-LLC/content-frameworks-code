# Base R workflow for Framework Composition diagnostics.

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)

if (length(file_arg) > 0) {
  script_path <- normalizePath(sub("^--file=", "", file_arg[1]), mustWork = TRUE)
  article_root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)
} else {
  article_root <- getwd()
}

setwd(article_root)

data_path <- file.path(article_root, "data", "framework_composition_items.csv")
tables_dir <- file.path(article_root, "outputs", "tables")
figures_dir <- file.path(article_root, "outputs", "figures")

if (!dir.exists(tables_dir)) dir.create(tables_dir, recursive = TRUE)
if (!dir.exists(figures_dir)) dir.create(figures_dir, recursive = TRUE)

items <- read.csv(data_path, stringsAsFactors = FALSE)

items$quality_score <- rowMeans(items[, c(
  "purpose_fit",
  "role_clarity",
  "boundary_clarity",
  "sequence_clarity",
  "translation_quality",
  "evidence_alignment",
  "governance_readiness"
)])

items$confusion_risk <- pmin(
  1,
  (1 - items$role_clarity) * 0.25 +
    items$audience_burden * 0.25 +
    (1 - items$translation_quality) * 0.25 +
    items$conflict_risk * 0.25
)

items$review_priority_score <- pmin(
  1,
  (1 - items$quality_score) * 0.50 +
    items$confusion_risk * 0.50
)

items$review_priority <- ifelse(
  items$status == "revise" | items$review_priority_score >= 0.45,
  "high",
  ifelse(
    items$status == "review" | items$confusion_risk >= 0.40,
    "medium",
    "standard"
  )
)

items <- items[order(items$review_priority_score, decreasing = TRUE), ]

write.csv(
  items,
  file.path(tables_dir, "framework_composition_summary.csv"),
  row.names = FALSE
)

governance_queue <- items[items$review_priority != "standard", ]

write.csv(
  governance_queue,
  file.path(tables_dir, "framework_composition_governance_queue.csv"),
  row.names = FALSE
)

png(file.path(figures_dir, "framework_composition_confusion_risk.png"), width = 1200, height = 700)
barplot(
  items$confusion_risk,
  names.arg = items$item,
  las = 2,
  ylab = "Confusion risk",
  main = "Framework Composition Confusion Risk"
)
grid()
dev.off()

png(file.path(figures_dir, "framework_composition_quality.png"), width = 1000, height = 700)
barplot(
  items$quality_score,
  names.arg = items$item,
  las = 2,
  ylab = "Composition quality score",
  main = "Framework Composition Quality"
)
grid()
dev.off()

print(items[, c("item", "composition_type", "quality_score", "confusion_risk", "review_priority_score", "review_priority")])
