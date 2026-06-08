# Base R workflow for curriculum pathway coverage and readiness.

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

nodes <- read.csv(file.path(data_dir, "curriculum_pathway_inventory.csv"), stringsAsFactors = FALSE)
prerequisites <- read.csv(file.path(data_dir, "prerequisite_relationships.csv"), stringsAsFactors = FALSE)
objectives <- read.csv(file.path(data_dir, "learning_objectives.csv"), stringsAsFactors = FALSE)
review_queue <- read.csv(file.path(data_dir, "editorial_review_queue.csv"), stringsAsFactors = FALSE)

yes <- function(x) tolower(trimws(x)) %in% c("yes", "true", "1", "ready", "complete")

stage_summary <- as.data.frame(table(nodes$learning_stage), stringsAsFactors = FALSE)
names(stage_summary) <- c("learning_stage", "node_count")

cluster_summary <- as.data.frame(table(nodes$pathway_cluster, nodes$status), stringsAsFactors = FALSE)
names(cluster_summary) <- c("pathway_cluster", "status", "node_count")

published_nodes <- nodes$node_slug[nodes$status == "published"]

required_counts <- as.data.frame(table(prerequisites$node_slug), stringsAsFactors = FALSE)
names(required_counts) <- c("node_slug", "required_prerequisites")

prerequisites$published_prerequisite <- prerequisites$prerequisite_slug %in% published_nodes

published_counts <- aggregate(
  published_prerequisite ~ node_slug,
  data = prerequisites,
  FUN = sum
)

names(published_counts) <- c("node_slug", "published_prerequisites")

prereq_report <- merge(
  nodes[, c("node_slug", "title", "status", "learning_stage")],
  required_counts,
  by = "node_slug",
  all.x = TRUE
)

prereq_report <- merge(prereq_report, published_counts, by = "node_slug", all.x = TRUE)
prereq_report$required_prerequisites[is.na(prereq_report$required_prerequisites)] <- 0
prereq_report$published_prerequisites[is.na(prereq_report$published_prerequisites)] <- 0

prereq_report$prerequisite_readiness <- ifelse(
  prereq_report$required_prerequisites == 0,
  1,
  prereq_report$published_prerequisites / prereq_report$required_prerequisites
)

prereq_report$prerequisite_readiness <- round(prereq_report$prerequisite_readiness, 4)

required_objectives <- subset(objectives, yes(required))

objective_required_counts <- as.data.frame(table(required_objectives$node_slug), stringsAsFactors = FALSE)
names(objective_required_counts) <- c("node_slug", "required_objectives")

required_objectives$supported_required_objectives <- yes(required_objectives$support_material_present)
required_objectives$assessed_required_objectives <- yes(required_objectives$assessment_present)

supported_counts <- aggregate(
  supported_required_objectives ~ node_slug,
  data = required_objectives,
  FUN = sum
)

assessed_counts <- aggregate(
  assessed_required_objectives ~ node_slug,
  data = required_objectives,
  FUN = sum
)

objective_report <- merge(
  nodes[, c("node_slug", "title", "status", "learning_stage")],
  objective_required_counts,
  by = "node_slug",
  all.x = TRUE
)

objective_report <- merge(objective_report, supported_counts, by = "node_slug", all.x = TRUE)
objective_report <- merge(objective_report, assessed_counts, by = "node_slug", all.x = TRUE)

objective_report$required_objectives[is.na(objective_report$required_objectives)] <- 0
objective_report$supported_required_objectives[is.na(objective_report$supported_required_objectives)] <- 0
objective_report$assessed_required_objectives[is.na(objective_report$assessed_required_objectives)] <- 0

objective_report$objective_coverage_score <- ifelse(
  objective_report$required_objectives == 0,
  1,
  objective_report$supported_required_objectives / objective_report$required_objectives
)

objective_report$assessment_alignment_score <- ifelse(
  objective_report$required_objectives == 0,
  1,
  objective_report$assessed_required_objectives / objective_report$required_objectives
)

