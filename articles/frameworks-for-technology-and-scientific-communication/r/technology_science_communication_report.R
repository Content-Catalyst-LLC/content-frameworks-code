# Base R workflow for technology and scientific communication diagnostics.

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)

if (length(file_arg) > 0) {
  script_path <- normalizePath(sub("^--file=", "", file_arg[1]), mustWork = TRUE)
  article_root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)
} else {
  article_root <- getwd()
}

setwd(article_root)

data_path <- file.path(article_root, "data", "technology_science_communication_items.csv")
tables_dir <- file.path(article_root, "outputs", "tables")
figures_dir <- file.path(article_root, "outputs", "figures")

if (!dir.exists(tables_dir)) dir.create(tables_dir, recursive = TRUE)
if (!dir.exists(figures_dir)) dir.create(figures_dir, recursive = TRUE)

items <- read.csv(data_path, stringsAsFactors = FALSE)

items$quality_score <- rowMeans(items[, c(
  "claim_clarity",
  "evidence_strength",
  "method_transparency",
  "uncertainty_disclosure",
  "audience_fit",
  "risk_visibility",
  "stakeholder_visibility"
)])

items$evidence_gap <- pmax(0, items$claim_breadth - items$evidence_strength)

items$hype_risk <- pmin(
  1,
  (1 - items$evidence_strength) * 0.25 +
    (1 - items$uncertainty_disclosure) * 0.25 +
    items$promotional_intensity * 0.25 +
    items$claim_breadth * 0.25
)

items$review_priority_score <- pmin(
  1,
  items$evidence_gap * 0.35 +
    items$hype_risk * 0.40 +
    (1 - items$audience_fit) * 0.15 +
    (1 - items$risk_visibility) * 0.10
)

items$review_priority <- ifelse(
  items$status == "revise" | items$evidence_gap >= 0.30,
  "high",
  ifelse(
    items$review_priority_score >= 0.45 |
      items$hype_risk >= 0.55 |
      items$status == "review",
    "medium",
    "standard"
  )
)

items <- items[order(items$review_priority_score, decreasing = TRUE), ]

write.csv(
  items,
  file.path(tables_dir, "technology_science_communication_summary.csv"),
  row.names = FALSE
)

governance_queue <- items[items$review_priority != "standard", ]

write.csv(
  governance_queue,
  file.path(tables_dir, "technology_science_governance_queue.csv"),
  row.names = FALSE
)

png(file.path(figures_dir, "technology_science_hype_risk.png"), width = 1200, height = 700)
barplot(
  items$hype_risk,
  names.arg = items$item,
  las = 2,
  ylab = "Hype risk",
  main = "Technology and Scientific Communication Hype Risk"
)
grid()
dev.off()

png(file.path(figures_dir, "technology_science_quality.png"), width = 1000, height = 700)
barplot(
  items$quality_score,
  names.arg = items$item,
  las = 2,
  ylab = "Communication quality score",
  main = "Technology and Scientific Communication Quality"
)
grid()
dev.off()

print(items[, c("item", "communication_type", "quality_score", "evidence_gap", "hype_risk", "review_priority_score", "review_priority")])
