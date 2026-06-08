# Base R workflow for PAS/BAB tension and transformation readiness.

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

messages <- read.csv(file.path(data_dir, "pas_bab_message_inventory.csv"), stringsAsFactors = FALSE)
review_queue <- read.csv(file.path(data_dir, "editorial_review_queue.csv"), stringsAsFactors = FALSE)

yes <- function(x) tolower(trimws(x)) %in% c("yes", "true", "1", "ready", "complete")

sequence_balance <- function(values) {
  mean_value <- mean(values)
  if (mean_value == 0) return(0)
  balance <- 1 - min(sd(values) / mean_value, 1)
  max(0, min(balance, 1))
}

messages$current_state_score <- round(
  (
    yes(messages$problem_clear) +
      yes(messages$before_state_specific) +
      yes(messages$audience_context_present)
  ) / 3,
  4
)

messages$stakes_score <- round(
  (
    yes(messages$stakes_visible) +
      yes(messages$agitation_proportionate) +
      yes(messages$consequence_supported)
  ) / 3,
  4
)

messages$transformation_score <- round(
  (
    yes(messages$after_state_credible) +
      yes(messages$transformation_bounded) +
      yes(messages$benefit_claim_supported)
  ) / 3,
  4
)

messages$bridge_score <- round(
  (
    yes(messages$solution_fit_clear) +
      yes(messages$bridge_mechanism_visible) +
      yes(messages$commitment_transparent)
  ) / 3,
  4
)

messages$ethical_review_score <- round(
  (
    !yes(messages$uses_invented_pain) +
      !yes(messages$uses_fear_escalation) +
      !yes(messages$uses_false_urgency) +
      yes(messages$audience_agency_preserved)
  ) / 4,
  4
)

messages$sequence_balance_score <- apply(
  messages[, c("current_state_score", "stakes_score", "transformation_score", "bridge_score")],
  1,
  sequence_balance
)

messages$sequence_balance_score <- round(messages$sequence_balance_score, 4)

messages$pas_bab_readiness_score <- round(
  0.20 * messages$current_state_score +
    0.20 * messages$stakes_score +
    0.20 * messages$transformation_score +
    0.20 * messages$bridge_score +
    0.20 * messages$ethical_review_score,
  4
)

messages$pas_bab_status <- ifelse(
  messages$pas_bab_readiness_score >= 0.78 & messages$ethical_review_score >= 0.70,
  "ready",
  "governance review"
)

stage_summary <- data.frame(
  stage_or_metric = c(
    "current_state_score",
    "stakes_score",
    "transformation_score",
    "bridge_score",
    "ethical_review_score",
    "sequence_balance_score"
  ),
  average_score = c(
    mean(messages$current_state_score),
    mean(messages$stakes_score),
    mean(messages$transformation_score),
    mean(messages$bridge_score),
    mean(messages$ethical_review_score),
    mean(messages$sequence_balance_score)
  )
)
stage_summary$average_score <- round(stage_summary$average_score, 4)

framework_summary <- aggregate(pas_bab_readiness_score ~ framework_used, data = messages, FUN = mean)
names(framework_summary) <- c("framework_used", "average_pas_bab_readiness")
framework_summary$average_pas_bab_readiness <- round(framework_summary$average_pas_bab_readiness, 4)

audience_summary <- aggregate(pas_bab_readiness_score ~ audience, data = messages, FUN = mean)
names(audience_summary) <- c("audience", "average_pas_bab_readiness")
audience_summary$average_pas_bab_readiness <- round(audience_summary$average_pas_bab_readiness, 4)

governance_queue <- subset(messages, pas_bab_status == "governance review")

catalog <- messages[, c(
  "message_id",
  "asset_name",
  "asset_type",
  "framework_used",
  "audience",
  "pas_bab_readiness_score",
  "pas_bab_status"
)]

catalog$series <- "Content Frameworks"
catalog$article_slug <- "pas-bab-and-the-structure-of-tension-and-transformation"
catalog$github_path <- "articles/pas-bab-and-the-structure-of-tension-and-transformation/"

write.csv(messages, file.path(tables_dir, "r_pas_bab_sequence_readiness_report.csv"), row.names = FALSE)
write.csv(stage_summary, file.path(tables_dir, "r_pas_bab_stage_summary_report.csv"), row.names = FALSE)
write.csv(framework_summary, file.path(tables_dir, "r_pas_bab_framework_summary_report.csv"), row.names = FALSE)
write.csv(audience_summary, file.path(tables_dir, "r_pas_bab_audience_summary_report.csv"), row.names = FALSE)
write.csv(governance_queue, file.path(tables_dir, "r_pas_bab_governance_queue.csv"), row.names = FALSE)
write.csv(catalog, file.path(catalog_dir, "r_pas_bab_sequence_catalog_export.csv"), row.names = FALSE)

png(file.path(figures_dir, "r_pas_bab_readiness_scores.png"), width = 1200, height = 800)
barplot(messages$pas_bab_readiness_score, names.arg = messages$message_id, las = 2, main = "PAS/BAB Readiness Scores", ylab = "Readiness score")
dev.off()

png(file.path(figures_dir, "r_pas_bab_stage_summary.png"), width = 1000, height = 700)
barplot(stage_summary$average_score, names.arg = stage_summary$stage_or_metric, las = 2, main = "Average PAS/BAB Stage Scores", ylab = "Average score")
dev.off()

writeLines(c(
  "# PAS, BAB, and the Structure of Tension and Transformation: R Audit",
  "",
  paste0("- Message records: ", nrow(messages)),
  paste0("- Manual review queue records: ", nrow(review_queue)),
  paste0("- Average PAS/BAB readiness score: ", round(mean(messages$pas_bab_readiness_score), 4)),
  paste0("- Assets requiring governance review: ", nrow(governance_queue))
), file.path(reports_dir, "r_pas_bab_sequence_report.md"))

print("PAS/BAB sequence R analysis complete.")
print(messages[, c("message_id", "framework_used", "pas_bab_readiness_score", "pas_bab_status")])
