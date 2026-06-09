# Base R workflow for Five Forces intensity, evidence, and governance diagnostics.

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)

if (length(file_arg) > 0) {
  script_path <- normalizePath(sub("^--file=", "", file_arg[1]), mustWork = TRUE)
  article_root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)
} else {
  article_root <- getwd()
}

setwd(article_root)

data_path <- file.path(article_root, "data", "five_forces_records.csv")
tables_dir <- file.path(article_root, "outputs", "tables")
figures_dir <- file.path(article_root, "outputs", "figures")

if (!dir.exists(tables_dir)) dir.create(tables_dir, recursive = TRUE)
if (!dir.exists(figures_dir)) dir.create(figures_dir, recursive = TRUE)

forces <- read.csv(data_path, stringsAsFactors = FALSE)

forces$readiness_score <- rowMeans(forces[, c(
  "intensity",
  "evidence_strength",
  "strategic_relevance",
  "actionability"
)])

forces$weighted_priority <- (
  forces$intensity * 0.30 +
  forces$evidence_strength * 0.18 +
  forces$uncertainty * 0.12 +
  forces$strategic_relevance * 0.26 +
  forces$actionability * 0.14
)

forces$evidence_gap <- pmax(0, forces$claim_strength - forces$evidence_strength)
forces$governance_priority <- pmin(1, forces$weighted_priority + forces$evidence_gap * 0.45)

forces$review_priority <- ifelse(
  forces$status == "revise" | forces$evidence_gap >= 0.30,
  "high",
  ifelse(
    forces$governance_priority >= 0.75 |
      forces$evidence_gap >= 0.15 |
      forces$status == "review",
    "medium",
    "standard"
  )
)

forces <- forces[order(forces$governance_priority, decreasing = TRUE), ]

write.csv(
  forces,
  file.path(tables_dir, "five_forces_summary.csv"),
  row.names = FALSE
)

governance_queue <- forces[forces$review_priority != "standard", ]

write.csv(
  governance_queue,
  file.path(tables_dir, "five_forces_governance_queue.csv"),
  row.names = FALSE
)

png(file.path(figures_dir, "five_forces_governance_priority.png"), width = 1200, height = 700)
barplot(
  forces$governance_priority,
  names.arg = forces$force,
  las = 2,
  ylab = "Governance priority",
  main = "Five Forces Governance Priority"
)
grid()
dev.off()

png(file.path(figures_dir, "five_forces_intensity.png"), width = 1000, height = 700)
barplot(
  forces$intensity,
  names.arg = forces$force,
  las = 2,
  ylab = "Force intensity",
  main = "Competitive Force Intensity"
)
grid()
dev.off()

print(forces[, c("force", "intensity", "weighted_priority", "evidence_gap", "governance_priority", "review_priority")])
