# Base R workflow for PESTLE signal priority and governance diagnostics.

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)

if (length(file_arg) > 0) {
  script_path <- normalizePath(sub("^--file=", "", file_arg[1]), mustWork = TRUE)
  article_root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)
} else {
  article_root <- getwd()
}

setwd(article_root)

data_path <- file.path(article_root, "data", "pestle_factors.csv")
tables_dir <- file.path(article_root, "outputs", "tables")
figures_dir <- file.path(article_root, "outputs", "figures")

if (!dir.exists(tables_dir)) dir.create(tables_dir, recursive = TRUE)
if (!dir.exists(figures_dir)) dir.create(figures_dir, recursive = TRUE)

pestle <- read.csv(data_path, stringsAsFactors = FALSE)

pestle$readiness_score <- rowMeans(pestle[, c(
  "impact",
  "urgency",
  "evidence_strength",
  "strategic_relevance",
  "actionability"
)])

pestle$weighted_priority <- (
  pestle$impact * 0.24 +
  pestle$urgency * 0.18 +
  pestle$evidence_strength * 0.16 +
  pestle$uncertainty * 0.12 +
  pestle$strategic_relevance * 0.20 +
  pestle$actionability * 0.10
)

pestle$evidence_gap <- pmax(0, pestle$claim_strength - pestle$evidence_strength)
pestle$monitoring_priority <- pestle$impact * pestle$uncertainty
pestle$governance_priority <- pmin(1, pestle$weighted_priority + pestle$evidence_gap * 0.40)

pestle$review_priority <- ifelse(
  pestle$status == "revise" | pestle$evidence_gap >= 0.30,
  "high",
  ifelse(
    pestle$governance_priority >= 0.75 |
      pestle$monitoring_priority >= 0.50 |
      pestle$evidence_gap >= 0.15 |
      pestle$status == "review",
    "medium",
    "standard"
  )
)

pestle <- pestle[order(pestle$governance_priority, decreasing = TRUE), ]

write.csv(
  pestle,
  file.path(tables_dir, "pestle_analysis_summary.csv"),
  row.names = FALSE
)

governance_queue <- pestle[pestle$review_priority != "standard", ]

write.csv(
  governance_queue,
  file.path(tables_dir, "pestle_governance_queue.csv"),
  row.names = FALSE
)

png(file.path(figures_dir, "pestle_governance_priority.png"), width = 1200, height = 700)
barplot(
  pestle$governance_priority,
  names.arg = pestle$factor,
  las = 2,
  ylab = "Governance priority",
  main = "PESTLE Governance Priority"
)
grid()
dev.off()

category_counts <- table(pestle$category)

png(file.path(figures_dir, "pestle_category_balance.png"), width = 1000, height = 700)
barplot(
  category_counts,
  ylab = "Number of factors",
  main = "PESTLE Category Balance"
)
grid()
dev.off()

print(pestle[, c("factor", "category", "weighted_priority", "evidence_gap", "monitoring_priority", "governance_priority", "review_priority")])
