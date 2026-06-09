# Base R workflow for logic model and Theory of Change diagnostics.

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)

if (length(file_arg) > 0) {
  script_path <- normalizePath(sub("^--file=", "", file_arg[1]), mustWork = TRUE)
  article_root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)
} else {
  article_root <- getwd()
}

setwd(article_root)

data_path <- file.path(article_root, "data", "logic_model_elements.csv")
tables_dir <- file.path(article_root, "outputs", "tables")
figures_dir <- file.path(article_root, "outputs", "figures")

if (!dir.exists(tables_dir)) dir.create(tables_dir, recursive = TRUE)
if (!dir.exists(figures_dir)) dir.create(figures_dir, recursive = TRUE)

elements <- read.csv(data_path, stringsAsFactors = FALSE)

elements$assumption_risk <- elements$assumption_importance * (1 - elements$assumption_evidence)
elements$evidence_gap <- pmax(0, elements$claim_strength - elements$evidence_strength)
elements$pathway_quality <- rowMeans(elements[, c("evidence_strength", "assumption_evidence", "measurement_coverage", "outcome_clarity")])

elements$governance_priority <- pmin(
  1,
  elements$evidence_gap * 0.35 +
    elements$assumption_risk * 0.35 +
    (1 - elements$measurement_coverage) * 0.20 +
    (1 - elements$outcome_clarity) * 0.10
)

elements$review_priority <- ifelse(
  elements$status == "revise" | elements$evidence_gap >= 0.30,
  "high",
  ifelse(
    elements$governance_priority >= 0.45 |
      elements$assumption_risk >= 0.40 |
      elements$status == "review",
    "medium",
    "standard"
  )
)

elements <- elements[order(elements$governance_priority, decreasing = TRUE), ]

write.csv(elements, file.path(tables_dir, "logic_model_summary.csv"), row.names = FALSE)
governance_queue <- elements[elements$review_priority != "standard", ]
write.csv(governance_queue, file.path(tables_dir, "logic_model_governance_queue.csv"), row.names = FALSE)

png(file.path(figures_dir, "logic_model_governance_priority.png"), width = 1200, height = 700)
barplot(elements$governance_priority, names.arg = elements$element, las = 2, ylab = "Governance priority", main = "Logic Model Governance Priority")
grid()
dev.off()

png(file.path(figures_dir, "logic_model_pathway_quality.png"), width = 1000, height = 700)
barplot(elements$pathway_quality, names.arg = elements$element, las = 2, ylab = "Pathway quality", main = "Logic Model Pathway Quality")
grid()
dev.off()

print(elements[, c("element", "model_layer", "pathway_quality", "assumption_risk", "evidence_gap", "governance_priority", "review_priority")])
