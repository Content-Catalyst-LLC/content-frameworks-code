# Base R workflow for 5W1H explanatory-completeness readiness.

if (!exists("article_root")) article_root <- getwd()

data_dir <- file.path(article_root, "data")
tables_dir <- file.path(article_root, "outputs", "tables")
figures_dir <- file.path(article_root, "outputs", "figures")
reports_dir <- file.path(article_root, "outputs", "reports")
catalog_dir <- file.path(article_root, "outputs", "catalog_exports")

dir.create(tables_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(figures_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(reports_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(catalog_dir, recursive = TRUE, showWarnings = FALSE)

assets <- read.csv(file.path(data_dir, "five_w_one_h_content_inventory.csv"), stringsAsFactors = FALSE)
review_queue <- read.csv(file.path(data_dir, "editorial_review_queue.csv"), stringsAsFactors = FALSE)

yes <- function(x) tolower(trimws(x)) %in% c("yes", "true", "1", "ready", "complete")

balance_score <- function(values) {
  mean_value <- mean(values)
  if (mean_value == 0) return(0)
  balance <- 1 - min(sd(values) / mean_value, 1)
  max(0, min(balance, 1))
}

questions <- c("who", "what", "when", "where", "why", "how")
coverage_matrix <- sapply(questions, function(q) yes(assets[[paste0(q, "_answered")]]))
support_matrix <- sapply(questions, function(q) yes(assets[[paste0(q, "_supported")]]))

assets$coverage_score <- round(rowMeans(coverage_matrix), 4)

supported_answer_counts <- rowSums(coverage_matrix & support_matrix)
answered_counts <- rowSums(coverage_matrix)

assets$evidence_support_score <- ifelse(answered_counts == 0, 0, supported_answer_counts / answered_counts)
assets$evidence_support_score <- round(assets$evidence_support_score, 4)

assets$balance_score <- apply(coverage_matrix, 1, balance_score)
assets$balance_score <- round(assets$balance_score, 4)

assets$audience_fit_score <- round(
  (
    yes(assets$audience_context_present) +
      yes(assets$scope_note_present) +
      yes(assets$plain_language_summary_present)
  ) / 3,
  4
)

assets$governance_score <- round(
  (
    yes(assets$review_owner_present) +
      yes(assets$last_review_date_present) +
      yes(assets$freshness_checked) +
      yes(assets$revision_queue_checked)
  ) / 4,
  4
)

assets$explanatory_readiness_score <- round(
  0.24 * assets$coverage_score +
    0.26 * assets$evidence_support_score +
    0.16 * assets$balance_score +
    0.16 * assets$audience_fit_score +
    0.18 * assets$governance_score,
  4
)

assets$explanatory_status <- ifelse(
  assets$explanatory_readiness_score >= 0.78,
  "ready",
  "governance review"
)

question_coverage <- data.frame(
  question = questions,
  assets_answered = colSums(coverage_matrix),
  assets_supported = colSums(coverage_matrix & support_matrix)
)

question_coverage$answer_rate <- round(question_coverage$assets_answered / nrow(assets), 4)
question_coverage$support_rate <- ifelse(
  question_coverage$assets_answered == 0,
  0,
  round(question_coverage$assets_supported / question_coverage$assets_answered, 4)
)

audience_summary <- aggregate(explanatory_readiness_score ~ audience, data = assets, FUN = mean)
names(audience_summary) <- c("audience", "average_explanatory_readiness")
audience_summary$average_explanatory_readiness <- round(audience_summary$average_explanatory_readiness, 4)

asset_type_summary <- aggregate(explanatory_readiness_score ~ asset_type, data = assets, FUN = mean)
names(asset_type_summary) <- c("asset_type", "average_explanatory_readiness")
asset_type_summary$average_explanatory_readiness <- round(asset_type_summary$average_explanatory_readiness, 4)

governance_queue <- subset(assets, explanatory_status == "governance review")

catalog <- assets[, c(
  "asset_id",
  "asset_name",
  "asset_type",
  "audience",
  "explanatory_readiness_score",
  "explanatory_status"
)]

catalog$series <- "Content Frameworks"
catalog$article_slug <- "5w1h-and-the-architecture-of-explanatory-completeness"
catalog$github_path <- "articles/5w1h-and-the-architecture-of-explanatory-completeness/"

write.csv(assets, file.path(tables_dir, "r_five_w_one_h_readiness_report.csv"), row.names = FALSE)
write.csv(question_coverage, file.path(tables_dir, "r_five_w_one_h_question_coverage_report.csv"), row.names = FALSE)
write.csv(audience_summary, file.path(tables_dir, "r_five_w_one_h_audience_summary_report.csv"), row.names = FALSE)
write.csv(asset_type_summary, file.path(tables_dir, "r_five_w_one_h_asset_type_summary_report.csv"), row.names = FALSE)
write.csv(governance_queue, file.path(tables_dir, "r_five_w_one_h_governance_queue.csv"), row.names = FALSE)
write.csv(catalog, file.path(catalog_dir, "r_five_w_one_h_catalog_export.csv"), row.names = FALSE)

png(file.path(figures_dir, "r_five_w_one_h_readiness_scores.png"), width = 1200, height = 800)
barplot(assets$explanatory_readiness_score, names.arg = assets$asset_id, las = 2, main = "5W1H Explanatory Readiness Scores", ylab = "Readiness score")
dev.off()

png(file.path(figures_dir, "r_five_w_one_h_question_coverage.png"), width = 1000, height = 700)
barplot(question_coverage$answer_rate, names.arg = question_coverage$question, las = 2, main = "5W1H Question Coverage", ylab = "Answer rate")
dev.off()

writeLines(c(
  "# 5W1H and the Architecture of Explanatory Completeness: R Audit",
  "",
  paste0("- Content assets: ", nrow(assets)),
  paste0("- Manual review queue records: ", nrow(review_queue)),
  paste0("- Average explanatory readiness score: ", round(mean(assets$explanatory_readiness_score), 4)),
  paste0("- Assets requiring governance review: ", nrow(governance_queue))
), file.path(reports_dir, "r_five_w_one_h_report.md"))

print("5W1H completeness R analysis complete.")
print(assets[, c("asset_id", "explanatory_readiness_score", "explanatory_status")])
