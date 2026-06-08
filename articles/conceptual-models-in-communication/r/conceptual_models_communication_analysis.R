# Base R communication-model audit.

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

models <- read.csv(file.path(data_dir, "communication_model_inventory.csv"), stringsAsFactors = FALSE)
elements <- read.csv(file.path(data_dir, "model_elements.csv"), stringsAsFactors = FALSE)
relationships <- read.csv(file.path(data_dir, "model_relationships.csv"), stringsAsFactors = FALSE)

yes <- function(x) tolower(trimws(x)) %in% c("yes", "true", "1", "ready", "complete")

type_summary <- as.data.frame(table(models$model_type), stringsAsFactors = FALSE)
names(type_summary) <- c("model_type", "model_count")

risk_summary <- as.data.frame(table(models$abstraction_risk), stringsAsFactors = FALSE)
names(risk_summary) <- c("abstraction_risk", "model_count")

required_by_type <- list(
  linear = c("communicator", "message", "channel", "audience", "noise"),
  interactional = c("communicator", "message", "channel", "audience", "noise", "feedback"),
  transactional = c("communicator", "message", "audience", "context", "feedback", "interpretation"),
  systems = c("communicator", "message", "audience", "context", "feedback", "institutions", "power", "platform"),
  evidence = c("claim", "evidence", "method", "uncertainty", "limitation", "implication", "audience"),
  learning = c("orientation", "sequence", "prerequisites", "examples", "feedback", "transfer")
)

rows <- list()

for (i in seq_len(nrow(models))) {
  model_id <- models$model_id[i]
  model_type <- models$model_type[i]
  required <- required_by_type[[model_type]]
  present <- elements$element[elements$model_id == model_id & yes(elements$present)]
  element_score <- length(intersect(required, present)) / length(required)

  active_relationships <- sum(relationships$model_id == model_id & yes(relationships$active))
  relationship_score <- ifelse(active_relationships >= 5, 1, ifelse(active_relationships >= 3, 0.75, ifelse(active_relationships >= 1, 0.45, 0)))

  audience_score <- (
    yes(models$audience_visible[i]) +
      yes(models$context_visible[i]) +
      yes(models$interpretation_visible[i]) +
      yes(models$power_visible[i])
  ) / 4

  feedback_score <- ifelse(yes(models$feedback_visible[i]), 1, 0)

  evidence_score <- (
    yes(models$evidence_visible[i]) +
      yes(models$limitations_visible[i]) +
      yes(models$assumptions_visible[i])
  ) / 3

  domain_score <- ifelse(models$domain_fit[i] == "high", 1, ifelse(models$domain_fit[i] == "medium", 0.65, 0.30))
  penalty <- ifelse(models$abstraction_risk[i] == "high", 0.25, ifelse(models$abstraction_risk[i] == "medium", 0.10, 0))

  readiness <- max(0, min(1, 0.25 * element_score + 0.15 * relationship_score + 0.20 * audience_score + 0.15 * feedback_score + 0.15 * evidence_score + 0.10 * domain_score - penalty))

  rows[[length(rows) + 1]] <- data.frame(
    model_id = model_id,
    model_name = models$model_name[i],
    model_type = model_type,
    status = models$status[i],
    primary_domain = models$primary_domain[i],
    element_score = round(element_score, 4),
    relationship_score = round(relationship_score, 4),
    audience_context_score = round(audience_score, 4),
    feedback_score = round(feedback_score, 4),
    evidence_limitations_score = round(evidence_score, 4),
    domain_fit_score = round(domain_score, 4),
    risk_penalty = round(penalty, 4),
    model_readiness_score = round(readiness, 4),
    model_readiness_status = ifelse(readiness >= 0.78, "ready", "governance review"),
    stringsAsFactors = FALSE
  )
}

readiness_report <- do.call(rbind, rows)

write.csv(type_summary, file.path(tables_dir, "r_model_type_summary.csv"), row.names = FALSE)
write.csv(risk_summary, file.path(tables_dir, "r_abstraction_risk_summary.csv"), row.names = FALSE)
write.csv(readiness_report, file.path(tables_dir, "r_model_readiness_report.csv"), row.names = FALSE)

catalog <- readiness_report[, c("model_id", "model_name", "model_type", "status", "primary_domain", "model_readiness_score", "model_readiness_status")]
catalog$series <- "Content Frameworks"
catalog$article <- "Conceptual Models in Communication"
catalog$github_path <- "articles/conceptual-models-in-communication/"
write.csv(catalog, file.path(catalog_dir, "r_conceptual_models_communication_catalog_export.csv"), row.names = FALSE)

png(file.path(figures_dir, "r_model_readiness_scores.png"), width = 1200, height = 800)
barplot(readiness_report$model_readiness_score, names.arg = readiness_report$model_name, las = 2, main = "Communication Model Readiness Scores", ylab = "Readiness score")
dev.off()

writeLines(c(
  "# Conceptual Models in Communication: R Audit",
  "",
  paste0("- Communication models: ", nrow(models)),
  paste0("- Average readiness score: ", round(mean(readiness_report$model_readiness_score), 4))
), file.path(reports_dir, "r_conceptual_models_communication_report.md"))

print("R communication-model analysis complete.")
print(readiness_report[, c("model_id", "model_name", "model_readiness_score", "model_readiness_status")])
