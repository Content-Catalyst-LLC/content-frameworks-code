# Base R workflow for Systems Explanation diagnostics.

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)

if (length(file_arg) > 0) {
  script_path <- normalizePath(sub("^--file=", "", file_arg[1]), mustWork = TRUE)
  article_root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)
} else {
  article_root <- getwd()
}

setwd(article_root)

data_path <- file.path(article_root, "data", "systems_explanation_items.csv")
tables_dir <- file.path(article_root, "outputs", "tables")
figures_dir <- file.path(article_root, "outputs", "figures")

if (!dir.exists(tables_dir)) dir.create(tables_dir, recursive = TRUE)
if (!dir.exists(figures_dir)) dir.create(figures_dir, recursive = TRUE)

items <- read.csv(data_path, stringsAsFactors = FALSE)

items$quality_score <- rowMeans(items[, c(
  "boundary_clarity",
  "actor_coverage",
  "relationship_clarity",
  "feedback_visibility",
  "delay_visibility",
  "stock_flow_clarity",
  "stakeholder_visibility",
  "evidence_strength",
  "leverage_readiness"
)])

items$systems_ambiguity <- pmin(
  1,
  (1 - items$boundary_clarity) * 0.30 +
    (1 - items$relationship_clarity) * 0.30 +
    (1 - items$evidence_strength) * 0.25 +
    (1 - items$feedback_visibility) * 0.15
)

items$review_priority_score <- pmin(
  1,
  items$systems_ambiguity * 0.40 +
    (1 - items$leverage_readiness) * 0.25 +
    (1 - items$stakeholder_visibility) * 0.20 +
    (1 - items$delay_visibility) * 0.15
)

items$review_priority <- ifelse(
  items$status == "revise" | items$review_priority_score >= 0.45,
  "high",
  ifelse(
    items$status == "review" | items$systems_ambiguity >= 0.45,
    "medium",
    "standard"
  )
)

items <- items[order(items$review_priority_score, decreasing = TRUE), ]

write.csv(
  items,
  file.path(tables_dir, "systems_explanation_summary.csv"),
  row.names = FALSE
)

governance_queue <- items[items$review_priority != "standard", ]

write.csv(
  governance_queue,
  file.path(tables_dir, "systems_explanation_governance_queue.csv"),
  row.names = FALSE
)

png(file.path(figures_dir, "systems_explanation_ambiguity.png"), width = 1200, height = 700)
barplot(
  items$systems_ambiguity,
  names.arg = items$item,
  las = 2,
  ylab = "Systems ambiguity",
  main = "Systems Explanation Ambiguity"
)
grid()
dev.off()

png(file.path(figures_dir, "systems_explanation_quality.png"), width = 1000, height = 700)
barplot(
  items$quality_score,
  names.arg = items$item,
  las = 2,
  ylab = "Systems explanation quality score",
  main = "Systems Explanation Quality"
)
grid()
dev.off()

print(items[, c("item", "explanation_type", "quality_score", "systems_ambiguity", "review_priority_score", "review_priority")])
