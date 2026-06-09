# Base R workflow for policy explanation and governance communication diagnostics.

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)

if (length(file_arg) > 0) {
  script_path <- normalizePath(sub("^--file=", "", file_arg[1]), mustWork = TRUE)
  article_root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)
} else {
  article_root <- getwd()
}

setwd(article_root)

data_path <- file.path(article_root, "data", "policy_governance_items.csv")
tables_dir <- file.path(article_root, "outputs", "tables")
figures_dir <- file.path(article_root, "outputs", "figures")

if (!dir.exists(tables_dir)) dir.create(tables_dir, recursive = TRUE)
if (!dir.exists(figures_dir)) dir.create(figures_dir, recursive = TRUE)

items <- read.csv(data_path, stringsAsFactors = FALSE)

items$completeness_score <- rowMeans(items[, c(
  "problem_clarity",
  "authority_clarity",
  "evidence_strength",
  "stakeholder_visibility",
  "implementation_detail",
  "accountability_coverage",
  "participation_clarity"
)])

items$evidence_gap <- pmax(0, items$claim_strength - items$evidence_strength)

items$governance_risk <- pmin(
  1,
  (1 - items$accountability_coverage) * 0.25 +
    (1 - items$stakeholder_visibility) * 0.20 +
    (1 - items$evidence_strength) * 0.20 +
    items$ambiguity * 0.20 +
    (1 - items$implementation_detail) * 0.15
)

items$review_priority_score <- pmin(
  1,
  items$evidence_gap * 0.35 +
    items$governance_risk * 0.40 +
    (1 - items$completeness_score) * 0.25
)

items$review_priority <- ifelse(
  items$status == "revise" | items$evidence_gap >= 0.30,
  "high",
  ifelse(
    items$review_priority_score >= 0.45 |
      items$governance_risk >= 0.55 |
      items$status == "review",
    "medium",
    "standard"
  )
)

items <- items[order(items$review_priority_score, decreasing = TRUE), ]

write.csv(
  items,
  file.path(tables_dir, "policy_governance_summary.csv"),
  row.names = FALSE
)

governance_queue <- items[items$review_priority != "standard", ]

write.csv(
  governance_queue,
  file.path(tables_dir, "policy_governance_queue.csv"),
  row.names = FALSE
)

png(file.path(figures_dir, "policy_governance_risk.png"), width = 1200, height = 700)
barplot(
  items$governance_risk,
  names.arg = items$item,
  las = 2,
  ylab = "Governance communication risk",
  main = "Policy Explanation Governance Risk"
)
grid()
dev.off()

png(file.path(figures_dir, "policy_explanation_completeness.png"), width = 1000, height = 700)
barplot(
  items$completeness_score,
  names.arg = items$item,
  las = 2,
  ylab = "Completeness score",
  main = "Policy Explanation Completeness"
)
grid()
dev.off()

print(items[, c("item", "policy_area", "completeness_score", "evidence_gap", "governance_risk", "review_priority_score", "review_priority")])
