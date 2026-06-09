# Base R workflow for audience journey readiness and link gap diagnostics.

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)

if (length(file_arg) > 0) {
  script_path <- normalizePath(sub("^--file=", "", file_arg[1]), mustWork = TRUE)
  article_root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)
} else {
  article_root <- getwd()
}

setwd(article_root)

data_path <- file.path(article_root, "data", "audience_journey_stages.csv")
tables_dir <- file.path(article_root, "outputs", "tables")
figures_dir <- file.path(article_root, "outputs", "figures")

if (!dir.exists(tables_dir)) dir.create(tables_dir, recursive = TRUE)
if (!dir.exists(figures_dir)) dir.create(figures_dir, recursive = TRUE)

journey <- read.csv(data_path, stringsAsFactors = FALSE)

journey$readiness_score <- rowMeans(journey[, c(
  "stage_clarity",
  "content_coverage",
  "transition_quality",
  "evidence_readiness",
  "governance_readiness"
)])

journey$weighted_readiness <- (
  journey$stage_clarity * 0.18 +
  journey$content_coverage * 0.22 +
  journey$transition_quality * 0.20 +
  journey$evidence_readiness * 0.22 +
  journey$governance_readiness * 0.18
)

journey$link_gap <- pmax(0, journey$required_links - journey$available_links)
journey$persona_mismatch <- pmax(0, 1 - journey$persona_fit)
journey$normalized_link_gap <- pmin(1, journey$link_gap / pmax(1, journey$required_links))
journey$evidence_gap <- pmax(0, 0.70 - journey$evidence_readiness)
journey$transition_gap <- pmax(0, 0.65 - journey$transition_quality)
journey$governance_gap <- pmax(0, 0.65 - journey$governance_readiness)

journey$journey_risk <- apply(journey[, c(
  "normalized_link_gap",
  "persona_mismatch",
  "staleness_risk",
  "evidence_gap",
  "transition_gap",
  "governance_gap"
)], 1, max)

journey$review_priority <- ifelse(
  journey$status == "revise" | journey$journey_risk >= 0.70,
  "high",
  ifelse(
    journey$status == "review" |
      journey$link_gap > 0 |
      journey$journey_risk >= 0.45 |
      journey$evidence_readiness < 0.70 |
      journey$governance_readiness < 0.65,
    "medium",
    "standard"
  )
)

journey <- journey[order(journey$weighted_readiness, decreasing = TRUE), ]

write.csv(
  journey,
  file.path(tables_dir, "audience_journey_summary.csv"),
  row.names = FALSE
)

revision_queue <- journey[journey$review_priority != "standard", ]

write.csv(
  revision_queue,
  file.path(tables_dir, "audience_journey_revision_queue.csv"),
  row.names = FALSE
)

png(file.path(figures_dir, "audience_journey_readiness_scores.png"), width = 1200, height = 700)
barplot(
  journey$weighted_readiness,
  names.arg = journey$stage,
  las = 2,
  ylab = "Weighted readiness",
  main = "Audience Journey Readiness"
)
grid()
dev.off()

png(file.path(figures_dir, "audience_journey_link_gaps.png"), width = 1200, height = 700)
barplot(
  journey$link_gap,
  names.arg = journey$stage,
  las = 2,
  ylab = "Missing journey links",
  main = "Audience Journey Link Gaps"
)
grid()
dev.off()

print(journey[, c("stage", "weighted_readiness", "link_gap", "journey_risk", "review_priority")])
