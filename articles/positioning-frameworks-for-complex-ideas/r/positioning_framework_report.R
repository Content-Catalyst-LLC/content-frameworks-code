# Base R workflow for positioning readiness and drift diagnostics.

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)

if (length(file_arg) > 0) {
  script_path <- normalizePath(sub("^--file=", "", file_arg[1]), mustWork = TRUE)
  article_root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)
} else {
  article_root <- getwd()
}

setwd(article_root)

data_path <- file.path(article_root, "data", "positioning_records.csv")
tables_dir <- file.path(article_root, "outputs", "tables")
figures_dir <- file.path(article_root, "outputs", "figures")

if (!dir.exists(tables_dir)) dir.create(tables_dir, recursive = TRUE)
if (!dir.exists(figures_dir)) dir.create(figures_dir, recursive = TRUE)

positioning <- read.csv(data_path, stringsAsFactors = FALSE)

positioning$readiness_score <- rowMeans(positioning[, c(
  "category_clarity",
  "audience_relevance",
  "differentiation",
  "evidence_strength",
  "governance_readiness",
  "boundary_clarity"
)])

positioning$weighted_readiness <- (
  positioning$category_clarity * 0.18 +
  positioning$audience_relevance * 0.20 +
  positioning$differentiation * 0.16 +
  positioning$evidence_strength * 0.20 +
  positioning$governance_readiness * 0.14 +
  positioning$boundary_clarity * 0.12
)

claim_strength <- rowMeans(positioning[, c(
  "category_clarity",
  "audience_relevance",
  "differentiation"
)])

positioning$evidence_gap <- pmax(0, claim_strength - positioning$evidence_strength)

positioning$review_priority <- ifelse(
  positioning$status == "revise" | positioning$ethical_risk >= 0.70,
  "high",
  ifelse(
    positioning$status == "review" |
      positioning$evidence_gap >= 0.15 |
      positioning$drift_risk >= 0.60 |
      positioning$boundary_clarity < 0.65 |
      positioning$governance_readiness < 0.65 |
      positioning$evidence_strength < 0.65,
    "medium",
    "standard"
  )
)

positioning <- positioning[order(positioning$weighted_readiness, decreasing = TRUE), ]

write.csv(
  positioning,
  file.path(tables_dir, "positioning_framework_summary.csv"),
  row.names = FALSE
)

revision_queue <- positioning[positioning$review_priority != "standard", ]

write.csv(
  revision_queue,
  file.path(tables_dir, "positioning_revision_queue.csv"),
  row.names = FALSE
)

png(file.path(figures_dir, "positioning_readiness_scores.png"), width = 1200, height = 700)
barplot(
  positioning$weighted_readiness,
  names.arg = positioning$idea,
  las = 2,
  ylab = "Weighted readiness",
  main = "Positioning Readiness for Complex Ideas"
)
grid()
dev.off()

png(file.path(figures_dir, "positioning_drift_risk.png"), width = 1200, height = 700)
barplot(
  positioning$drift_risk,
  names.arg = positioning$idea,
  las = 2,
  ylab = "Drift risk",
  main = "Positioning Drift Risk"
)
grid()
dev.off()

print(positioning[, c("idea", "weighted_readiness", "evidence_gap", "drift_risk", "review_priority")])
