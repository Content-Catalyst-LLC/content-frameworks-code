# Base R workflow for interdisciplinary knowledge-bridge readiness.

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

bridges <- read.csv(file.path(data_dir, "knowledge_bridge_inventory.csv"), stringsAsFactors = FALSE)
vocabulary <- read.csv(file.path(data_dir, "vocabulary_alignment.csv"), stringsAsFactors = FALSE)
evidence_links <- read.csv(file.path(data_dir, "evidence_compatibility.csv"), stringsAsFactors = FALSE)
review_queue <- read.csv(file.path(data_dir, "editorial_review_queue.csv"), stringsAsFactors = FALSE)

yes <- function(x) tolower(trimws(x)) %in% c("yes", "true", "1", "ready", "complete")

vocabulary$aligned_term <- yes(vocabulary$shared_term) &
  yes(vocabulary$source_definition_present) &
  yes(vocabulary$target_definition_present) &
  yes(vocabulary$translation_note_present)

shared_counts <- aggregate(shared_term ~ bridge_id, data = vocabulary, FUN = function(x) sum(yes(x)))
aligned_counts <- aggregate(aligned_term ~ bridge_id, data = vocabulary, FUN = sum)

names(shared_counts) <- c("bridge_id", "shared_terms")
names(aligned_counts) <- c("bridge_id", "aligned_terms")

translation_report <- merge(
  bridges[, c("bridge_id", "bridge_title", "source_domain", "target_domain")],
  shared_counts,
  by = "bridge_id",
  all.x = TRUE
)

translation_report <- merge(translation_report, aligned_counts, by = "bridge_id", all.x = TRUE)
translation_report$shared_terms[is.na(translation_report$shared_terms)] <- 0
translation_report$aligned_terms[is.na(translation_report$aligned_terms)] <- 0

translation_report$translation_alignment_score <- ifelse(
  translation_report$shared_terms == 0,
  1,
  translation_report$aligned_terms / translation_report$shared_terms
)
translation_report$translation_alignment_score <- round(translation_report$translation_alignment_score, 4)

evidence_links$compatible_evidence_link <- yes(evidence_links$evidence_type_classified) &
  yes(evidence_links$method_fit_explained) &
  yes(evidence_links$limitation_visible)

evidence_counts <- as.data.frame(table(evidence_links$bridge_id), stringsAsFactors = FALSE)
names(evidence_counts) <- c("bridge_id", "evidence_links")

compatible_counts <- aggregate(compatible_evidence_link ~ bridge_id, data = evidence_links, FUN = sum)
names(compatible_counts) <- c("bridge_id", "compatible_evidence_links")

evidence_report <- merge(
  bridges[, c("bridge_id", "bridge_title")],
  evidence_counts,
  by = "bridge_id",
  all.x = TRUE
)

evidence_report <- merge(evidence_report, compatible_counts, by = "bridge_id", all.x = TRUE)
evidence_report$evidence_links[is.na(evidence_report$evidence_links)] <- 0
evidence_report$compatible_evidence_links[is.na(evidence_report$compatible_evidence_links)] <- 0

evidence_report$evidence_compatibility_score <- ifelse(
  evidence_report$evidence_links == 0,
  0,
  evidence_report$compatible_evidence_links / evidence_report$evidence_links
)
evidence_report$evidence_compatibility_score <- round(evidence_report$evidence_compatibility_score, 4)

readiness <- merge(
  bridges,
  translation_report[, c("bridge_id", "translation_alignment_score")],
  by = "bridge_id",
  all.x = TRUE
)

readiness <- merge(
  readiness,
  evidence_report[, c("bridge_id", "evidence_compatibility_score")],
  by = "bridge_id",
  all.x = TRUE
)

readiness$method_transparency_score <- round(
  (
    yes(readiness$source_method_visible) +
      yes(readiness$target_method_visible) +
      yes(readiness$assumptions_visible)
  ) / 3,
  4
)

readiness$audience_support_score <- round(
  (
    yes(readiness$audience_context_present) +
      yes(readiness$plain_language_bridge_summary) +
      yes(readiness$example_present) +
      yes(readiness$misuse_warning_present)
  ) / 4,
  4
)

