# Base R workflow for institutional and organizational communication diagnostics.

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)

if (length(file_arg) > 0) {
  script_path <- normalizePath(sub("^--file=", "", file_arg[1]), mustWork = TRUE)
  article_root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)
} else {
  article_root <- getwd()
}

setwd(article_root)

data_path <- file.path(article_root, "data", "institutional_communication_items.csv")
tables_dir <- file.path(article_root, "outputs", "tables")
figures_dir <- file.path(article_root, "outputs", "figures")

if (!dir.exists(tables_dir)) dir.create(tables_dir, recursive = TRUE)
if (!dir.exists(figures_dir)) dir.create(figures_dir, recursive = TRUE)

items <- read.csv(data_path, stringsAsFactors = FALSE)

items$quality_score <- rowMeans(items[, c(
  "clarity",
  "authority_coverage",
  "evidence_strength",
  "stakeholder_visibility",
  "feedback_quality",
  "channel_fit",
  "cultural_alignment",
  "governance_coverage"
)])

items$evidence_gap <- pmax(0, items$claim_strength - items$evidence_strength)

items$trust_risk <- pmin(
  1,
  items$ambiguity * 0.25 +
    (1 - items$governance_coverage) * 0.25 +
    (1 - items$evidence_strength) * 0.20 +
    (1 - items$stakeholder_visibility) * 0.15 +
    (1 - items$feedback_quality) * 0.15
)

items$review_priority_score <- pmin(
  1,
  items$trust_risk * 0.40 +
    (1 - items$authority_coverage) * 0.25 +
    items$evidence_gap * 0.20 +
    (1 - items$feedback_quality) * 0.15
)

items$review_priority <- ifelse(
  items$status == "revise" | items$evidence_gap >= 0.30,
  "high",
  ifelse(
    items$review_priority_score >= 0.45 |
      items$trust_risk >= 0.55 |
      items$status == "review",
    "medium",
    "standard"
  )
)

items <- items[order(items$review_priority_score, decreasing = TRUE), ]

write.csv(
  items,
  file.path(tables_dir, "institutional_communication_summary.csv"),
  row.names = FALSE
)

governance_queue <- items[items$review_priority != "standard", ]

write.csv(
  governance_queue,
  file.path(tables_dir, "institutional_communication_governance_queue.csv"),
  row.names = FALSE
)

png(file.path(figures_dir, "institutional_communication_trust_risk.png"), width = 1200, height = 700)
barplot(
  items$trust_risk,
  names.arg = items$item,
  las = 2,
  ylab = "Trust risk",
  main = "Institutional Communication Trust Risk"
)
grid()
dev.off()

png(file.path(figures_dir, "institutional_communication_quality.png"), width = 1000, height = 700)
barplot(
  items$quality_score,
  names.arg = items$item,
  las = 2,
  ylab = "Communication quality score",
  main = "Institutional Communication Quality"
)
grid()
dev.off()

print(items[, c("item", "communication_type", "quality_score", "evidence_gap", "trust_risk", "review_priority_score", "review_priority")])
