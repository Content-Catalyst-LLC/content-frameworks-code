# Base R workflow for storytelling framework audits.

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

assets <- read.csv(file.path(data_dir, "storytelling_framework_inventory.csv"), stringsAsFactors = FALSE)
review_queue <- read.csv(file.path(data_dir, "editorial_review_queue.csv"), stringsAsFactors = FALSE)

yes <- function(x) tolower(trimws(x)) %in% c("yes", "true", "1", "ready", "complete")

balance_score <- function(values) {
  mean_value <- mean(values)
  if (mean_value == 0) return(0)
  balance <- 1 - min(sd(values) / mean_value, 1)
  max(0, min(balance, 1))
}

dimensions <- c("context", "actors", "tension", "sequence", "transformation", "action")

dimension_matrix <- sapply(dimensions, function(dimension) yes(assets[[paste0(dimension, "_present")]]))
support_matrix <- sapply(dimensions, function(dimension) yes(assets[[paste0(dimension, "_supported")]]))

assets$narrative_completeness_score <- round(rowMeans(dimension_matrix), 4)

supported_dimension_counts <- rowSums(dimension_matrix & support_matrix)
present_dimension_counts <- rowSums(dimension_matrix)

assets$evidence_support_score <- ifelse(
  present_dimension_counts == 0,
  0,
  supported_dimension_counts / present_dimension_counts
)

assets$evidence_support_score <- round(assets$evidence_support_score, 4)

assets$narrative_balance_score <- apply(dimension_matrix, 1, balance_score)
assets$narrative_balance_score <- round(assets$narrative_balance_score, 4)

assets$agency_score <- round(
  (
    yes(assets$affected_people_have_agency) +
      yes(assets$institutional_responsibility_visible) +
      yes(assets$audience_agency_preserved)
  ) / 3,
  4
)

assets$transformation_credibility_score <- round(
  (
    yes(assets$transformation_bounded) +
      yes(assets$mechanism_visible) +
      yes(assets$limitations_present)
  ) / 3,
  4
)

assets$governance_score <- round(
  (
    yes(assets$review_owner_present) +
      yes(assets$consent_or_source_context_present) +
      yes(assets$last_review_date_present) +
      yes(assets$revision_queue_checked)
  ) / 4,
  4
)

assets$ethical_review_score <- round(
  (
    !yes(assets$uses_savior_framing) +
      !yes(assets$overdramatizes_tension) +
      !yes(assets$uses_unsupported_anecdote) +
      !yes(assets$uses_pressure_cta)
  ) / 4,
  4
)

assets$storytelling_readiness_score <- round(
  0.24 * assets$narrative_completeness_score +
    0.22 * assets$evidence_support_score +
    0.18 * assets$agency_score +
    0.16 * assets$transformation_credibility_score +
    0.12 * assets$governance_score +
    0.08 * assets$ethical_review_score,
  4
)

assets$storytelling_status <- ifelse(
  assets$storytelling_readiness_score >= 0.78 &
    assets$evidence_support_score >= 0.70 &
    assets$governance_score >= 0.70,
  "ready",
  "governance review"
)

dimension_summary <- data.frame(
  narrative_dimension = dimensions,
  assets_with_dimension = colSums(dimension_matrix),
  assets_with_support = colSums(dimension_matrix & support_matrix)
)

dimension_summary$presence_rate <- round(dimension_summary$assets_with_dimension / nrow(assets), 4)
dimension_summary$support_rate <- ifelse(
  dimension_summary$assets_with_dimension == 0,
  0,
  round(dimension_summary$assets_with_support / dimension_summary$assets_with_dimension, 4)
)

audience_summary <- aggregate(storytelling_readiness_score ~ audience, data = assets, FUN = mean)
names(audience_summary) <- c("audience", "average_storytelling_readiness")
audience_summary$average_storytelling_readiness <- round(audience_summary$average_storytelling_readiness, 4)

story_purpose_summary <- aggregate(storytelling_readiness_score ~ story_purpose, data = assets, FUN = mean)
names(story_purpose_summary) <- c("story_purpose", "average_storytelling_readiness")
story_purpose_summary$average_storytelling_readiness <- round(story_purpose_summary$average_storytelling_readiness, 4)

governance_queue <- subset(assets, storytelling_status == "governance review")

catalog <- assets[, c(
  "asset_id",
  "asset_name",
  "asset_type",
  "story_purpose",
  "audience",
  "storytelling_readiness_score",
  "storytelling_status"
)]

catalog$series <- "Content Frameworks"
catalog$article_slug <- "storytelling-frameworks-for-transformation-and-action"
catalog$github_path <- "articles/storytelling-frameworks-for-transformation-and-action/"

write.csv(assets, file.path(tables_dir, "r_storytelling_readiness_report.csv"), row.names = FALSE)
write.csv(dimension_summary, file.path(tables_dir, "r_storytelling_dimension_summary_report.csv"), row.names = FALSE)
write.csv(audience_summary, file.path(tables_dir, "r_storytelling_audience_summary_report.csv"), row.names = FALSE)
write.csv(story_purpose_summary, file.path(tables_dir, "r_storytelling_purpose_summary_report.csv"), row.names = FALSE)
write.csv(governance_queue, file.path(tables_dir, "r_storytelling_governance_queue.csv"), row.names = FALSE)
write.csv(catalog, file.path(catalog_dir, "r_storytelling_catalog_export.csv"), row.names = FALSE)

png(file.path(figures_dir, "r_storytelling_readiness_scores.png"), width = 1200, height = 800)
barplot(assets$storytelling_readiness_score, names.arg = assets$asset_id, las = 2, main = "Storytelling Framework Readiness Scores", ylab = "Readiness score")
dev.off()

png(file.path(figures_dir, "r_storytelling_dimension_presence.png"), width = 1100, height = 750)
barplot(dimension_summary$presence_rate, names.arg = dimension_summary$narrative_dimension, las = 2, main = "Narrative Dimension Presence", ylab = "Presence rate")
dev.off()

writeLines(c(
  "# Storytelling Frameworks for Transformation and Action: R Audit",
  "",
  paste0("- Content assets: ", nrow(assets)),
  paste0("- Manual review queue records: ", nrow(review_queue)),
  paste0("- Average storytelling readiness score: ", round(mean(assets$storytelling_readiness_score), 4)),
  paste0("- Assets requiring governance review: ", nrow(governance_queue))
), file.path(reports_dir, "r_storytelling_framework_report.md"))

print("Storytelling framework R analysis complete.")
print(assets[, c("asset_id", "story_purpose", "storytelling_readiness_score", "storytelling_status")])
