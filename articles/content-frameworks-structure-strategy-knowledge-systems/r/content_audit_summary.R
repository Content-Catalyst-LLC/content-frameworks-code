# Content Frameworks: Content Audit Summary in R
# Educational example only.

library(tidyverse)

audit <- read_csv("../data/content_audit.csv", show_col_types = FALSE)

audit <- audit |>
  mutate(
    word_score = pmin(word_count / 3000, 1),
    link_score = pmin(internal_links / 10, 1),
    reference_score = pmin(references / 10, 1),
    metadata_score =
      0.34 * as.numeric(has_image_metadata) +
      0.33 * as.numeric(has_excerpt) +
      0.33 * as.numeric(has_repository_link),
    completion_score =
      0.30 * word_score +
      0.25 * link_score +
      0.25 * reference_score +
      0.20 * metadata_score,
    needs_review =
      completion_score < 0.75 | internal_links < 6 | references < 6
  ) |>
  arrange(completion_score)

summary <- audit |>
  group_by(status) |>
  summarise(
    article_count = n(),
    mean_completion_score = mean(completion_score),
    mean_internal_links = mean(internal_links),
    mean_references = mean(references),
    .groups = "drop"
  )

dir.create("../outputs", showWarnings = FALSE, recursive = TRUE)

write_csv(audit, "../outputs/r_content_audit_scores.csv")
write_csv(summary, "../outputs/r_content_audit_summary.csv")

print(audit)
print(summary)
