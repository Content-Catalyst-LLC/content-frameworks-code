# Base R workflow for evidence architecture readiness.

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

articles <- read.csv(file.path(data_dir, "evidence_architecture_inventory.csv"), stringsAsFactors = FALSE)
claims <- read.csv(file.path(data_dir, "claim_inventory.csv"), stringsAsFactors = FALSE)
sources <- read.csv(file.path(data_dir, "source_inventory.csv"), stringsAsFactors = FALSE)
visuals <- read.csv(file.path(data_dir, "visual_evidence_inventory.csv"), stringsAsFactors = FALSE)
review_queue <- read.csv(file.path(data_dir, "editorial_review_queue.csv"), stringsAsFactors = FALSE)

yes <- function(x) tolower(trimws(x)) %in% c("yes", "true", "1", "ready", "complete")

source_type_summary <- as.data.frame(table(sources$source_type), stringsAsFactors = FALSE)
names(source_type_summary) <- c("source_type", "source_count")

authority_summary <- as.data.frame(table(sources$authority_level), stringsAsFactors = FALSE)
names(authority_summary) <- c("authority_level", "source_count")

claims_sources <- merge(
  claims,
  sources[, c("source_id", "source_type", "authority_level", "review_status")],
  by = "source_id",
  all.x = TRUE
)

claims_sources$source_quality_score <- ifelse(
  claims_sources$authority_level == "high",
  1,
  ifelse(claims_sources$authority_level == "medium", 0.75, ifelse(claims_sources$authority_level == "low", 0.45, 0))
)

claims_sources$direct_support_score <- ifelse(yes(claims_sources$direct_support), 1, 0.45)

claims_sources$claim_support_score <- round(
  claims_sources$source_quality_score * claims_sources$direct_support_score,
  4
)

claim_report <- claims_sources[, c(
  "claim_id",
  "article_slug",
  "claim_type",
  "claim_strength",
  "source_id",
  "source_type",
  "authority_level",
  "direct_support",
  "claim_support_score"
)]

claim_scores <- aggregate(claim_support_score ~ article_slug, data = claim_report, FUN = mean)
names(claim_scores) <- c("article_slug", "claim_support_score")

source_quality_scores <- aggregate(source_quality_score ~ article_slug, data = claims_sources, FUN = mean)
names(source_quality_scores) <- c("article_slug", "source_quality_score")

visuals$visual_support_score <- round(
  (
    yes(visuals$source_visible) +
      yes(visuals$caption_explains_claim) +
      yes(visuals$alt_text_present) +
      yes(visuals$visual_limitations_visible)
  ) / 4,
  4
)

visual_scores <- aggregate(visual_support_score ~ article_slug, data = visuals, FUN = mean)
names(visual_scores) <- c("article_slug", "visual_support_score")

readiness <- merge(articles, claim_scores, by = "article_slug", all.x = TRUE)
readiness <- merge(readiness, source_quality_scores, by = "article_slug", all.x = TRUE)
readiness <- merge(readiness, visual_scores, by = "article_slug", all.x = TRUE)

readiness$claim_support_score[is.na(readiness$claim_support_score)] <- 0
readiness$source_quality_score[is.na(readiness$source_quality_score)] <- 0
readiness$visual_support_score[is.na(readiness$visual_support_score)] <- 1

readiness$uncertainty_visibility_score <- round(
  (
    yes(readiness$limitations_visible) +
      yes(readiness$uncertainty_visible) +
      yes(readiness$assumptions_visible) +
      yes(readiness$confidence_language_present)
  ) / 4,
  4
)

readiness$review_readiness_score <- round(
  (
    yes(readiness$source_review_complete) +
      yes(readiness$last_review_date_present) +
      yes(readiness$revision_queue_checked)
  ) / 3,
  4
)

readiness$evidence_architecture_readiness <- round(
  0.30 * readiness$claim_support_score +
    0.20 * readiness$source_quality_score +
    0.20 * readiness$uncertainty_visibility_score +
    0.12 * readiness$visual_support_score +
    0.18 * readiness$review_readiness_score,
  4
)

readiness$evidence_architecture_status <- ifelse(
  readiness$evidence_architecture_readiness >= 0.78,
  "ready",
  "governance review"
)

governance_queue <- subset(
  readiness,
  status == "published" & evidence_architecture_status == "governance review"
)

catalog <- readiness[, c(
  "article_slug",
  "title",
  "evidence_architecture_readiness",
  "evidence_architecture_status"
)]

catalog$series <- "Content Frameworks"
catalog$github_path <- paste0("articles/", catalog$article_slug, "/")

write.csv(source_type_summary, file.path(tables_dir, "r_source_type_summary.csv"), row.names = FALSE)
write.csv(authority_summary, file.path(tables_dir, "r_authority_summary.csv"), row.names = FALSE)
write.csv(claim_report, file.path(tables_dir, "r_claim_support_report.csv"), row.names = FALSE)
write.csv(visuals, file.path(tables_dir, "r_visual_evidence_support_report.csv"), row.names = FALSE)
write.csv(readiness, file.path(tables_dir, "r_evidence_architecture_readiness_report.csv"), row.names = FALSE)
write.csv(governance_queue, file.path(tables_dir, "r_evidence_architecture_governance_queue.csv"), row.names = FALSE)
write.csv(catalog, file.path(catalog_dir, "r_evidence_architecture_catalog_export.csv"), row.names = FALSE)

png(file.path(figures_dir, "r_evidence_architecture_readiness.png"), width = 1200, height = 800)
barplot(readiness$evidence_architecture_readiness, names.arg = readiness$article_slug, las = 2, main = "Evidence Architecture Readiness", ylab = "Readiness score")
dev.off()

png(file.path(figures_dir, "r_source_authority_distribution.png"), width = 1000, height = 700)
barplot(authority_summary$source_count, names.arg = authority_summary$authority_level, main = "Source Authority Distribution", ylab = "Source count")
dev.off()

png(file.path(figures_dir, "r_uncertainty_visibility.png"), width = 1200, height = 800)
barplot(readiness$uncertainty_visibility_score, names.arg = readiness$article_slug, las = 2, main = "Uncertainty Visibility", ylab = "Uncertainty visibility score")
dev.off()

writeLines(c(
  "# Evidence Architecture in Explanatory Content: R Audit",
  "",
  paste0("- Evidence architecture records: ", nrow(articles)),
  paste0("- Claim records: ", nrow(claims)),
  paste0("- Source records: ", nrow(sources)),
  paste0("- Visual evidence records: ", nrow(visuals)),
  paste0("- Manual review queue records: ", nrow(review_queue)),
  paste0("- Average evidence architecture readiness: ", round(mean(readiness$evidence_architecture_readiness), 4))
), file.path(reports_dir, "r_evidence_architecture_report.md"))

print("Evidence architecture R analysis complete.")
print(readiness[, c("article_slug", "evidence_architecture_readiness", "evidence_architecture_status")])
