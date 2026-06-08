# educational_scaffolding_learning_system_analysis.R
# Professional base R workflow for learning-path and scaffold-readiness reporting.

if (!exists("article_root")) {
  article_root <- getwd()
}

data_dir <- file.path(article_root, "data")
tables_dir <- file.path(article_root, "outputs", "tables")
figures_dir <- file.path(article_root, "outputs", "figures")
reports_dir <- file.path(article_root, "outputs", "reports")
catalog_dir <- file.path(article_root, "outputs", "catalog_exports")

dir.create(tables_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(figures_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(reports_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(catalog_dir, recursive = TRUE, showWarnings = FALSE)

learning <- read.csv(file.path(data_dir, "learning_path_inventory.csv"), stringsAsFactors = FALSE)
prerequisites <- read.csv(file.path(data_dir, "prerequisite_relationships.csv"), stringsAsFactors = FALSE)
feature_catalog <- read.csv(file.path(data_dir, "scaffold_feature_catalog.csv"), stringsAsFactors = FALSE)
review_queue <- read.csv(file.path(data_dir, "editorial_review_queue.csv"), stringsAsFactors = FALSE)

yes <- function(x) {
  tolower(trimws(x)) %in% c("yes", "true", "1", "complete", "ready")
}

# ------------------------------------------------------------
# Stage and concept coverage
# ------------------------------------------------------------
stage_summary <- as.data.frame(table(learning$learning_stage), stringsAsFactors = FALSE)
names(stage_summary) <- c("learning_stage", "article_count")

concept_summary <- aggregate(
  slug ~ concept_cluster + status,
  data = learning,
  FUN = length
)

names(concept_summary) <- c("concept_cluster", "status", "article_count")

concept_totals <- aggregate(
  slug ~ concept_cluster,
  data = learning,
  FUN = length
)

names(concept_totals) <- c("concept_cluster", "total_articles")

concept_published <- aggregate(
  slug ~ concept_cluster,
  data = subset(learning, status == "published"),
  FUN = length
)

names(concept_published) <- c("concept_cluster", "published_articles")

concept_report <- merge(concept_totals, concept_published, by = "concept_cluster", all.x = TRUE)
concept_report$published_articles[is.na(concept_report$published_articles)] <- 0
concept_report$coverage_rate <- round(concept_report$published_articles / concept_report$total_articles, 4)
concept_report$coverage_status <- ifelse(concept_report$coverage_rate >= 0.60, "healthy", "needs development")

# ------------------------------------------------------------
# Prerequisite readiness
# ------------------------------------------------------------
published_slugs <- learning$slug[learning$status == "published"]

required_counts <- as.data.frame(table(prerequisites$article_slug), stringsAsFactors = FALSE)
names(required_counts) <- c("slug", "required_prerequisites")

prerequisites$published_prerequisite <- prerequisites$prerequisite_slug %in% published_slugs

published_prereq_counts <- aggregate(
  published_prerequisite ~ article_slug,
  data = prerequisites,
  FUN = sum
)

names(published_prereq_counts) <- c("slug", "published_prerequisites")

prereq_report <- merge(
  learning[, c("slug", "title", "status", "learning_stage")],
  required_counts,
  by = "slug",
  all.x = TRUE
)

prereq_report <- merge(
  prereq_report,
  published_prereq_counts,
  by = "slug",
  all.x = TRUE
)

prereq_report$required_prerequisites[is.na(prereq_report$required_prerequisites)] <- 0
prereq_report$published_prerequisites[is.na(prereq_report$published_prerequisites)] <- 0

prereq_report$prerequisite_readiness <- ifelse(
  prereq_report$required_prerequisites == 0,
  1,
  prereq_report$published_prerequisites / prereq_report$required_prerequisites
)

prereq_report$prerequisite_readiness <- round(prereq_report$prerequisite_readiness, 4)
prereq_report$prerequisite_status <- ifelse(
  prereq_report$prerequisite_readiness >= 0.80,
  "ready",
  "needs prerequisite support"
)

# ------------------------------------------------------------
# Scaffold features
# ------------------------------------------------------------
learning$orientation_score <- ifelse(yes(learning$orientation_support), 1, 0)
learning$example_score <- ifelse(yes(learning$worked_examples), 1, 0)
learning$feedback_score <- ifelse(yes(learning$feedback_prompts), 1, 0)
learning$transfer_score <- ifelse(yes(learning$transfer_support), 1, 0)

learning$accessibility_score <- round(
  (
    yes(learning$alt_text) +
      yes(learning$clear_headings) +
      yes(learning$descriptive_links) +
      yes(learning$summary_support)
  ) / 4,
  4
)

learning$load_penalty <- ifelse(
  learning$cognitive_load_risk == "high",
  0.25,
  ifelse(learning$cognitive_load_risk == "medium", 0.10, 0)
)

# ------------------------------------------------------------
# Scaffold readiness
# ------------------------------------------------------------
readiness <- merge(
  learning,
  prereq_report[, c("slug", "prerequisite_readiness")],
  by = "slug",
  all.x = TRUE
)

readiness$scaffold_readiness_score <- round(
  0.18 * readiness$orientation_score +
    0.20 * readiness$prerequisite_readiness +
    0.18 * readiness$example_score +
    0.16 * readiness$feedback_score +
    0.18 * readiness$transfer_score +
    0.10 * readiness$accessibility_score -
    readiness$load_penalty,
  4
)

readiness$scaffold_readiness_score <- pmax(0, pmin(1, readiness$scaffold_readiness_score))

readiness$scaffold_status <- ifelse(
  readiness$scaffold_readiness_score >= 0.78,
  "ready",
  "governance review"
)

# ------------------------------------------------------------
# Relationship summaries
# ------------------------------------------------------------
relationship_summary <- as.data.frame(table(prerequisites$relationship_type), stringsAsFactors = FALSE)
names(relationship_summary) <- c("relationship_type", "relationship_count")

importance_summary <- as.data.frame(table(prerequisites$importance), stringsAsFactors = FALSE)
names(importance_summary) <- c("importance", "relationship_count")

# ------------------------------------------------------------
# Governance queue
# ------------------------------------------------------------
governance_queue <- subset(
  readiness,
  status == "published" &
    scaffold_status == "governance review"
)

governance_queue <- governance_queue[
  order(governance_queue$scaffold_readiness_score, governance_queue$concept_cluster),
]

# ------------------------------------------------------------
# Catalog export
# ------------------------------------------------------------
catalog <- readiness[, c(
  "slug",
  "title",
  "status",
  "concept_cluster",
  "learning_stage",
  "scaffold_readiness_score",
  "scaffold_status"
)]

catalog$series <- "Content Frameworks"
catalog$github_path <- paste0("articles/", catalog$slug, "/")

catalog <- catalog[, c(
  "series",
  "slug",
  "title",
  "status",
  "concept_cluster",
  "learning_stage",
  "scaffold_readiness_score",
  "scaffold_status",
  "github_path"
)]

# ------------------------------------------------------------
# Write outputs
# ------------------------------------------------------------
write.csv(stage_summary, file.path(tables_dir, "r_learning_stage_summary.csv"), row.names = FALSE)
write.csv(concept_report, file.path(tables_dir, "r_concept_coverage_report.csv"), row.names = FALSE)
write.csv(prereq_report, file.path(tables_dir, "r_prerequisite_readiness_report.csv"), row.names = FALSE)
write.csv(relationship_summary, file.path(tables_dir, "r_relationship_type_summary.csv"), row.names = FALSE)
write.csv(importance_summary, file.path(tables_dir, "r_relationship_importance_summary.csv"), row.names = FALSE)
write.csv(feature_catalog, file.path(tables_dir, "r_scaffold_feature_catalog.csv"), row.names = FALSE)

write.csv(
  readiness[, c(
    "slug",
    "title",
    "status",
    "concept_cluster",
    "learning_stage",
    "orientation_score",
    "prerequisite_readiness",
    "example_score",
    "feedback_score",
    "transfer_score",
    "accessibility_score",
    "load_penalty",
    "scaffold_readiness_score",
    "scaffold_status"
  )],
  file.path(tables_dir, "r_scaffold_readiness_report.csv"),
  row.names = FALSE
)

write.csv(governance_queue, file.path(tables_dir, "r_learning_system_governance_queue.csv"), row.names = FALSE)
write.csv(catalog, file.path(catalog_dir, "r_educational_scaffolding_catalog_export.csv"), row.names = FALSE)

# ------------------------------------------------------------
# Figures
# ------------------------------------------------------------
png(file.path(figures_dir, "r_scaffold_readiness_by_article.png"), width = 1300, height = 850)
barplot(
  readiness$scaffold_readiness_score,
  names.arg = readiness$slug,
  las = 2,
  main = "Scaffold Readiness by Article",
  ylab = "Readiness score"
)
dev.off()

png(file.path(figures_dir, "r_concept_coverage_rates.png"), width = 1100, height = 750)
barplot(
  concept_report$coverage_rate,
  names.arg = concept_report$concept_cluster,
  las = 2,
  main = "Published Coverage Rate by Concept Cluster",
  ylab = "Coverage rate"
)
dev.off()

png(file.path(figures_dir, "r_learning_stage_distribution.png"), width = 1000, height = 700)
barplot(
  stage_summary$article_count,
  names.arg = stage_summary$learning_stage,
  las = 2,
  main = "Learning Stage Distribution",
  ylab = "Article count"
)
dev.off()

png(file.path(figures_dir, "r_prerequisite_readiness.png"), width = 1300, height = 850)
barplot(
  prereq_report$prerequisite_readiness,
  names.arg = prereq_report$slug,
  las = 2,
  main = "Prerequisite Readiness by Article",
  ylab = "Prerequisite readiness"
)
dev.off()

# ------------------------------------------------------------
# Markdown report
# ------------------------------------------------------------
summary_lines <- c(
  "# Educational Scaffolding and Learning-System Analysis",
  "",
  "## Summary",
  "",
  paste0("- Learning-path records: ", nrow(learning)),
  paste0("- Prerequisite relationships: ", nrow(prerequisites)),
  paste0("- Scaffold feature catalog records: ", nrow(feature_catalog)),
  paste0("- Manual review queue records: ", nrow(review_queue)),
  paste0("- Automated governance review records: ", nrow(governance_queue)),
  paste0("- Average scaffold-readiness score: ", round(mean(readiness$scaffold_readiness_score), 4)),
  "",
  "## Generated outputs",
  "",
  "- `r_learning_stage_summary.csv`",
  "- `r_concept_coverage_report.csv`",
  "- `r_prerequisite_readiness_report.csv`",
  "- `r_relationship_type_summary.csv`",
  "- `r_scaffold_readiness_report.csv`",
  "- `r_learning_system_governance_queue.csv`",
  "- `r_educational_scaffolding_catalog_export.csv`",
  "",
  "These outputs support learning-path review and educational scaffolding governance."
)

writeLines(
  summary_lines,
  file.path(reports_dir, "r_educational_scaffolding_learning_system_report.md")
)

print("Educational scaffolding R analysis complete.")
print(concept_report)
print(readiness[, c("slug", "scaffold_readiness_score", "scaffold_status")])
