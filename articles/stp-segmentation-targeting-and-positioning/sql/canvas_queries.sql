-- Catalyst Canvas STP queries.
-- Run from the article directory after loading data into stp_canvas_segments.

.headers on
.mode column

SELECT
  segment,
  weighted_target_score,
  positioning_score,
  positioning_gap,
  ethical_review_flag,
  status
FROM stp_canvas_scores
ORDER BY weighted_target_score DESC;

SELECT
  segment,
  positioning_gap,
  ethical_review_flag,
  status
FROM stp_canvas_scores
WHERE positioning_gap >= 0.10
   OR ethical_review_flag != 'standard review'
   OR status IN ('review', 'revise')
ORDER BY positioning_gap DESC;
