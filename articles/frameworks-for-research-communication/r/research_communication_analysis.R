# Base R workflow for evidence coverage, uncertainty visibility, and audience readiness.

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

articles <- read.csv(file.path(data_dir, "research_communication_inventory.csv"), stringsAsFactors = FALSE)
claims <- read.csv(file.path(data_dir, "claim_inventory.csv"), stringsAsFactors = FALSE)
sources <- read.csv(file.path(data_dir, "source_inventory.csv"), stringsAsFactors = FALSE)
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

claims_sources$authority_score <- ifelse(
  claims_sources$authority_level == "high",
  1,
  ifelse(claims_sources$authority_level == "medium", 0.75, 0.50)
)

claims_sources$authority_score[is.na(claims_sources$authority_score)] <- 0

claims_sources$claim_support_score <- ifelse(
  yes(claims_sources$claim_supported),
  claims_sources$authority_score,
  pmin(claims_sources$authority_score, 0.35)
)

claim_report <- claims_sources[, c(
  "claim_id",
  "article_slug",
  "claim_type",
  "claim_strength",
  "source_id",
  "source_type",
  "authority_level",
  "claim_supported",
  "claim_support_score"
)]

claim_scores <- aggregate(
  claim_support_score ~ article_slug,
  data = claim_report,
  FUN = mean
)

names(claim_scores) <- c("article_slug", "claim_support_score")

readiness <- merge(articles, claim_scores, by = "article_slug", all.x = TRUE)
readiness$claim_support_score[is.na(readiness$claim_support_score)] <- 0

readiness$method_clarity_score <- ifelse(yes(readiness$method_explained), 1, 0)

readiness$uncertainty_visibility_score <- round(
  (
    yes(readiness$limitations_visible) +
      yes(readiness$uncertainty_visible) +
      yes(readiness$assumptions_visible) +
      yes(readiness$confidence_language_present)
  ) / 4,
  4
)

readiness$audience_context_score <- round(
  (
    yes(readiness$audience_defined) +
      yes(readiness$prior_knowledge_supported) +
      yes(readiness$plain_language_summary) +
      yes(readiness$implications_bounded)
  ) / 4,
  4
)

readiness$visual_accessibility_score <- round(
  (
    yes(readiness$visuals_accessible) +
      yes(readiness$tables_explained) +
      yes(readiness$alt_text_present)
  ) / 3,
  4
)

readiness$research_communication_readiness <- round(
  0.28 * readiness$claim_support_score +
    0.18 * readiness$method_clarity_score +
    0.22 * readiness$uncertainty_visibility_score +
    0.17 * readiness$audience_context_score +
    0.15 * readiness$visual_accessibility_score,
  4
)

readiness$readiness_status <- ifelse(
  readiness$research_communication_readiness >= 0.78,
  "ready",
  "governance review"
)

governance_queue <- subset(
  readiness,
  status == "published" & readiness_status == "governance review"
)

catalog <- readiness[, c(
  "article_slug",
  "title",
  "research_domain",
  "audience",
  "research_communication_readiness",
  "readiness_status"
)]

catalog$series <- "Content Frameworks"
catalog$github_path <- paste0("articles/", catalog$article_slug, "/")

write.csv(source_type_summary, file.path(tables_dir, "r_source_type_summary.csv"), row.names = FALSE)
write.csv(authority_summary, file.path(tables_dir, "r_authority_summary.csv"), row.names = FALSE)
write.csv(claim_report, file.path(tables_dir, "r_claim_support_report.csv"), row.names = FALSE)
write.csv(readiness, file.path(tables_dir, "r_research_communication_readiness_report.csv"), row.names = FALSE)
write.csv(governance_queue, file.path(tables_dir, "r_research_communication_governance_queue.csv"), row.names = FALSE)
write.csv(catalog, file.path(catalog_dir, "r_research_communication_catalog_export.csv"), row.names = FALSE)

png(file.path(figures_dir, "r_research_communication_readiness.png"), width = 1200, height = 800)
barplot(readiness$research_communication_readiness, names.arg = readiness$article_slug, las = 2, main = "Research Communication Readiness", ylab = "Readiness score")
dev.off()

png(file.path(figures_dir, "r_source_authority_distribution.png"), width = 1000, height = 700)
barplot(authority_summary$source_count, names.arg = authority_summary$authority_level, main = "Source Authority Distribution", ylab = "Source count")
dev.off()

writeLines(c(
  "# Frameworks for Research Communication: R Audit",
  "",
  paste0("- Research communication records: ", nrow(articles)),
  paste0("- Claim records: ", nrow(claims)),
  paste0("- Source records: ", nrow(sources)),
  paste0("- Manual review queue records: ", nrow(review_queue)),
  paste0("- Average readiness score: ", round(mean(readiness$research_communication_readiness), 4))
), file.path(reports_dir, "r_research_communication_report.md"))

print("Research communication R analysis complete.")
print(readiness[, c("article_slug", "research_communication_readiness", "readiness_status")])
