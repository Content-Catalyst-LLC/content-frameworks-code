# Base R workflow for SWOT priority and evidence diagnostics.

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)

if (length(file_arg) > 0) {
  script_path <- normalizePath(sub("^--file=", "", file_arg[1]), mustWork = TRUE)
  article_root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)
} else {
  article_root <- getwd()
}

setwd(article_root)

data_path <- file.path(article_root, "data", "swot_items.csv")
tables_dir <- file.path(article_root, "outputs", "tables")
figures_dir <- file.path(article_root, "outputs", "figures")

if (!dir.exists(tables_dir)) dir.create(tables_dir, recursive = TRUE)
if (!dir.exists(figures_dir)) dir.create(figures_dir, recursive = TRUE)

swot <- read.csv(data_path, stringsAsFactors = FALSE)

swot$priority_score <- rowMeans(swot[, c(
  "impact",
  "confidence",
  "urgency",
  "feasibility",
  "strategic_fit"
)])

swot$weighted_priority <- (
  swot$impact * 0.26 +
  swot$confidence * 0.20 +
  swot$urgency * 0.18 +
  swot$feasibility * 0.16 +
  swot$strategic_fit * 0.20
)

swot$evidence_gap <- pmax(0, swot$claim_strength - swot$evidence_strength)
swot$governance_priority <- pmin(1, swot$weighted_priority + swot$evidence_gap * 0.50)

swot$review_priority <- ifelse(
  swot$status == "revise" | swot$evidence_gap >= 0.30,
  "high",
  ifelse(
    swot$governance_priority >= 0.75 |
      swot$evidence_gap >= 0.15 |
      swot$status == "review",
    "medium",
    "standard"
  )
)

swot <- swot[order(swot$governance_priority, decreasing = TRUE), ]

write.csv(
  swot,
  file.path(tables_dir, "swot_analysis_summary.csv"),
  row.names = FALSE
)

governance_queue <- swot[swot$review_priority != "standard", ]

write.csv(
  governance_queue,
  file.path(tables_dir, "swot_governance_queue.csv"),
  row.names = FALSE
)

png(file.path(figures_dir, "swot_governance_priority.png"), width = 1200, height = 700)
barplot(
  swot$governance_priority,
  names.arg = swot$item,
  las = 2,
  ylab = "Governance priority",
  main = "SWOT Governance Priority"
)
grid()
dev.off()

quadrant_counts <- table(swot$quadrant)

png(file.path(figures_dir, "swot_quadrant_balance.png"), width = 1000, height = 700)
barplot(
  quadrant_counts,
  ylab = "Number of items",
  main = "SWOT Quadrant Balance"
)
grid()
dev.off()

print(swot[, c("item", "quadrant", "weighted_priority", "evidence_gap", "governance_priority", "review_priority")])