readiness$governance_readiness_score <- round(
  (
    yes(readiness$review_owner_present) +
      yes(readiness$last_review_date_present) +
      yes(readiness$revision_queue_checked)
  ) / 3,
  4
)

readiness$interdisciplinary_bridge_readiness <- round(
  0.22 * readiness$translation_alignment_score +
    0.24 * readiness$evidence_compatibility_score +
    0.18 * readiness$method_transparency_score +
    0.18 * readiness$audience_support_score +
    0.18 * readiness$governance_readiness_score,
  4
)

readiness$bridge_status <- ifelse(
  readiness$interdisciplinary_bridge_readiness >= 0.78,
  "ready",
  "governance review"
)

domain_source_summary <- as.data.frame(table(bridges$source_domain), stringsAsFactors = FALSE)
names(domain_source_summary) <- c("domain", "source_bridge_count")

domain_target_summary <- as.data.frame(table(bridges$target_domain), stringsAsFactors = FALSE)
names(domain_target_summary) <- c("domain", "target_bridge_count")

domain_summary <- merge(domain_source_summary, domain_target_summary, by = "domain", all = TRUE)
domain_summary$source_bridge_count[is.na(domain_summary$source_bridge_count)] <- 0
domain_summary$target_bridge_count[is.na(domain_summary$target_bridge_count)] <- 0
domain_summary$total_bridge_count <- domain_summary$source_bridge_count + domain_summary$target_bridge_count

governance_queue <- subset(readiness, bridge_status == "governance review")

catalog <- readiness[, c(
  "bridge_id",
  "bridge_title",
  "source_domain",
  "target_domain",
  "interdisciplinary_bridge_readiness",
  "bridge_status"
)]

catalog$series <- "Content Frameworks"
catalog$article_slug <- "interdisciplinary-frameworks-and-knowledge-bridges"
catalog$github_path <- "articles/interdisciplinary-frameworks-and-knowledge-bridges/"

write.csv(translation_report, file.path(tables_dir, "r_translation_alignment_report.csv"), row.names = FALSE)
write.csv(evidence_report, file.path(tables_dir, "r_evidence_compatibility_report.csv"), row.names = FALSE)
write.csv(readiness, file.path(tables_dir, "r_interdisciplinary_bridge_readiness_report.csv"), row.names = FALSE)
write.csv(domain_summary, file.path(tables_dir, "r_domain_balance_report.csv"), row.names = FALSE)
write.csv(governance_queue, file.path(tables_dir, "r_interdisciplinary_governance_queue.csv"), row.names = FALSE)
write.csv(catalog, file.path(catalog_dir, "r_interdisciplinary_bridge_catalog_export.csv"), row.names = FALSE)

png(file.path(figures_dir, "r_interdisciplinary_bridge_readiness.png"), width = 1200, height = 800)
barplot(readiness$interdisciplinary_bridge_readiness, names.arg = readiness$bridge_id, las = 2, main = "Interdisciplinary Bridge Readiness", ylab = "Readiness score")
dev.off()

png(file.path(figures_dir, "r_domain_balance.png"), width = 1000, height = 700)
barplot(domain_summary$total_bridge_count, names.arg = domain_summary$domain, las = 2, main = "Domain Balance Across Bridges", ylab = "Bridge count")
dev.off()

writeLines(c(
  "# Interdisciplinary Frameworks and Knowledge Bridges: R Audit",
  "",
  paste0("- Bridge records: ", nrow(bridges)),
  paste0("- Vocabulary alignment records: ", nrow(vocabulary)),
  paste0("- Evidence compatibility records: ", nrow(evidence_links)),
  paste0("- Manual review queue records: ", nrow(review_queue)),
  paste0("- Average bridge readiness: ", round(mean(readiness$interdisciplinary_bridge_readiness), 4))
), file.path(reports_dir, "r_interdisciplinary_bridge_report.md"))

print("Interdisciplinary bridge R analysis complete.")
print(readiness[, c("bridge_id", "interdisciplinary_bridge_readiness", "bridge_status")])
