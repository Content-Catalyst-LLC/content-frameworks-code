# Content Frameworks: Framework Library Analysis in R
# Educational example only.

library(tidyverse)

frameworks <- read_csv("../data/framework_library.csv", show_col_types = FALSE)

frameworks <- frameworks |>
  mutate(
    framework_profile =
      0.22 * complexity_level +
      0.20 * transferability -
      0.12 * ethical_risk +
      0.24 * knowledge_depth +
      0.22 * action_support,
    requires_caution =
      ethical_risk > 0.50 | knowledge_depth < 0.50
  )

frameworks_long <- frameworks |>
  pivot_longer(
    cols = c(
      complexity_level,
      transferability,
      ethical_risk,
      knowledge_depth,
      action_support
    ),
    names_to = "dimension",
    values_to = "value"
  )

dir.create("../outputs", showWarnings = FALSE, recursive = TRUE)

write_csv(frameworks, "../outputs/r_framework_library_scored.csv")
write_csv(frameworks_long, "../outputs/r_framework_library_long.csv")

print(frameworks)
