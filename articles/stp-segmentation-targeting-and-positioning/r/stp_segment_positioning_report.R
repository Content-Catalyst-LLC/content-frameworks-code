# STP segment positioning report
# Base R workflow for segmentation, targeting, and positioning diagnostics.

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)

if (length(file_arg) > 0) {
  script_path <- normalizePath(sub("^--file=", "", file_arg[1]), mustWork = TRUE)
  article_root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)
} else {
  article_root <- getwd()
}

setwd(article_root)

data_path <- file.path(article_root, "data", "stp_segments.csv")
tables_dir <- file.path(article_root, "outputs", "tables")
figures_dir <- file.path(article_root, "outputs", "figures")

if (!dir.exists(tables_dir)) {
  dir.create(tables_dir, recursive = TRUE)
}

if (!dir.exists(figures_dir)) {
  dir.create(figures_dir, recursive = TRUE)
}

stp <- read.csv(data_path, stringsAsFactors = FALSE)

stp$target_score <- rowMeans(stp[, c(
  "need_intensity",
  "strategic_fit",
  "reachability",
  "evidence_fit",
  "ethical_responsibility"
)])

stp$weighted_target_score <- (
  stp$need_intensity * 0.25 +
  stp$strategic_fit * 0.20 +
  stp$reachability * 0.15 +
  stp$evidence_fit * 0.20 +
  stp$ethical_responsibility * 0.20
)

stp$positioning_score <- rowMeans(stp[, c(
  "category_clarity",
  "audience_relevance",
  "differentiation",
  "evidence_fit",
  "credibility"
)])

stp$positioning_gap <- pmax(0, stp$need_intensity - stp$positioning_score)

classify_target <- function(score) {
  if (score >= 0.85) {
    return("primary target candidate")
  } else if (score >= 0.70) {
    return("strong secondary target")
  } else if (score >= 0.55) {
    return("monitor or support with lighter pathway")
  } else {
    return("low current fit")
  }
}

stp$target_classification <- vapply(
  stp$weighted_target_score,
  classify_target,
  character(1)
)

stp$ethical_review_flag <- ifelse(
  stp$stereotype_risk >= 0.70 | stp$exclusion_risk >= 0.70,
  "high ethical review",
  ifelse(
    stp$stereotype_risk >= 0.50 | stp$exclusion_risk >= 0.50,
    "moderate ethical review",
    "standard review"
  )
)

stp <- stp[order(stp$weighted_target_score, decreasing = TRUE), ]

write.csv(
  stp,
  file.path(tables_dir, "stp_segment_positioning_summary.csv"),
  row.names = FALSE
)

revision_queue <- stp[
  stp$positioning_gap >= 0.15 | stp$ethical_review_flag != "standard review",
]

write.csv(
  revision_queue,
  file.path(tables_dir, "stp_revision_queue.csv"),
  row.names = FALSE
)

metric_means <- colMeans(stp[, c(
  "need_intensity",
  "strategic_fit",
  "reachability",
  "evidence_fit",
  "ethical_responsibility",
  "positioning_score"
)])

write.csv(
  data.frame(metric = names(metric_means), mean_score = as.numeric(metric_means)),
  file.path(tables_dir, "stp_dimension_means.csv"),
  row.names = FALSE
)

png(file.path(figures_dir, "stp_target_scores.png"), width = 1200, height = 700)
barplot(
  stp$weighted_target_score,
  names.arg = stp$segment,
  las = 2,
  ylab = "Weighted target score",
  main = "STP Weighted Target Score by Segment"
)
grid()
dev.off()

png(file.path(figures_dir, "stp_positioning_gaps.png"), width = 1200, height = 700)
barplot(
  stp$positioning_gap,
  names.arg = stp$segment,
  las = 2,
  ylab = "Positioning gap",
  main = "Positioning Gap by Segment"
)
grid()
dev.off()

print(stp[, c("segment", "weighted_target_score", "positioning_score", "positioning_gap", "ethical_review_flag")])
