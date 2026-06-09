# Base R workflow for BCG portfolio position and governance diagnostics.

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)

if (length(file_arg) > 0) {
  script_path <- normalizePath(sub("^--file=", "", file_arg[1]), mustWork = TRUE)
  article_root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)
} else {
  article_root <- getwd()
}

setwd(article_root)

data_path <- file.path(article_root, "data", "bcg_portfolio_items.csv")
tables_dir <- file.path(article_root, "outputs", "tables")
figures_dir <- file.path(article_root, "outputs", "figures")

if (!dir.exists(tables_dir)) dir.create(tables_dir, recursive = TRUE)
if (!dir.exists(figures_dir)) dir.create(figures_dir, recursive = TRUE)

portfolio <- read.csv(data_path, stringsAsFactors = FALSE)

growth_threshold <- 0.60
share_threshold <- 0.60

portfolio$quadrant <- ifelse(
  portfolio$growth_score >= growth_threshold & portfolio$relative_share_score >= share_threshold,
  "star",
  ifelse(
    portfolio$growth_score < growth_threshold & portfolio$relative_share_score >= share_threshold,
    "cash_cow",
    ifelse(
      portfolio$growth_score >= growth_threshold & portfolio$relative_share_score < share_threshold,
      "question_mark",
      "review_quadrant"
    )
  )
)

portfolio$evidence_gap <- pmax(0, portfolio$claim_strength - portfolio$evidence_strength)

quadrant_weight <- ifelse(
  portfolio$quadrant == "star",
  0.85,
  ifelse(
    portfolio$quadrant == "cash_cow",
    0.60,
    ifelse(portfolio$quadrant == "question_mark", 0.78, 0.70)
  )
)

portfolio$portfolio_priority <- pmin(
  1,
  quadrant_weight * 0.35 +
    portfolio$strategic_fit * 0.30 +
    portfolio$maintenance_burden * 0.15 +
    portfolio$evidence_gap * 0.20
)

portfolio$review_priority <- ifelse(
  portfolio$status == "revise" | portfolio$evidence_gap >= 0.30,
  "high",
  ifelse(
    portfolio$portfolio_priority >= 0.70 |
      portfolio$evidence_gap >= 0.15 |
      portfolio$status == "review",
    "medium",
    "standard"
  )
)

portfolio <- portfolio[order(portfolio$portfolio_priority, decreasing = TRUE), ]

write.csv(
  portfolio,
  file.path(tables_dir, "bcg_portfolio_summary.csv"),
  row.names = FALSE
)

governance_queue <- portfolio[portfolio$review_priority != "standard", ]

write.csv(
  governance_queue,
  file.path(tables_dir, "bcg_governance_queue.csv"),
  row.names = FALSE
)

png(file.path(figures_dir, "bcg_portfolio_position.png"), width = 1000, height = 800)
plot(
  portfolio$relative_share_score,
  portfolio$growth_score,
  xlab = "Relative share score",
  ylab = "Growth score",
  main = "BCG Portfolio Position",
  pch = 19,
  xlim = c(0, 1),
  ylim = c(0, 1)
)
abline(h = growth_threshold, lty = 2)
abline(v = share_threshold, lty = 2)
text(
  portfolio$relative_share_score,
  portfolio$growth_score,
  labels = portfolio$item,
  pos = 4,
  cex = 0.75
)
grid()
dev.off()

png(file.path(figures_dir, "bcg_portfolio_priority.png"), width = 1200, height = 700)
barplot(
  portfolio$portfolio_priority,
  names.arg = portfolio$item,
  las = 2,
  ylab = "Portfolio priority",
  main = "BCG Portfolio Communication Priority"
)
grid()
dev.off()

print(portfolio[, c("item", "quadrant", "growth_score", "relative_share_score", "evidence_gap", "portfolio_priority", "review_priority")])
