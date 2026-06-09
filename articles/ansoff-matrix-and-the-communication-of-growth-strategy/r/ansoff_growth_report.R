# Base R workflow for Ansoff growth strategy diagnostics.

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)

if (length(file_arg) > 0) {
  script_path <- normalizePath(sub("^--file=", "", file_arg[1]), mustWork = TRUE)
  article_root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)
} else {
  article_root <- getwd()
}

setwd(article_root)

data_path <- file.path(article_root, "data", "ansoff_growth_options.csv")
tables_dir <- file.path(article_root, "outputs", "tables")
figures_dir <- file.path(article_root, "outputs", "figures")

if (!dir.exists(tables_dir)) dir.create(tables_dir, recursive = TRUE)
if (!dir.exists(figures_dir)) dir.create(figures_dir, recursive = TRUE)

growth_options <- read.csv(data_path, stringsAsFactors = FALSE)

growth_options$readiness_score <- rowMeans(growth_options[, c(
  "strategic_fit",
  "evidence_strength",
  "feasibility",
  "capability_readiness"
)])

growth_options$risk_score <- pmin(
  1,
  ((1 - growth_options$market_familiarity) +
     (1 - growth_options$product_familiarity) +
     growth_options$uncertainty) / 3
)

growth_options$evidence_gap <- pmax(
  0,
  growth_options$claim_strength - growth_options$evidence_strength
)

growth_options$growth_quality <- pmax(
  0,
  pmin(
    1,
    growth_options$readiness_score * 0.55 +
      growth_options$expected_value * 0.35 -
      growth_options$risk_score * 0.20
  )
)

growth_options$governance_priority <- pmin(
  1,
  growth_options$risk_score * 0.35 +
    growth_options$evidence_gap * 0.40 +
    (1 - growth_options$feasibility) * 0.25
)

growth_options$review_priority <- ifelse(
  growth_options$status == "revise" | growth_options$evidence_gap >= 0.30,
  "high",
  ifelse(
    growth_options$governance_priority >= 0.50 |
      growth_options$risk_score >= 0.55 |
      growth_options$status == "review",
    "medium",
    "standard"
  )
)

growth_options <- growth_options[order(growth_options$governance_priority, decreasing = TRUE), ]

write.csv(
  growth_options,
  file.path(tables_dir, "ansoff_growth_summary.csv"),
  row.names = FALSE
)

governance_queue <- growth_options[growth_options$review_priority != "standard", ]

write.csv(
  governance_queue,
  file.path(tables_dir, "ansoff_governance_queue.csv"),
  row.names = FALSE
)

png(file.path(figures_dir, "ansoff_governance_priority.png"), width = 1200, height = 700)
barplot(
  growth_options$governance_priority,
  names.arg = growth_options$option,
  las = 2,
  ylab = "Governance priority",
  main = "Ansoff Governance Priority"
)
grid()
dev.off()

png(file.path(figures_dir, "ansoff_growth_quality.png"), width = 1000, height = 700)
barplot(
  growth_options$growth_quality,
  names.arg = growth_options$option,
  las = 2,
  ylab = "Growth quality",
  main = "Ansoff Growth Quality"
)
grid()
dev.off()

print(growth_options[, c("option", "growth_path", "readiness_score", "risk_score", "growth_quality", "governance_priority", "review_priority")])
