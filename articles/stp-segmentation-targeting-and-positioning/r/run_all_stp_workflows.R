# Run all STP R workflows.

source(file.path("r", "stp_segment_positioning_report.R"))
source(file.path("r", "stp_dimension_summary.R"))
source(file.path("r", "stp_targeting_plots.R"))

cat("All STP R workflows completed.\n")
