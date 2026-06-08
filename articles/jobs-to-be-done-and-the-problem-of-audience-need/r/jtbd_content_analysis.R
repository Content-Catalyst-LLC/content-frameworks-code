# Base R workflow for Jobs to Be Done content audits.

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

assets <- read.csv(file.path(data_dir, "jtbd_content_inventory.csv"), stringsAsFactors = FALSE)
review_queue <- read.csv(file.path(data_dir, "editorial_review_queue.csv"), stringsAsFactors = FALSE)

yes <- function(x) tolower(trimws(x)) %in% c("yes", "true", "1", "present", "complete", "ready")

job_dimensions <- c("functional", "emotional", "social", "strategic", "learning")

dimension_matrix <- sapply(job_dimensions, function(dimension) {
  yes(assets[[paste0(dimension, "_job_supported")]])
})

assets$job_dimension_support_score <- round(rowMeans(dimension_matrix), 4)

assets$job_clarity_score <- round(
  (
    yes(assets$situation_defined) +
      yes(assets$motivation_defined) +
      yes(assets$desired_outcome_defined) +
      yes(assets$constraint_defined)
  ) / 4,
  4
)

assets$content_fit_score <- round(
  (
    yes(assets$format_matches_job) +
      yes(assets$examples_match_job) +
      yes(assets$sections_match_job) +
      yes(assets$next_step_matches_job)
  ) / 4,
  4
)

assets$evidence_support_score <- round(
  pmin(assets$supported_job_assumptions / pmax(assets$total_job_assumptions, 1), 1),
  4
)

assets$outcome_support_score <- round(
  (
    yes(assets$success_criteria_defined) +
      yes(assets$measurement_matches_job) +
      yes(assets$content_supports_progress)
  ) / 3,
  4
)

assets$agency_score <- round(
  (
    yes(assets$audience_choice_preserved) +
      yes(assets$alternatives_visible) +
      yes(assets$claims_bounded)
  ) / 3,
  4
)

assets$governance_score <- round(
  (
    yes(assets$review_owner_present) +
      yes(assets$last_review_date_present) +
      yes(assets$revision_queue_checked) +
      yes(assets$job_assumption_reviewed)
  ) / 4,
  4
)

assets$jtbd_readiness_score <- round(
  0.24 * assets$job_clarity_score +
    0.22 * assets$content_fit_score +
    0.20 * assets$evidence_support_score +
    0.14 * assets$outcome_support_score +
    0.10 * assets$agency_score +
    0.10 * assets$governance_score,
  4
)

assets$jtbd_status <- ifelse(
  assets$jtbd_readiness_score >= 0.78 &
    assets$evidence_support_score >= 0.70 &
    assets$content_fit_score >= 0.70,
  "ready",
  "governance review"
)

job_summary <- aggregate(jtbd_readiness_score ~ primary_job, data = assets, FUN = mean)
names(job_summary) <- c("primary_job", "average_jtbd_readiness")
job_summary$average_jtbd_readiness <- round(job_summary$average_jtbd_readiness, 4)

audience_summary <- aggregate(jtbd_readiness_score ~ audience, data = assets, FUN = mean)
names(audience_summary) <- c("audience", "average_jtbd_readiness")
audience_summary$average_jtbd_readiness <- round(audience_summary$average_jtbd_readiness, 4)

asset_type_summary <- aggregate(jtbd_readiness_score ~ asset_type, data = assets, FUN = mean)
names(asset_type_summary) <- c("asset_type", "average_jtbd_readiness")
asset_type_summary$average_jtbd_readiness <- round(asset_type_summary$average_jtbd_readiness, 4)

dimension_summary <- data.frame(
  job_dimension = job_dimensions,
  assets_supporting_dimension = colSums(dimension_matrix),
  support_rate = round(colMeans(dimension_matrix), 4)
)

governance_queue <- subset(assets, jtbd_status == "governance review")

catalog <- assets[, c(
  "asset_id",
  "asset_name",
  "asset_type",
  "primary_job",
  "audience",
  "jtbd_readiness_score",
  "jtbd_status"
)]

catalog$series <- "Content Frameworks"
catalog$article_slug <- "jobs-to-be-done-and-the-problem-of-audience-need"
catalog$github_path <- "articles/jobs-to-be-done-and-the-problem-of-audience-need/"

write.csv(assets, file.path(tables_dir, "r_jtbd_content_readiness_report.csv"), row.names = FALSE)
write.csv(job_summary, file.path(tables_dir, "r_jtbd_job_summary_report.csv"), row.names = FALSE)
write.csv(audience_summary, file.path(tables_dir, "r_jtbd_audience_summary_report.csv"), row.names = FALSE)
write.csv(asset_type_summary, file.path(tables_dir, "r_jtbd_asset_type_summary_report.csv"), row.names = FALSE)
write.csv(dimension_summary, file.path(tables_dir, "r_jtbd_dimension_summary_report.csv"), row.names = FALSE)
write.csv(governance_queue, file.path(tables_dir, "r_jtbd_governance_queue.csv"), row.names = FALSE)
write.csv(catalog, file.path(catalog_dir, "r_jtbd_catalog_export.csv"), row.names = FALSE)

png(file.path(figures_dir, "r_jtbd_readiness_scores.png"), width = 1200, height = 800)
barplot(assets$jtbd_readiness_score, names.arg = assets$asset_id, las = 2, main = "JTBD Content Readiness Scores", ylab = "JTBD readiness score")
dev.off()

png(file.path(figures_dir, "r_jtbd_dimension_support.png"), width = 1100, height = 750)
barplot(dimension_summary$support_rate, names.arg = dimension_summary$job_dimension, las = 2, main = "Audience Job Dimension Support", ylab = "Support rate")
dev.off()

writeLines(c(
  "# Jobs to Be Done and the Problem of Audience Need: R Audit",
  "",
  paste0("- Content assets: ", nrow(assets)),
  paste0("- Manual review queue records: ", nrow(review_queue)),
  paste0("- Average JTBD readiness score: ", round(mean(assets$jtbd_readiness_score), 4)),
  paste0("- Assets requiring governance review: ", nrow(governance_queue))
), file.path(reports_dir, "r_jtbd_content_report.md"))

print("JTBD content R analysis complete.")
print(assets[, c("asset_id", "primary_job", "jtbd_readiness_score", "jtbd_status")])
