# Base R workflow for AI-Assisted Framework Design diagnostics.

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)

if (length(file_arg) > 0) {
  script_path <- normalizePath(sub("^--file=", "", file_arg[1]), mustWork = TRUE)
  article_root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)
} else {
  article_root <- getwd()
}

setwd(article_root)

data_path <- file.path(article_root, "data", "ai_assisted_framework_design_items.csv")
tables_dir <- file.path(article_root, "outputs", "tables")
figures_dir <- file.path(article_root, "outputs", "figures")

if (!dir.exists(tables_dir)) dir.create(tables_dir, recursive = TRUE)
if (!dir.exists(figures_dir)) dir.create(figures_dir, recursive = TRUE)

items <- read.csv(data_path, stringsAsFactors = FALSE)

items$readiness_score <- rowMeans(items[, c(
  "conceptual_clarity",
  "evidence_grounding",
  "metadata_consistency",
  "human_review_strength",
  "bias_review",
  "governance_maturity",
  "platform_readiness",
  "drift_control"
)])

items$ai_framework_risk <- pmin(
  1,
  (1 - items$readiness_score) * 0.32 +
    items$unsupported_claim_risk * 0.24 +
    items$generic_structure_risk * 0.18 +
    (1 - items$bias_review) * 0.14 +
    (1 - items$output_validation) * 0.12
)

items$governance_priority_score <- pmin(
  1,
  items$ai_framework_risk * 0.70 +
    items$audience_impact * 0.30
)

items$governance_priority <- ifelse(
  items$status == "revise" | items$governance_priority_score >= 0.55,
  "high",
  ifelse(
    items$status == "review" | items$governance_priority_score >= 0.40,
    "medium",
    "standard"
  )
)

items <- items[order(items$governance_priority_score, decreasing = TRUE), ]

write.csv(
  items,
  file.path(tables_dir, "ai_assisted_framework_design_summary.csv"),
  row.names = FALSE
)

governance_queue <- items[items$governance_priority != "standard", ]

write.csv(
  governance_queue,
  file.path(tables_dir, "ai_assisted_framework_design_governance_queue.csv"),
  row.names = FALSE
)

png(file.path(figures_dir, "ai_assisted_framework_design_risk.png"), width = 1200, height = 700)
barplot(
  items$ai_framework_risk,
  names.arg = items$item,
  las = 2,
  ylab = "AI framework risk",
  main = "AI-Assisted Framework Design Risk"
)
grid()
dev.off()

png(file.path(figures_dir, "ai_assisted_framework_readiness.png"), width = 1000, height = 700)
barplot(
  items$readiness_score,
  names.arg = items$item,
  las = 2,
  ylab = "Readiness score",
  main = "AI-Assisted Framework Readiness"
)
grid()
dev.off()

print(items[, c("item", "item_type", "readiness_score", "ai_framework_risk", "governance_priority_score", "governance_priority")])
