# Base R workflow for OKR KPI and measurement governance diagnostics.

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)

if (length(file_arg) > 0) {
  script_path <- normalizePath(sub("^--file=", "", file_arg[1]), mustWork = TRUE)
  article_root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)
} else {
  article_root <- getwd()
}

setwd(article_root)

data_path <- file.path(article_root, "data", "measurement_items.csv")
tables_dir <- file.path(article_root, "outputs", "tables")
figures_dir <- file.path(article_root, "outputs", "figures")

if (!dir.exists(tables_dir)) dir.create(tables_dir, recursive = TRUE)
if (!dir.exists(figures_dir)) dir.create(figures_dir, recursive = TRUE)

items <- read.csv(data_path, stringsAsFactors = FALSE)

items$quality_score <- rowMeans(items[, c(
  "validity",
  "reliability",
  "strategic_relevance",
  "actionability",
  "timeliness"
)])

items$measurement_risk <- pmin(
  1,
  items$gaming_risk * 0.30 +
    items$ambiguity * 0.25 +
    items$reporting_burden * 0.20 +
    (1 - items$evidence_strength) * 0.25
)

items$evidence_gap <- pmax(0, items$claim_strength - items$evidence_strength)

items$governance_priority <- pmin(
  1,
  items$measurement_risk * 0.40 +
    items$evidence_gap * 0.30 +
    (1 - items$quality_score) * 0.30
)

items$review_priority <- ifelse(
  items$status == "revise" | items$evidence_gap >= 0.30,
  "high",
  ifelse(
    items$governance_priority >= 0.45 |
      items$measurement_risk >= 0.55 |
      items$status == "review",
    "medium",
    "standard"
  )
)

items <- items[order(items$governance_priority, decreasing = TRUE), ]

write.csv(
  items,
  file.path(tables_dir, "measurement_framework_summary.csv"),
  row.names = FALSE
)

governance_queue <- items[items$review_priority != "standard", ]

write.csv(
  governance_queue,
  file.path(tables_dir, "measurement_governance_queue.csv"),
  row.names = FALSE
)

png(file.path(figures_dir, "measurement_governance_priority.png"), width = 1200, height = 700)
barplot(
  items$governance_priority,
  names.arg = items$item,
  las = 2,
  ylab = "Governance priority",
  main = "Measurement Governance Priority"
)
grid()
dev.off()

png(file.path(figures_dir, "measurement_quality_score.png"), width = 1000, height = 700)
barplot(
  items$quality_score,
  names.arg = items$item,
  las = 2,
  ylab = "Metric quality score",
  main = "Measurement Quality Score"
)
grid()
dev.off()

print(items[, c("item", "measurement_type", "quality_score", "measurement_risk", "evidence_gap", "governance_priority", "review_priority")])
