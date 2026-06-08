# run_all_narrative_pathway_workflows.R
# Run all R workflows for Narrative Pathways and Knowledge Architecture.

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)

if (length(file_arg) > 0) {
  script_path <- normalizePath(sub("^--file=", "", file_arg[1]), mustWork = TRUE)
  article_root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)
} else {
  article_root <- getwd()
}

source(file.path(article_root, "r", "catalyst_canvas_narrative_pathway_analysis.R"))

message("All R narrative-pathway workflows complete.")
