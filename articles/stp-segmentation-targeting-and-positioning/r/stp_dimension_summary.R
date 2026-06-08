# Summarize STP dimensions.

source_path <- file.path("outputs", "tables", "stp_segment_positioning_summary.csv")
stp <- read.csv(source_path, stringsAsFactors = FALSE)

metrics <- c(
  "need_intensity",
  "strategic_fit",
  "reachability",
  "evidence_fit",
  "ethical_responsibility",
  "positioning_score"
)

summary <- data.frame(
  metric = metrics,
  mean = as.numeric(colMeans(stp[, metrics])),
  minimum = as.numeric(apply(stp[, metrics], 2, min)),
  maximum = as.numeric(apply(stp[, metrics], 2, max))
)

write.csv(summary, file.path("outputs", "tables", "stp_dimension_summary.csv"), row.names = FALSE)
print(summary)
