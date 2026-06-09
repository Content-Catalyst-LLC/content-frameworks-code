# Base R workflow for sustainability communication claim diagnostics.

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)

if (length(file_arg) > 0) {
  script_path <- normalizePath(sub("^--file=", "", file_arg[1]), mustWork = TRUE)
  article_root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)
} else {
  article_root <- getwd()
}

setwd(article_root)

data_path <- file.path(article_root, "data", "sustainability_claims.csv")
tables_dir <- file.path(article_root, "outputs", "tables")
figures_dir <- file.path(article_root, "outputs", "figures")

if (!dir.exists(tables_dir)) dir.create(tables_dir, recursive = TRUE)
if (!dir.exists(figures_dir)) dir.create(figures_dir, recursive = TRUE)

claims <- read.csv(data_path, stringsAsFactors = FALSE)

claims$quality_score <- rowMeans(claims[, c(
  "claim_specificity",
  "boundary_clarity",
  "evidence_strength",
  "materiality_relevance",
  "stakeholder_visibility",
  "accountability_coverage"
)])

claims$evidence_gap <- pmax(0, claims$claim_strength - claims$evidence_strength)

vagueness <- 1 - claims$claim_specificity

claims$greenwashing_risk <- pmin(
  1,
  vagueness * 0.25 +
    (1 - claims$evidence_strength) * 0.25 +
    (1 - claims$boundary_clarity) * 0.20 +
    (1 - claims$accountability_coverage) * 0.15 +
    claims$promotional_intensity * 0.15
)

claims$review_priority_score <- pmin(
  1,
  claims$evidence_gap * 0.35 +
    claims$greenwashing_risk * 0.40 +
    (1 - claims$stakeholder_visibility) * 0.15 +
    (1 - claims$uncertainty_disclosure) * 0.10
)

claims$review_priority <- ifelse(
  claims$status == "revise" | claims$evidence_gap >= 0.30,
  "high",
  ifelse(
    claims$review_priority_score >= 0.45 |
      claims$greenwashing_risk >= 0.55 |
      claims$status == "review",
    "medium",
    "standard"
  )
)

claims <- claims[order(claims$review_priority_score, decreasing = TRUE), ]

write.csv(
  claims,
  file.path(tables_dir, "sustainability_communication_summary.csv"),
  row.names = FALSE
)

governance_queue <- claims[claims$review_priority != "standard", ]

write.csv(
  governance_queue,
  file.path(tables_dir, "sustainability_claim_governance_queue.csv"),
  row.names = FALSE
)

png(file.path(figures_dir, "sustainability_greenwashing_risk.png"), width = 1200, height = 700)
barplot(
  claims$greenwashing_risk,
  names.arg = claims$claim,
  las = 2,
  ylab = "Greenwashing risk",
  main = "Sustainability Claim Greenwashing Risk"
)
grid()
dev.off()

png(file.path(figures_dir, "sustainability_claim_quality.png"), width = 1000, height = 700)
barplot(
  claims$quality_score,
  names.arg = claims$claim,
  las = 2,
  ylab = "Claim quality score",
  main = "Sustainability Claim Quality"
)
grid()
dev.off()

print(claims[, c("claim", "claim_type", "quality_score", "evidence_gap", "greenwashing_risk", "review_priority_score", "review_priority")])
