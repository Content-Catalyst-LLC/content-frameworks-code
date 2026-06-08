# catalyst_canvas_narrative_pathway_analysis.R
# Base R workflow for narrative pathways, reader states,
# article roles, internal-link coverage, metadata readiness,
# pathway readiness, and editorial governance.

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

articles <- read.csv(file.path(data_dir, "pathway_article_inventory.csv"), stringsAsFactors = FALSE)
links <- read.csv(file.path(data_dir, "internal_links.csv"), stringsAsFactors = FALSE)
pathways <- read.csv(file.path(data_dir, "narrative_pathway_definitions.csv"), stringsAsFactors = FALSE)
metadata <- read.csv(file.path(data_dir, "metadata_inventory.csv"), stringsAsFactors = FALSE)

metadata_fields <- c(
  "excerpt",
  "tags",
  "github_url",
  "image_alt",
  "references",
  "last_reviewed",
  "series_context",
  "footer_navigation"
)

# ------------------------------------------------------------
# Article role and reader-state summaries
# ------------------------------------------------------------
article_role_summary <- as.data.frame(table(articles$article_role), stringsAsFactors = FALSE)
names(article_role_summary) <- c("article_role", "article_count")

pathway_role_summary <- as.data.frame(table(articles$pathway_role), stringsAsFactors = FALSE)
names(pathway_role_summary) <- c("pathway_role", "article_count")

reader_state_summary <- as.data.frame(table(articles$reader_state), stringsAsFactors = FALSE)
names(reader_state_summary) <- c("reader_state", "article_count")

status_summary <- as.data.frame(table(articles$status), stringsAsFactors = FALSE)
names(status_summary) <- c("status", "article_count")

pathway_type_summary <- as.data.frame(table(pathways$pathway_type), stringsAsFactors = FALSE)
names(pathway_type_summary) <- c("pathway_type", "pathway_count")

# ------------------------------------------------------------
# Metadata readiness
# ------------------------------------------------------------
metadata_complete <- metadata[, metadata_fields] == "yes"
metadata$completed_fields <- rowSums(metadata_complete)
metadata$required_fields <- length(metadata_fields)
metadata$metadata_completion <- round(metadata$completed_fields / metadata$required_fields, 4)
metadata$metadata_status <- ifelse(metadata$metadata_completion >= 0.85, "ready", "needs metadata work")

metadata_report <- metadata[, c(
  "slug",
  "title",
  "status",
  "completed_fields",
  "required_fields",
  "metadata_completion",
  "metadata_status"
)]

# ------------------------------------------------------------
# Link diagnostics
# ------------------------------------------------------------
outgoing <- as.data.frame(table(links$source_slug), stringsAsFactors = FALSE)
names(outgoing) <- c("slug", "outgoing_links")

incoming <- as.data.frame(table(links$target_slug), stringsAsFactors = FALSE)
names(incoming) <- c("slug", "incoming_links")

link_report <- merge(
  articles[, c("slug", "title", "cluster", "status", "article_role", "pathway_role", "reader_state")],
  outgoing,
  by = "slug",
  all.x = TRUE
)
link_report <- merge(link_report, incoming, by = "slug", all.x = TRUE)
link_report$outgoing_links[is.na(link_report$outgoing_links)] <- 0
link_report$incoming_links[is.na(link_report$incoming_links)] <- 0
link_report$total_link_degree <- link_report$outgoing_links + link_report$incoming_links

link_report$network_role <- ifelse(
  link_report$total_link_degree >= 5,
  "pathway hub",
  ifelse(link_report$total_link_degree >= 2, "connected article", "thinly linked article")
)

# ------------------------------------------------------------
# Article readiness
# ------------------------------------------------------------
article_readiness <- merge(
  link_report,
  metadata_report[, c("slug", "metadata_completion", "metadata_status")],
  by = "slug",
  all.x = TRUE
)

orientation_map <- articles[, c("slug", "has_series_context", "links_to_article_map", "has_transition_links", "has_next_step")]
article_readiness <- merge(article_readiness, orientation_map, by = "slug", all.x = TRUE)

article_readiness$orientation_ready <- article_readiness$has_series_context == "yes" & article_readiness$links_to_article_map == "yes"
article_readiness$bridge_ready <- article_readiness$has_transition_links == "yes" & article_readiness$has_next_step == "yes"

article_readiness$editorial_status <- ifelse(
  article_readiness$status == "published" &
    article_readiness$metadata_completion >= 0.85 &
    article_readiness$total_link_degree >= 2 &
    article_readiness$orientation_ready &
    article_readiness$bridge_ready,
  "ready",
  ifelse(article_readiness$status == "planned", "planned", "review required")
)

# ------------------------------------------------------------
# Pathway readiness
# ------------------------------------------------------------
pathway_rows <- list()

