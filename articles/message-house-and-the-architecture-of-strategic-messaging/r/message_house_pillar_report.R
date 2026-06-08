# Base R workflow for Message House pillar and proof diagnostics.

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)

if (length(file_arg) > 0) {
  script_path <- normalizePath(sub("^--file=", "", file_arg[1]), mustWork = TRUE)
  article_root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)
} else {
  article_root <- getwd()
}

setwd(article_root)

data_path <- file.path(article_root, "data", "message_house_pillars.csv")
tables_dir <- file.path(article_root, "outputs", "tables")
figures_dir <- file.path(article_root, "outputs", "figures")

if (!dir.exists(tables_dir)) dir.create(tables_dir, recursive = TRUE)
if (!dir.exists(figures_dir)) dir.create(figures_dir, recursive = TRUE)

pillars <- read.csv(data_path, stringsAsFactors = FALSE)

pillars$readiness_score <- rowMeans(pillars[, c(
  "core_alignment",
  "audience_relevance",
  "evidence_strength",
  "differentiation",
  "governance_readiness"
)])

pillars$weighted_readiness <- (
  pillars$core_alignment * 0.22 +
  pillars$audience_relevance * 0.24 +
  pillars$evidence_strength * 0.24 +
  pillars$differentiation * 0.16 +
  pillars$governance_readiness * 0.14
)

pillar_importance <- rowMeans(pillars[, c(
  "core_alignment",
  "audience_relevance",
  "differentiation"
)])

pillars$proof_gap <- pmax(0, pillar_importance - pillars$evidence_strength)
pillars$message_drift_risk <- pmax(
  pmax(0, pillars$core_alignment - pillars$governance_readiness),
  pillars$proof_gap,
  pillars$ethical_risk * 0.6
)

pillars$review_priority <- ifelse(
  pillars$status == "revise" | pillars$ethical_risk >= 0.70 | pillars$proof_gap >= 0.25,
  "high",
  ifelse(
    pillars$status == "review" |
      pillars$proof_gap >= 0.10 |
      pillars$message_drift_risk >= 0.20 |
      pillars$evidence_strength < 0.65,
    "medium",
    "standard"
  )
)

pillars <- pillars[order(pillars$weighted_readiness, decreasing = TRUE), ]

write.csv(
  pillars,
  file.path(tables_dir, "message_house_pillar_summary.csv"),
  row.names = FALSE
)

revision_queue <- pillars[pillars$review_priority != "standard", ]

write.csv(
  revision_queue,
  file.path(tables_dir, "message_house_revision_queue.csv"),
  row.names = FALSE
)

png(file.path(figures_dir, "message_house_readiness_scores.png"), width = 1200, height = 700)
barplot(
  pillars$weighted_readiness,
  names.arg = pillars$pillar,
  las = 2,
  ylab = "Weighted readiness",
  main = "Message House Pillar Readiness"
)
grid()
dev.off()

png(file.path(figures_dir, "message_house_proof_gaps.png"), width = 1200, height = 700)
barplot(
  pillars$proof_gap,
  names.arg = pillars$pillar,
  las = 2,
  ylab = "Proof gap",
  main = "Message House Proof Gaps"
)
grid()
dev.off()

print(pillars[, c("pillar", "weighted_readiness", "proof_gap", "message_drift_risk", "review_priority")])
