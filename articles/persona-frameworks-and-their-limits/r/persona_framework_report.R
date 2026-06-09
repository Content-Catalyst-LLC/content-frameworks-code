# Base R workflow for persona readiness and risk diagnostics.

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)

if (length(file_arg) > 0) {
  script_path <- normalizePath(sub("^--file=", "", file_arg[1]), mustWork = TRUE)
  article_root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)
} else {
  article_root <- getwd()
}

setwd(article_root)

data_path <- file.path(article_root, "data", "persona_records.csv")
tables_dir <- file.path(article_root, "outputs", "tables")
figures_dir <- file.path(article_root, "outputs", "figures")

if (!dir.exists(tables_dir)) dir.create(tables_dir, recursive = TRUE)
if (!dir.exists(figures_dir)) dir.create(figures_dir, recursive = TRUE)

personas <- read.csv(data_path, stringsAsFactors = FALSE)

personas$readiness_score <- rowMeans(personas[, c(
  "evidence_strength",
  "specificity",
  "content_fit",
  "segment_alignment",
  "governance_readiness"
)])

personas$weighted_readiness <- (
  personas$evidence_strength * 0.28 +
  personas$specificity * 0.18 +
  personas$content_fit * 0.20 +
  personas$segment_alignment * 0.18 +
  personas$governance_readiness * 0.16
)

personas$risk_score <- apply(personas[, c(
  "stereotype_risk",
  "exclusion_risk",
  "weak_evidence_risk",
  "overgeneralization_risk"
)], 1, max)

personas$revision_pressure <- pmax(0, personas$risk_score - personas$weighted_readiness)

personas$review_priority <- ifelse(
  personas$status == "revise" | personas$risk_score >= 0.70,
  "high",
  ifelse(
    personas$status == "review" |
      personas$revision_pressure >= 0.15 |
      personas$evidence_strength < 0.60 |
      personas$governance_readiness < 0.65 |
      personas$exclusion_risk >= 0.50,
    "medium",
    "standard"
  )
)

personas <- personas[order(personas$weighted_readiness, decreasing = TRUE), ]

write.csv(
  personas,
  file.path(tables_dir, "persona_framework_summary.csv"),
  row.names = FALSE
)

revision_queue <- personas[personas$review_priority != "standard", ]

write.csv(
  revision_queue,
  file.path(tables_dir, "persona_revision_queue.csv"),
  row.names = FALSE
)

png(file.path(figures_dir, "persona_readiness_scores.png"), width = 1200, height = 700)
barplot(
  personas$weighted_readiness,
  names.arg = personas$persona,
  las = 2,
  ylab = "Weighted readiness",
  main = "Persona Framework Readiness"
)
grid()
dev.off()

png(file.path(figures_dir, "persona_risk_scores.png"), width = 1200, height = 700)
barplot(
  personas$risk_score,
  names.arg = personas$persona,
  las = 2,
  ylab = "Risk score",
  main = "Persona Framework Risk"
)
grid()
dev.off()

print(personas[, c("persona", "weighted_readiness", "risk_score", "revision_pressure", "review_priority")])