for (i in seq_len(nrow(pathways))) {
  required_slugs <- unlist(strsplit(pathways$required_article_slugs[i], "\\|"))
  required_slugs <- trimws(required_slugs)
  required_slugs <- required_slugs[nchar(required_slugs) > 0]

  published_required <- required_slugs[
    required_slugs %in% articles$slug[articles$status == "published"]
  ]

  planned_required <- required_slugs[
    required_slugs %in% articles$slug[articles$status == "planned"]
  ]

  missing_required <- required_slugs[
    !(required_slugs %in% articles$slug)
  ]

  pathway_readiness <- ifelse(
    length(required_slugs) > 0,
    round(length(published_required) / length(required_slugs), 4),
    0
  )

  pathway_rows[[i]] <- data.frame(
    pathway_id = pathways$pathway_id[i],
    pathway_name = pathways$pathway_name[i],
    pathway_type = pathways$pathway_type[i],
    reader_state = pathways$reader_state[i],
    required_article_count = length(required_slugs),
    published_required_count = length(published_required),
    planned_required_count = length(planned_required),
    missing_required_count = length(missing_required),
    pathway_readiness = pathway_readiness,
    pathway_status = ifelse(pathway_readiness >= 0.75, "ready", ifelse(pathway_readiness >= 0.40, "developing", "early stage")),
    stringsAsFactors = FALSE
  )
}

pathway_readiness <- do.call(rbind, pathway_rows)

# ------------------------------------------------------------
# Catalog export
# ------------------------------------------------------------
catalog <- article_readiness
catalog$catalog_product <- "Catalyst Canvas"
catalog$series <- "Content Frameworks"
catalog$github_path <- paste0("articles/", catalog$slug, "/")

catalog <- catalog[, c(
  "catalog_product",
  "series",
  "slug",
  "title",
  "cluster",
  "status",
  "article_role",
  "pathway_role",
  "reader_state",
  "network_role",
  "metadata_completion",
  "metadata_status",
  "editorial_status",
  "github_path"
)]

# ------------------------------------------------------------
# Write outputs
# ------------------------------------------------------------
write.csv(article_role_summary, file.path(tables_dir, "r_article_role_summary.csv"), row.names = FALSE)
write.csv(pathway_role_summary, file.path(tables_dir, "r_pathway_role_summary.csv"), row.names = FALSE)
write.csv(reader_state_summary, file.path(tables_dir, "r_reader_state_summary.csv"), row.names = FALSE)
write.csv(status_summary, file.path(tables_dir, "r_article_status_summary.csv"), row.names = FALSE)
write.csv(pathway_type_summary, file.path(tables_dir, "r_pathway_type_summary.csv"), row.names = FALSE)
write.csv(link_report, file.path(tables_dir, "r_narrative_pathway_link_report.csv"), row.names = FALSE)
write.csv(metadata_report, file.path(tables_dir, "r_narrative_pathway_metadata_readiness.csv"), row.names = FALSE)
write.csv(article_readiness, file.path(tables_dir, "r_narrative_pathway_article_readiness.csv"), row.names = FALSE)
write.csv(pathway_readiness, file.path(tables_dir, "r_narrative_pathway_readiness.csv"), row.names = FALSE)
write.csv(catalog, file.path(catalog_dir, "r_catalyst_canvas_narrative_pathway_catalog.csv"), row.names = FALSE)

# ------------------------------------------------------------
# Figures
# ------------------------------------------------------------
png(file.path(figures_dir, "r_pathway_readiness.png"), width = 1200, height = 800)
barplot(
  pathway_readiness$pathway_readiness,
  names.arg = pathway_readiness$pathway_name,
  las = 2,
  main = "Narrative Pathway Readiness",
  ylab = "Published required articles / required articles"
)
dev.off()

png(file.path(figures_dir, "r_reader_state_coverage.png"), width = 1000, height = 700)
barplot(
  table(articles$reader_state),
  main = "Reader State Coverage",
  ylab = "Article count"
)
dev.off()

png(file.path(figures_dir, "r_article_link_degree.png"), width = 1300, height = 850)
barplot(
  article_readiness$total_link_degree,
  names.arg = article_readiness$slug,
  las = 2,
  main = "Article Link Degree Across Narrative Pathways",
  ylab = "Total link degree"
)
dev.off()

png(file.path(figures_dir, "r_metadata_completion.png"), width = 1300, height = 850)
barplot(
  article_readiness$metadata_completion,
  names.arg = article_readiness$slug,
  las = 2,
  main = "Metadata Completion Across Narrative Pathways",
  ylab = "Metadata completion"
)
dev.off()

# ------------------------------------------------------------
# Markdown report
# ------------------------------------------------------------
report_lines <- c(
  "# Catalyst Canvas Narrative Pathway Analysis",
  "",
  "Article: Narrative Pathways and Knowledge Architecture",
  "",
  "## Summary",
  "",
  paste0("- Articles reviewed: ", nrow(articles)),
  paste0("- Internal links reviewed: ", nrow(links)),
  paste0("- Pathways reviewed: ", nrow(pathways)),
  paste0("- Articles requiring review: ", sum(article_readiness$editorial_status == "review required")),
  "",
  "## Outputs",
  "",
  "- `r_narrative_pathway_article_readiness.csv`",
  "- `r_narrative_pathway_readiness.csv`",
  "- `r_narrative_pathway_link_report.csv`",
  "- `r_narrative_pathway_metadata_readiness.csv`",
  "- `r_reader_state_summary.csv`",
  "- `r_catalyst_canvas_narrative_pathway_catalog.csv`",
  "",
  "These outputs are generated from synthetic data and demonstrate professional-grade narrative-pathway workflows."
)

writeLines(
  report_lines,
  file.path(reports_dir, "r_catalyst_canvas_narrative_pathway_analysis.md")
)

print("Catalyst Canvas R narrative pathway analysis complete.")
print(pathway_readiness)
print(article_readiness[, c("slug", "network_role", "metadata_status", "editorial_status")])
