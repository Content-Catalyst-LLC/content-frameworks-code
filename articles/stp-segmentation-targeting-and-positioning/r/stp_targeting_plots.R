# Base R plots for STP targeting diagnostics.

stp <- read.csv(file.path("outputs", "tables", "stp_segment_positioning_summary.csv"), stringsAsFactors = FALSE)

if (!dir.exists(file.path("outputs", "figures"))) {
  dir.create(file.path("outputs", "figures"), recursive = TRUE)
}

png(file.path("outputs", "figures", "stp_target_vs_positioning.png"), width = 1200, height = 800)
plot(
  stp$weighted_target_score,
  stp$positioning_score,
  xlab = "Weighted target score",
  ylab = "Positioning score",
  main = "Target Priority vs Positioning Strength",
  pch = 19
)
text(stp$weighted_target_score, stp$positioning_score, labels = stp$segment, pos = 4, cex = 0.8)
grid()
dev.off()
