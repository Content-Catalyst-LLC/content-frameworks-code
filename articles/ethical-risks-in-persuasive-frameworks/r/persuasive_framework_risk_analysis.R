# Base R workflow for ethical-risk audits of persuasive frameworks.

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

assets <- read.csv(file.path(data_dir, "persuasive_framework_risk_inventory.csv"), stringsAsFactors = FALSE)
review_queue <- read.csv(file.path(data_dir, "editorial_review_queue.csv"), stringsAsFactors = FALSE)

yes <- function(x) tolower(trimws(x)) %in% c("yes", "true", "1", "present", "complete")

agency_fields <- c("clear_claim", "refusal_visible", "decision_support_present", "commitment_transparent")
pressure_fields <- c("uses_false_urgency", "uses_false_scarcity", "uses_fear_escalation", "uses_shame_pressure")
governance_fields <- c("review_owner_present", "evidence_reviewed", "accessibility_reviewed", "revision_queue_checked")
dark_pattern_fields <- c("hidden_terms", "cancellation_friction", "preselected_consent", "disguised_ad")

agency_matrix <- sapply(agency_fields, function(field) yes(assets[[field]]))
pressure_matrix <- sapply(pressure_fields, function(field) yes(assets[[field]]))
governance_matrix <- sapply(governance_fields, function(field) yes(assets[[field]]))
dark_pattern_matrix <- sapply(dark_pattern_fields, function(field) yes(assets[[field]]))

assets$agency_score <- round(rowMeans(agency_matrix), 4)
assets$pressure_score <- round(rowMeans(pressure_matrix), 4)
assets$governance_score <- round(rowMeans(governance_matrix), 4)
assets$dark_pattern_risk_score <- round(rowMeans(dark_pattern_matrix), 4)

assets$evidence_support_score <- round(
  pmin(assets$supported_persuasive_claims / pmax(assets$total_persuasive_claims, 1), 1),
  4
)

assets$accessibility_score <- round(
  (
    yes(assets$plain_language_present) +
      yes(assets$keyboard_path_clear) +
      yes(assets$contrast_and_readability_checked) +
      yes(assets$terms_accessible_before_action)
  ) / 4,
  4
)

assets$vulnerability_risk_score <- round(
  (
    yes(assets$high_stakes_context) +
      yes(assets$financial_or_health_pressure) +
      yes(assets$audience_dependency_present) +
      yes(assets$time_pressure_present)
  ) / 4,
  4
)

assets$responsible_persuasion_score <- round(
  pmax(
    0,
    pmin(
      1,
      0.24 * assets$agency_score +
        0.24 * assets$evidence_support_score +
        0.18 * assets$governance_score +
        0.14 * assets$accessibility_score -
        0.12 * assets$pressure_score -
        0.08 * assets$vulnerability_risk_score -
        0.10 * assets$dark_pattern_risk_score
    )
  ),
  4
)

assets$ethical_status <- ifelse(
  assets$responsible_persuasion_score >= 0.78 &
    assets$pressure_score <= 0.25 &
    assets$evidence_support_score >= 0.70 &
    assets$dark_pattern_risk_score == 0,
  "ready",
  "governance review"
)

framework_summary <- aggregate(responsible_persuasion_score ~ framework_used, data = assets, FUN = mean)
names(framework_summary) <- c("framework_used", "average_responsible_persuasion_score")
framework_summary$average_responsible_persuasion_score <- round(framework_summary$average_responsible_persuasion_score, 4)

audience_summary <- aggregate(responsible_persuasion_score ~ audience, data = assets, FUN = mean)
names(audience_summary) <- c("audience", "average_responsible_persuasion_score")
audience_summary$average_responsible_persuasion_score <- round(audience_summary$average_responsible_persuasion_score, 4)

risk_summary <- data.frame(
  risk_dimension = c(
    "agency_score",
    "pressure_score",
    "evidence_support_score",
    "governance_score",
    "accessibility_score",
    "vulnerability_risk_score",
    "dark_pattern_risk_score",
    "responsible_persuasion_score"
  ),
  average_score = c(
    mean(assets$agency_score),
    mean(assets$pressure_score),
    mean(assets$evidence_support_score),
    mean(assets$governance_score),
    mean(assets$accessibility_score),
    mean(assets$vulnerability_risk_score),
    mean(assets$dark_pattern_risk_score),
    mean(assets$responsible_persuasion_score)
  )
)

risk_summary$average_score <- round(risk_summary$average_score, 4)

governance_queue <- subset(assets, ethical_status == "governance review")

catalog <- assets[, c(
  "asset_id",
  "asset_name",
  "asset_type",
  "framework_used",
  "audience",
  "requested_action",
  "responsible_persuasion_score",
  "ethical_status"
)]

catalog$series <- "Content Frameworks"
catalog$article_slug <- "ethical-risks-in-persuasive-frameworks"
catalog$github_path <- "articles/ethical-risks-in-persuasive-frameworks/"

write.csv(assets, file.path(tables_dir, "r_persuasive_framework_risk_report.csv"), row.names = FALSE)
write.csv(framework_summary, file.path(tables_dir, "r_persuasive_framework_summary_report.csv"), row.names = FALSE)
write.csv(audience_summary, file.path(tables_dir, "r_persuasive_framework_audience_summary_report.csv"), row.names = FALSE)
write.csv(risk_summary, file.path(tables_dir, "r_persuasive_framework_risk_summary_report.csv"), row.names = FALSE)
write.csv(governance_queue, file.path(tables_dir, "r_persuasive_framework_governance_queue.csv"), row.names = FALSE)
write.csv(catalog, file.path(catalog_dir, "r_persuasive_framework_catalog_export.csv"), row.names = FALSE)

png(file.path(figures_dir, "r_responsible_persuasion_scores.png"), width = 1200, height = 800)
barplot(assets$responsible_persuasion_score, names.arg = assets$asset_id, las = 2, main = "Responsible Persuasion Scores", ylab = "Responsible persuasion score")
dev.off()

png(file.path(figures_dir, "r_persuasive_risk_summary.png"), width = 1100, height = 750)
barplot(risk_summary$average_score, names.arg = risk_summary$risk_dimension, las = 2, main = "Persuasive Framework Risk Summary", ylab = "Average score")
dev.off()

writeLines(c(
  "# Ethical Risks in Persuasive Frameworks: R Audit",
  "",
  paste0("- Content assets: ", nrow(assets)),
  paste0("- Manual review queue records: ", nrow(review_queue)),
  paste0("- Average responsible persuasion score: ", round(mean(assets$responsible_persuasion_score), 4)),
  paste0("- Assets requiring governance review: ", nrow(governance_queue))
), file.path(reports_dir, "r_persuasive_framework_risk_report.md"))

print("Persuasive framework R risk analysis complete.")
print(assets[, c("asset_id", "framework_used", "responsible_persuasion_score", "ethical_status")])
