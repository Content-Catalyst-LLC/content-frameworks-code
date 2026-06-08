# Base R workflow for hierarchy-of-effects and communication response audits.

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

assets <- read.csv(file.path(data_dir, "communication_response_inventory.csv"), stringsAsFactors = FALSE)
review_queue <- read.csv(file.path(data_dir, "editorial_review_queue.csv"), stringsAsFactors = FALSE)

yes <- function(x) tolower(trimws(x)) %in% c("yes", "true", "1", "ready", "complete")

balance_score <- function(values) {
  mean_value <- mean(values)
  if (mean_value == 0) return(0)
  balance <- 1 - min(sd(values) / mean_value, 1)
  max(0, min(balance, 1))
}

stages <- c("awareness", "knowledge", "liking", "preference", "conviction", "action", "follow_through")

stage_matrix <- sapply(stages, function(stage) yes(assets[[paste0(stage, "_supported")]]))
evidence_matrix <- sapply(stages, function(stage) yes(assets[[paste0(stage, "_evidence_present")]]))

assets$stage_coverage_score <- round(rowMeans(stage_matrix), 4)

supported_evidence_counts <- rowSums(stage_matrix & evidence_matrix)
supported_stage_counts <- rowSums(stage_matrix)

assets$evidence_support_score <- ifelse(
  supported_stage_counts == 0,
  0,
  supported_evidence_counts / supported_stage_counts
)

assets$evidence_support_score <- round(assets$evidence_support_score, 4)

assets$stage_balance_score <- apply(stage_matrix, 1, balance_score)
assets$stage_balance_score <- round(assets$stage_balance_score, 4)

assets$audience_fit_score <- round(
  (
    yes(assets$audience_context_present) +
      yes(assets$audience_readiness_defined) +
      yes(assets$next_step_matches_stage)
  ) / 3,
  4
)

assets$governance_score <- round(
  (
    yes(assets$measurement_aligned) +
      yes(assets$review_owner_present) +
      yes(assets$last_review_date_present) +
      yes(assets$revision_queue_checked)
  ) / 4,
  4
)

assets$ethical_review_score <- round(
  (
    !yes(assets$uses_false_urgency) +
      !yes(assets$overclaims_response) +
      !yes(assets$uses_pressure_cta) +
      yes(assets$audience_agency_preserved)
  ) / 4,
  4
)

assets$response_readiness_score <- round(
  0.22 * assets$stage_coverage_score +
    0.22 * assets$evidence_support_score +
    0.16 * assets$stage_balance_score +
    0.16 * assets$audience_fit_score +
    0.14 * assets$governance_score +
    0.10 * assets$ethical_review_score,
  4
)

assets$response_status <- ifelse(
  assets$response_readiness_score >= 0.78 & assets$governance_score >= 0.70,
  "ready",
  "governance review"
)

stage_summary <- data.frame(
  response_stage = stages,
  assets_supporting_stage = colSums(stage_matrix),
  assets_with_evidence = colSums(stage_matrix & evidence_matrix)
)

stage_summary$support_rate <- round(stage_summary$assets_supporting_stage / nrow(assets), 4)
stage_summary$evidence_rate <- ifelse(
  stage_summary$assets_supporting_stage == 0,
  0,
  round(stage_summary$assets_with_evidence / stage_summary$assets_supporting_stage, 4)
)

audience_summary <- aggregate(response_readiness_score ~ audience, data = assets, FUN = mean)
names(audience_summary) <- c("audience", "average_response_readiness")
audience_summary$average_response_readiness <- round(audience_summary$average_response_readiness, 4)

asset_type_summary <- aggregate(response_readiness_score ~ asset_type, data = assets, FUN = mean)
names(asset_type_summary) <- c("asset_type", "average_response_readiness")
asset_type_summary$average_response_readiness <- round(asset_type_summary$average_response_readiness, 4)

governance_queue <- subset(assets, response_status == "governance review")

catalog <- assets[, c(
  "asset_id",
  "asset_name",
  "asset_type",
  "primary_response_stage",
  "audience",
  "response_readiness_score",
  "response_status"
)]

catalog$series <- "Content Frameworks"
catalog$article_slug <- "hierarchy-of-effects-and-communication-response-models"
catalog$github_path <- "articles/hierarchy-of-effects-and-communication-response-models/"

write.csv(assets, file.path(tables_dir, "r_communication_response_readiness_report.csv"), row.names = FALSE)
write.csv(stage_summary, file.path(tables_dir, "r_communication_response_stage_summary_report.csv"), row.names = FALSE)
write.csv(audience_summary, file.path(tables_dir, "r_communication_response_audience_summary_report.csv"), row.names = FALSE)
write.csv(asset_type_summary, file.path(tables_dir, "r_communication_response_asset_type_summary_report.csv"), row.names = FALSE)
write.csv(governance_queue, file.path(tables_dir, "r_communication_response_governance_queue.csv"), row.names = FALSE)
write.csv(catalog, file.path(catalog_dir, "r_communication_response_catalog_export.csv"), row.names = FALSE)

png(file.path(figures_dir, "r_communication_response_readiness_scores.png"), width = 1200, height = 800)
barplot(assets$response_readiness_score, names.arg = assets$asset_id, las = 2, main = "Communication Response Readiness Scores", ylab = "Readiness score")
dev.off()

png(file.path(figures_dir, "r_communication_response_stage_support.png"), width = 1100, height = 750)
barplot(stage_summary$support_rate, names.arg = stage_summary$response_stage, las = 2, main = "Response Stage Support", ylab = "Support rate")
dev.off()

writeLines(c(
  "# Hierarchy of Effects and Communication Response Models: R Audit",
  "",
  paste0("- Content assets: ", nrow(assets)),
  paste0("- Manual review queue records: ", nrow(review_queue)),
  paste0("- Average response readiness score: ", round(mean(assets$response_readiness_score), 4)),
  paste0("- Assets requiring governance review: ", nrow(governance_queue))
), file.path(reports_dir, "r_communication_response_report.md"))

print("Communication response R analysis complete.")
print(assets[, c("asset_id", "primary_response_stage", "response_readiness_score", "response_status")])
