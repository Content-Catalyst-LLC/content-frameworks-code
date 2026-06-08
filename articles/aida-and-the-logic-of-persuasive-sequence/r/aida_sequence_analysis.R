# Base R workflow for AIDA sequence readiness.

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

messages <- read.csv(file.path(data_dir, "aida_message_inventory.csv"), stringsAsFactors = FALSE)
review_queue <- read.csv(file.path(data_dir, "editorial_review_queue.csv"), stringsAsFactors = FALSE)

yes <- function(x) tolower(trimws(x)) %in% c("yes", "true", "1", "ready", "complete")

stage_balance <- function(values) {
  mean_value <- mean(values)
  if (mean_value == 0) return(0)
  balance <- 1 - min(sd(values) / mean_value, 1)
  max(0, min(balance, 1))
}

messages$attention_score <- round(
  (
    yes(messages$headline_relevant) +
      yes(messages$opening_problem_clear) +
      yes(messages$attention_claim_supported)
  ) / 3,
  4
)

messages$interest_score <- round(
  (
    yes(messages$audience_relevance_visible) +
      yes(messages$context_provided) +
      yes(messages$evidence_or_example_present)
  ) / 3,
  4
)

messages$desire_score <- round(
  (
    yes(messages$value_proposition_clear) +
      yes(messages$benefit_claim_supported) +
      yes(messages$fit_and_limits_visible)
  ) / 3,
  4
)

messages$action_score <- round(
  (
    yes(messages$cta_clear) +
      yes(messages$cta_feasible) +
      yes(messages$commitment_transparent)
  ) / 3,
  4
)

messages$ethical_review_score <- round(
  (
    !yes(messages$uses_false_urgency) +
      !yes(messages$uses_exaggerated_claims) +
      !yes(messages$uses_hidden_cost_or_condition) +
      yes(messages$audience_agency_preserved)
  ) / 4,
  4
)

messages$stage_balance_score <- apply(
  messages[, c("attention_score", "interest_score", "desire_score", "action_score")],
  1,
  stage_balance
)

messages$stage_balance_score <- round(messages$stage_balance_score, 4)

messages$aida_readiness_score <- round(
  0.18 * messages$attention_score +
    0.20 * messages$interest_score +
    0.22 * messages$desire_score +
    0.20 * messages$action_score +
    0.20 * messages$ethical_review_score,
  4
)

messages$aida_status <- ifelse(
  messages$aida_readiness_score >= 0.78 & messages$ethical_review_score >= 0.70,
  "ready",
  "governance review"
)

stage_summary <- data.frame(
  stage_or_metric = c(
    "attention_score",
    "interest_score",
    "desire_score",
    "action_score",
    "ethical_review_score",
    "stage_balance_score"
  ),
  average_score = c(
    mean(messages$attention_score),
    mean(messages$interest_score),
    mean(messages$desire_score),
    mean(messages$action_score),
    mean(messages$ethical_review_score),
    mean(messages$stage_balance_score)
  )
)
stage_summary$average_score <- round(stage_summary$average_score, 4)

audience_summary <- aggregate(aida_readiness_score ~ audience, data = messages, FUN = mean)
names(audience_summary) <- c("audience", "average_aida_readiness")
audience_summary$average_aida_readiness <- round(audience_summary$average_aida_readiness, 4)

asset_type_summary <- aggregate(aida_readiness_score ~ asset_type, data = messages, FUN = mean)
names(asset_type_summary) <- c("asset_type", "average_aida_readiness")
asset_type_summary$average_aida_readiness <- round(asset_type_summary$average_aida_readiness, 4)

governance_queue <- subset(messages, aida_status == "governance review")

catalog <- messages[, c(
  "message_id",
  "asset_name",
  "asset_type",
  "audience",
  "aida_readiness_score",
  "aida_status"
)]

catalog$series <- "Content Frameworks"
catalog$article_slug <- "aida-and-the-logic-of-persuasive-sequence"
catalog$github_path <- "articles/aida-and-the-logic-of-persuasive-sequence/"

write.csv(messages, file.path(tables_dir, "r_aida_sequence_readiness_report.csv"), row.names = FALSE)
write.csv(stage_summary, file.path(tables_dir, "r_aida_stage_summary_report.csv"), row.names = FALSE)
write.csv(audience_summary, file.path(tables_dir, "r_aida_audience_summary_report.csv"), row.names = FALSE)
write.csv(asset_type_summary, file.path(tables_dir, "r_aida_asset_type_summary_report.csv"), row.names = FALSE)
write.csv(governance_queue, file.path(tables_dir, "r_aida_governance_queue.csv"), row.names = FALSE)
write.csv(catalog, file.path(catalog_dir, "r_aida_sequence_catalog_export.csv"), row.names = FALSE)

png(file.path(figures_dir, "r_aida_readiness_scores.png"), width = 1200, height = 800)
barplot(messages$aida_readiness_score, names.arg = messages$message_id, las = 2, main = "AIDA Readiness Scores", ylab = "Readiness score")
dev.off()

png(file.path(figures_dir, "r_aida_stage_summary.png"), width = 1000, height = 700)
barplot(stage_summary$average_score, names.arg = stage_summary$stage_or_metric, las = 2, main = "Average AIDA Stage Scores", ylab = "Average score")
dev.off()

writeLines(c(
  "# AIDA and the Logic of Persuasive Sequence: R Audit",
  "",
  paste0("- Message records: ", nrow(messages)),
  paste0("- Manual review queue records: ", nrow(review_queue)),
  paste0("- Average AIDA readiness score: ", round(mean(messages$aida_readiness_score), 4)),
  paste0("- Assets requiring governance review: ", nrow(governance_queue))
), file.path(reports_dir, "r_aida_sequence_report.md"))

print("AIDA sequence R analysis complete.")
print(messages[, c("message_id", "aida_readiness_score", "aida_status")])
