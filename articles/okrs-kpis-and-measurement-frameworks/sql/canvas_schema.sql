-- Catalyst Canvas schema for OKR KPI and measurement framework diagnostics.

DROP TABLE IF EXISTS measurement_items;

CREATE TABLE measurement_items (
  item TEXT PRIMARY KEY,
  measurement_type TEXT NOT NULL CHECK (measurement_type IN ('OKR objective', 'key result', 'KPI', 'metric', 'threshold', 'dashboard item')),
  description TEXT NOT NULL,
  strategic_relevance REAL NOT NULL CHECK (strategic_relevance BETWEEN 0 AND 1),
  validity REAL NOT NULL CHECK (validity BETWEEN 0 AND 1),
  reliability REAL NOT NULL CHECK (reliability BETWEEN 0 AND 1),
  actionability REAL NOT NULL CHECK (actionability BETWEEN 0 AND 1),
  timeliness REAL NOT NULL CHECK (timeliness BETWEEN 0 AND 1),
  evidence_strength REAL NOT NULL CHECK (evidence_strength BETWEEN 0 AND 1),
  gaming_risk REAL NOT NULL CHECK (gaming_risk BETWEEN 0 AND 1),
  reporting_burden REAL NOT NULL CHECK (reporting_burden BETWEEN 0 AND 1),
  ambiguity REAL NOT NULL CHECK (ambiguity BETWEEN 0 AND 1),
  claim_strength REAL NOT NULL CHECK (claim_strength BETWEEN 0 AND 1),
  owner TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('active', 'review', 'revise', 'archive')),
  review_date TEXT NOT NULL
);

DROP VIEW IF EXISTS measurement_scores;

CREATE VIEW measurement_scores AS
SELECT
  item,
  measurement_type,
  description,
  strategic_relevance,
  validity,
  reliability,
  actionability,
  timeliness,
  evidence_strength,
  gaming_risk,
  reporting_burden,
  ambiguity,
  claim_strength,
  ROUND((validity + reliability + strategic_relevance + actionability + timeliness) / 5.0, 3) AS quality_score,
  ROUND(
    CASE
      WHEN gaming_risk * 0.30 + ambiguity * 0.25 + reporting_burden * 0.20 + (1 - evidence_strength) * 0.25 > 1 THEN 1
      ELSE gaming_risk * 0.30 + ambiguity * 0.25 + reporting_burden * 0.20 + (1 - evidence_strength) * 0.25
    END,
    3
  ) AS measurement_risk,
  ROUND(
    CASE
      WHEN claim_strength - evidence_strength > 0 THEN claim_strength - evidence_strength
      ELSE 0
    END,
    3
  ) AS evidence_gap,
  ROUND(
    CASE
      WHEN (
        (CASE
          WHEN gaming_risk * 0.30 + ambiguity * 0.25 + reporting_burden * 0.20 + (1 - evidence_strength) * 0.25 > 1 THEN 1
          ELSE gaming_risk * 0.30 + ambiguity * 0.25 + reporting_burden * 0.20 + (1 - evidence_strength) * 0.25
        END) * 0.40
        + (CASE WHEN claim_strength - evidence_strength > 0 THEN claim_strength - evidence_strength ELSE 0 END) * 0.30
        + (1 - ((validity + reliability + strategic_relevance + actionability + timeliness) / 5.0)) * 0.30
      ) > 1 THEN 1
      ELSE (
        (CASE
          WHEN gaming_risk * 0.30 + ambiguity * 0.25 + reporting_burden * 0.20 + (1 - evidence_strength) * 0.25 > 1 THEN 1
          ELSE gaming_risk * 0.30 + ambiguity * 0.25 + reporting_burden * 0.20 + (1 - evidence_strength) * 0.25
        END) * 0.40
        + (CASE WHEN claim_strength - evidence_strength > 0 THEN claim_strength - evidence_strength ELSE 0 END) * 0.30
        + (1 - ((validity + reliability + strategic_relevance + actionability + timeliness) / 5.0)) * 0.30
      )
    END,
    3
  ) AS governance_priority,
  owner,
  status,
  review_date
FROM measurement_items;
