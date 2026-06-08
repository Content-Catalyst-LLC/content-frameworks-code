-- Sample STP analysis queries.

.mode csv
.import --skip 1 data/stp_segments.csv stp_segments

.headers on

SELECT
  segment,
  ROUND(weighted_target_score, 3) AS weighted_target_score,
  ROUND(positioning_score, 3) AS positioning_score,
  ROUND(positioning_gap, 3) AS positioning_gap,
  ethical_review_flag
FROM stp_scores
ORDER BY weighted_target_score DESC;

SELECT
  segment,
  ROUND(positioning_gap, 3) AS positioning_gap,
  ethical_review_flag
FROM stp_scores
WHERE positioning_gap >= 0.10
   OR ethical_review_flag != 'standard review'
ORDER BY positioning_gap DESC;
