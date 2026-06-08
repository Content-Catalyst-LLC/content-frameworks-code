# Value Proposition Canvas coverage and relevance report
# Uses base R only.

root <- normalizePath(file.path(dirname(sys.frame(1)$ofile), ".."), mustWork = TRUE)
data_path <- file.path(root, "data", "value_relevance_inventory.csv")
out_tables <- file.path(root, "outputs", "tables")
out_reports <- file.path(root, "outputs", "reports")
dir.create(out_tables, recursive = TRUE, showWarnings = FALSE)
dir.create(out_reports, recursive = TRUE, showWarnings = FALSE)

items <- read.csv(data_path, stringsAsFactors = FALSE)
score_columns <- c(
  "job_alignment",
  "pain_relief_alignment",
  "gain_creation_alignment",
  "evidence_strength",
  "communication_clarity",
  "ethical_fit"
)

items$relevance_score <- rowMeans(items[, score_columns])

classify_relevance <- function(score) {
  if (score >= 0.88) {
    return("strong relevance")
  } else if (score >= 0.78) {
    return("publishable with review")
  } else if (score >= 0.60) {
    return("revise before publication")
  } else {
    return("major relevance gap")
  }
}

items$classification <- vapply(items$relevance_score, classify_relevance, character(1))

metric_means <- data.frame(
  dimension = score_columns,
  average_score = as.numeric(colMeans(items[, score_columns]))
)

write.csv(
  items[, c("item_id", "title", "audience_segment", "status", "relevance_score", "classification", "primary_risk")],
  file.path(out_tables, "r_value_relevance_scores.csv"),
  row.names = FALSE
)

write.csv(
  metric_means,
  file.path(out_tables, "r_value_relevance_dimension_means.csv"),
  row.names = FALSE
)

summary_lines <- c(
  "Value Proposition Canvas relevance report",
  "========================================",
  paste("Items reviewed:", nrow(items)),
  paste("Average score:", round(mean(items$relevance_score), 3)),
  paste("Items below threshold:", paste(items$item_id[items$relevance_score < 0.78], collapse = ", ")),
  "",
  "Dimension means:",
  paste(metric_means$dimension, round(metric_means$average_score, 3), sep = ": ")
)

writeLines(summary_lines, file.path(out_reports, "r_value_relevance_summary.txt"))
print(items[, c("item_id", "relevance_score", "classification")])
