# catalyst_canvas_internal_link_analysis.R
# Professional base R workflow for internal-link infrastructure analysis.

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

articles <- read.csv(file.path(data_dir, "article_inventory.csv"), stringsAsFactors = FALSE)
links <- read.csv(file.path(data_dir, "internal_links.csv"), stringsAsFactors = FALSE)

outgoing <- as.data.frame(table(links$source_slug), stringsAsFactors = FALSE)
names(outgoing) <- c("slug", "outgoing_links")
incoming <- as.data.frame(table(links$target_slug), stringsAsFactors = FALSE)
names(incoming) <- c("slug", "incoming_links")

link_report <- merge(articles, outgoing, by = "slug", all.x = TRUE)
link_report <- merge(link_report, incoming, by = "slug", all.x = TRUE)
link_report$outgoing_links[is.na(link_report$outgoing_links)] <- 0
link_report$incoming_links[is.na(link_report$incoming_links)] <- 0
link_report$total_link_degree <- link_report$outgoing_links + link_report$incoming_links
link_report$network_role <- ifelse(link_report$total_link_degree >= 8, "hub", ifelse(link_report$total_link_degree >= 5, "bridge", ifelse(link_report$total_link_degree >= 3, "connector", ifelse(link_report$total_link_degree >= 1, "thinly linked", "orphaned"))))
link_report$governance_flag <- ifelse(link_report$status == "published" & link_report$total_link_degree < 3, "review", "acceptable")

cluster_counts <- aggregate(slug ~ cluster, data = articles, FUN = length)
names(cluster_counts) <- c("cluster", "article_count")
cluster_outgoing <- aggregate(outgoing_links ~ cluster, data = link_report, FUN = sum)
cluster_incoming <- aggregate(incoming_links ~ cluster, data = link_report, FUN = sum)
cluster_report <- merge(cluster_counts, cluster_outgoing, by = "cluster", all.x = TRUE)
cluster_report <- merge(cluster_report, cluster_incoming, by = "cluster", all.x = TRUE)
cluster_report$outgoing_links[is.na(cluster_report$outgoing_links)] <- 0
cluster_report$incoming_links[is.na(cluster_report$incoming_links)] <- 0
cluster_report$total_links <- cluster_report$outgoing_links + cluster_report$incoming_links
cluster_report$link_density_proxy <- round(cluster_report$total_links / pmax(cluster_report$article_count, 1), 3)

link_type_summary <- as.data.frame(table(links$relationship_type), stringsAsFactors = FALSE)
names(link_type_summary) <- c("relationship_type", "link_count")
priority_summary <- as.data.frame(table(links$priority), stringsAsFactors = FALSE)
names(priority_summary) <- c("priority", "link_count")
status_summary <- as.data.frame(table(links$status), stringsAsFactors = FALSE)
names(status_summary) <- c("link_status", "link_count")

governance_queue <- subset(link_report, governance_flag == "review")
governance_queue <- governance_queue[order(governance_queue$total_link_degree, governance_queue$cluster, governance_queue$slug),]

catalog <- link_report[, c("slug", "title", "cluster", "status", "article_type", "incoming_links", "outgoing_links", "total_link_degree", "network_role", "governance_flag")]
catalog$catalog_product <- "Catalyst Canvas"
catalog$series <- "Content Frameworks"
catalog$github_path <- paste0("articles/", catalog$slug, "/")
catalog <- catalog[, c("catalog_product", "series", "slug", "title", "cluster", "status", "article_type", "incoming_links", "outgoing_links", "total_link_degree", "network_role", "governance_flag", "github_path")]

write.csv(link_report, file.path(tables_dir, "r_internal_link_degree_report.csv"), row.names = FALSE)
write.csv(cluster_report, file.path(tables_dir, "r_cluster_link_coverage_report.csv"), row.names = FALSE)
write.csv(link_type_summary, file.path(tables_dir, "r_link_type_summary.csv"), row.names = FALSE)
write.csv(priority_summary, file.path(tables_dir, "r_link_priority_summary.csv"), row.names = FALSE)
write.csv(status_summary, file.path(tables_dir, "r_link_status_summary.csv"), row.names = FALSE)
write.csv(governance_queue, file.path(tables_dir, "r_internal_link_governance_queue.csv"), row.names = FALSE)
write.csv(catalog, file.path(catalog_dir, "r_catalyst_canvas_internal_link_catalog.csv"), row.names = FALSE)

png(file.path(figures_dir, "r_total_link_degree_by_article.png"), width = 1300, height = 850)
barplot(link_report$total_link_degree, names.arg = link_report$slug, las = 2, main = "Total Internal-Link Degree by Article", ylab = "Incoming + outgoing links")
dev.off()

png(file.path(figures_dir, "r_cluster_link_density.png"), width = 1100, height = 750)
barplot(cluster_report$link_density_proxy, names.arg = cluster_report$cluster, las = 2, main = "Cluster Link Density Proxy", ylab = "Links per article")
dev.off()

png(file.path(figures_dir, "r_link_relationship_types.png"), width = 1100, height = 750)
barplot(link_type_summary$link_count, names.arg = link_type_summary$relationship_type, las = 2, main = "Internal Link Relationship Types", ylab = "Link count")
dev.off()

summary_lines <- c(
  "# Catalyst Canvas Internal-Link Infrastructure Analysis",
  "",
  "Article: Internal Linking as Framework Infrastructure",
  "",
  paste0("- Article records: ", nrow(articles)),
  paste0("- Internal-link records: ", nrow(links)),
  paste0("- Articles needing governance review: ", nrow(governance_queue)),
  paste0("- Relationship types: ", nrow(link_type_summary)),
  "",
  "Generated outputs support editorial review of internal-link infrastructure."
)
writeLines(summary_lines, file.path(reports_dir, "r_internal_link_framework_audit.md"))
print("Catalyst Canvas R internal-link analysis complete.")
