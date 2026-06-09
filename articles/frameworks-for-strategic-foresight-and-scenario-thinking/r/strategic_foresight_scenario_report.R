# Base R workflow for strategic foresight and scenario thinking diagnostics.

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)

if (length(file_arg) > 0) {
  script_path <- normalizePath(sub("^--file=", "", file_arg[1]), mustWork = TRUE)
  article_root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)
} else {
  article_root <- getwd()
}

setwd(article_root)

data_path <- file.path(article_root, "data", "strategic_foresight_items.csv")
tables_dir <- file.path(article_root, "outputs", "tables")
figures_dir <- file.path(article_root, "outputs", "figures")

if (!dir.exists(tables_dir)) dir.create(tables_dir, recursive = TRUE)
if (!dir.exists(figures_dir)) dir.create(figures_dir, recursive = TRUE)

items <- read.csv(data_path, stringsAsFactors = FALSE)

items$quality_score <- rowMeans(items[, c(
  "driver_clarity",
  "uncertainty_logic",
  "scenario_logic",
  "assumption_transparency",
  "option_relevance",
  "indicator_coverage",
  "evidence_strength",
  "stakeholder_visibility"
)])

items$assumption_risk <- items$importance * items$uncertainty * (1 - items$evidence_strength)

items$review_priority_score <- pmin(
  1,
  items$assumption_risk * 0.35 +
    (1 - items$indicator_coverage) * 0.25 +
    (1 - items$option_relevance) * 0.20 +
    (1 - items$stakeholder_visibility) * 0.20
)

items$review_priority <- ifelse(
  items$status == "revise" | items$review_priority_score >= 0.45,
  "high",
  ifelse(
    items$status == "review" | items$assumption_risk >= 0.18,
    "medium",
    "standard"
  )
)

items <- items[order(items$review_priority_score, decreasing = TRUE), ]

write.csv(
  items,
  file.path(tables_dir, "strategic_foresight_scenario_summary.csv"),
  row.names = FALSE
)

governance_queue <- items[items$review_priority != "standard", ]

write.csv(
  governance_queue,
  file.path(tables_dir, "strategic_foresight_governance_queue.csv"),
  row.names = FALSE
)

png(file.path(figures_dir, "strategic_foresight_assumption_risk.png"), width = 1200, height = 700)
barplot(
  items$assumption_risk,
  names.arg = items$item,
  las = 2,
  ylab = "Assumption risk",
  main = "Strategic Foresight Assumption Risk"
)
grid()
dev.off()

png(file.path(figures_dir, "strategic_foresight_quality.png"), width = 1000, height = 700)
barplot(
  items$quality_score,
  names.arg = items$item,
  las = 2,
  ylab = "Scenario quality score",
  main = "Strategic Foresight Scenario Quality"
)
grid()
dev.off()

print(items[, c("item", "foresight_type", "quality_score", "assumption_risk", "review_priority_score", "review_priority")])
