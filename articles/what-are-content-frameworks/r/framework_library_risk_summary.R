# Base R workflow for framework library summaries.

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

frameworks <- read.csv(file.path(article_root, "data", "framework_library.csv"), stringsAsFactors = FALSE)
domain_summary <- as.data.frame(table(frameworks$domain), stringsAsFactors = FALSE)
names(domain_summary) <- c("domain", "framework_count")
write.csv(domain_summary, file.path(tables_dir, "r_framework_domain_summary.csv"), row.names = FALSE)

print(domain_summary)
