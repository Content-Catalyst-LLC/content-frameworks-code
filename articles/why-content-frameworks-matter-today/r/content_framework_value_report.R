# Base R workflow for Why Content Frameworks Matter Today diagnostics.

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)

if (length(file_arg) > 0) {
  script_path <- normalizePath(sub("^--file=", "", file_arg[1]), mustWork = TRUE)
  article_root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)
} else {
  article_root <- getwd()
}

setwd(article_root)

data_path <- file.path(article_root, "data", "content_framework_value_items.csv")
tables_dir <- file.path(article_root, "outputs", "tables")
figures_dir <- file.path(article_root, "outputs", "figures")

if (!dir.exists(tables_dir)) dir.create(tables_dir, recursive = TRUE)
if (!dir.exists(figures_dir)) dir.create(figures_dir, recursive = TRUE)

items <- read.csv(data_path, stringsAsFactors = FALSE)

items$value_score <- rowMeans(items[, c(
  "coherence",
  "reuse_readiness",
  "evidence_visibility",
  "audience_pathway_clarity",
  "governance_maturity",
  "platform_readiness",
  "learning_support",
  "ai_readiness"
)])

items$framework_risk <- pmin(
  1,
  (1 - items$evidence_visibility) * 0.22 +
    (1 - items$governance_maturity) * 0.22 +
    items$fragmentation_risk * 0.22 +
    (1 - items$context_preservation) * 0.17 +
    items$maintenance_burden * 0.17
)

items$review_priority_score <- pmin(
  1,
  (1 - items$value_score) * 0.50 +
    items$framework_risk * 0.50
)

items$review_priority <- ifelse(
  items$status == "revise" | items$review_priority_score >= 0.45,
  "high",
  ifelse(
    items$status == "review" | items$framework_risk >= 0.40,
    "medium",
    "standard"
  )
)

items <- items[order(items$review_priority_score, decreasing = TRUE), ]

write.csv(
  items,
  file.path(tables_dir, "content_framework_value_summary.csv"),
  row.names = FALSE
)

governance_queue <- items[items$review_priority != "standard", ]

write.csv(
  governance_queue,
  file.path(tables_dir, "content_framework_value_governance_queue.csv"),
  row.names = FALSE
)

png(file.path(figures_dir, "content_framework_value_risk.png"), width = 1200, height = 700)
barplot(
  items$framework_risk,
  names.arg = items$item,
  las = 2,
  ylab = "Framework risk",
  main = "Content Framework Risk"
)
grid()
dev.off()

png(file.path(figures_dir, "content_framework_value_score.png"), width = 1000, height = 700)
barplot(
  items$value_score,
  names.arg = items$item,
  las = 2,
  ylab = "Framework value score",
  main = "Content Framework Value Score"
)
grid()
dev.off()

print(items[, c("item", "framework_type", "value_score", "framework_risk", "review_priority_score", "review_priority")])
