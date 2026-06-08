# Base R workflow for Content Frameworks coverage.

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)

if (length(file_arg) > 0) {
  script_path <- normalizePath(sub("^--file=", "", file_arg[1]), mustWork = TRUE)
  article_root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)
} else {
  article_root <- getwd()
}

tables_dir <- file.path(article_root, "outputs", "tables")
dir.create(tables_dir, recursive = TRUE, showWarnings = FALSE)

article_map <- read.csv(file.path(article_root, "data", "content_framework_article_map.csv"), stringsAsFactors = FALSE)
coverage <- aggregate(title ~ cluster + status, data = article_map, FUN = length)
names(coverage) <- c("cluster", "status", "article_count")
write.csv(coverage, file.path(tables_dir, "r_article_map_status_summary.csv"), row.names = FALSE)

print(coverage)