objective_report$objective_coverage_score <- round(objective_report$objective_coverage_score, 4)
objective_report$assessment_alignment_score <- round(objective_report$assessment_alignment_score, 4)

readiness <- merge(
  nodes,
  prereq_report[, c("node_slug", "prerequisite_readiness")],
  by = "node_slug",
  all.x = TRUE
)

readiness <- merge(
  readiness,
  objective_report[, c("node_slug", "objective_coverage_score")],
  by = "node_slug",
  all.x = TRUE
)

readiness$accessibility_score <- round(
  (
    yes(readiness$clear_headings) +
      yes(readiness$descriptive_links) +
      yes(readiness$alt_text) +
      yes(readiness$plain_language_summary)
  ) / 4,
  4
)

readiness$feedback_score <- round(
  (
    yes(readiness$reflection_prompt) +
      yes(readiness$assessment_point) +
      yes(readiness$revision_prompt)
  ) / 3,
  4
)

readiness$transfer_score <- round(
  (
    yes(readiness$application_example) +
      yes(readiness$transfer_task) +
      yes(readiness$repository_support)
  ) / 3,
  4
)

readiness$pathway_readiness_score <- round(
  0.22 * readiness$prerequisite_readiness +
    0.22 * readiness$objective_coverage_score +
    0.16 * readiness$accessibility_score +
    0.18 * readiness$feedback_score +
    0.22 * readiness$transfer_score,
  4
)

readiness$pathway_status <- ifelse(
  readiness$pathway_readiness_score >= 0.78,
  "ready",
  "governance review"
)

governance_queue <- subset(
  readiness,
  status == "published" & pathway_status == "governance review"
)

catalog <- readiness[, c(
  "node_slug",
  "title",
  "pathway_cluster",
  "learning_stage",
  "pathway_readiness_score",
  "pathway_status"
)]

catalog$series <- "Content Frameworks"
catalog$github_path <- paste0("articles/", catalog$node_slug, "/")

write.csv(stage_summary, file.path(tables_dir, "r_learning_stage_summary.csv"), row.names = FALSE)
write.csv(cluster_summary, file.path(tables_dir, "r_pathway_cluster_summary.csv"), row.names = FALSE)
write.csv(prereq_report, file.path(tables_dir, "r_prerequisite_readiness_report.csv"), row.names = FALSE)
write.csv(objective_report, file.path(tables_dir, "r_objective_coverage_report.csv"), row.names = FALSE)
write.csv(readiness, file.path(tables_dir, "r_pathway_readiness_report.csv"), row.names = FALSE)
write.csv(governance_queue, file.path(tables_dir, "r_curriculum_pathway_governance_queue.csv"), row.names = FALSE)
write.csv(catalog, file.path(catalog_dir, "r_curriculum_pathway_catalog_export.csv"), row.names = FALSE)

png(file.path(figures_dir, "r_pathway_readiness_scores.png"), width = 1200, height = 800)
barplot(readiness$pathway_readiness_score, names.arg = readiness$node_slug, las = 2, main = "Curriculum Pathway Readiness Scores", ylab = "Readiness score")
dev.off()

png(file.path(figures_dir, "r_learning_stage_distribution.png"), width = 1000, height = 700)
barplot(stage_summary$node_count, names.arg = stage_summary$learning_stage, las = 2, main = "Learning Stage Distribution", ylab = "Node count")
dev.off()

writeLines(c(
  "# Curriculum Pathways and Framework Design: R Audit",
  "",
  paste0("- Pathway nodes: ", nrow(nodes)),
  paste0("- Prerequisite relationships: ", nrow(prerequisites)),
  paste0("- Learning objectives: ", nrow(objectives)),
  paste0("- Manual review queue records: ", nrow(review_queue)),
  paste0("- Average pathway readiness score: ", round(mean(readiness$pathway_readiness_score), 4))
), file.path(reports_dir, "r_curriculum_pathway_report.md"))

print("Curriculum pathway R analysis complete.")
print(readiness[, c("node_slug", "pathway_readiness_score", "pathway_status")])
