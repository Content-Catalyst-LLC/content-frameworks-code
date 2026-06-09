-- Catalyst Canvas schema for persona frameworks and governance diagnostics.

DROP TABLE IF EXISTS persona_records;

CREATE TABLE persona_records (
  persona TEXT PRIMARY KEY,
  segment TEXT NOT NULL,
  description TEXT NOT NULL,
  content_pathway TEXT NOT NULL,
  evidence_strength REAL NOT NULL CHECK (evidence_strength BETWEEN 0 AND 1),
  specificity REAL NOT NULL CHECK (specificity BETWEEN 0 AND 1),
  content_fit REAL NOT NULL CHECK (content_fit BETWEEN 0 AND 1),
  segment_alignment REAL NOT NULL CHECK (segment_alignment BETWEEN 0 AND 1),
  governance_readiness REAL NOT NULL CHECK (governance_readiness BETWEEN 0 AND 1),
  stereotype_risk REAL NOT NULL CHECK (stereotype_risk BETWEEN 0 AND 1),
  exclusion_risk REAL NOT NULL CHECK (exclusion_risk BETWEEN 0 AND 1),
  weak_evidence_risk REAL NOT NULL CHECK (weak_evidence_risk BETWEEN 0 AND 1),
  overgeneralization_risk REAL NOT NULL CHECK (overgeneralization_risk BETWEEN 0 AND 1),
  owner TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('active', 'review', 'revise', 'archive')),
  review_date TEXT NOT NULL
);

DROP VIEW IF EXISTS persona_scores;

CREATE VIEW persona_scores AS
SELECT
  persona,
  segment,
  description,
  content_pathway,
  ROUND((evidence_strength + specificity + content_fit + segment_alignment + governance_readiness) / 5.0, 3) AS readiness_score,
  ROUND(
    evidence_strength * 0.28 +
    specificity * 0.18 +
    content_fit * 0.20 +
    segment_alignment * 0.18 +
    governance_readiness * 0.16,
    3
  ) AS weighted_readiness,
  ROUND(
    CASE
      WHEN stereotype_risk >= exclusion_risk AND stereotype_risk >= weak_evidence_risk AND stereotype_risk >= overgeneralization_risk THEN stereotype_risk
      WHEN exclusion_risk >= weak_evidence_risk AND exclusion_risk >= overgeneralization_risk THEN exclusion_risk
      WHEN weak_evidence_risk >= overgeneralization_risk THEN weak_evidence_risk
      ELSE overgeneralization_risk
    END,
    3
  ) AS risk_score,
  ROUND(
    CASE
      WHEN (
        CASE
          WHEN stereotype_risk >= exclusion_risk AND stereotype_risk >= weak_evidence_risk AND stereotype_risk >= overgeneralization_risk THEN stereotype_risk
          WHEN exclusion_risk >= weak_evidence_risk AND exclusion_risk >= overgeneralization_risk THEN exclusion_risk
          WHEN weak_evidence_risk >= overgeneralization_risk THEN weak_evidence_risk
          ELSE overgeneralization_risk
        END
      ) - (
        evidence_strength * 0.28 +
        specificity * 0.18 +
        content_fit * 0.20 +
        segment_alignment * 0.18 +
        governance_readiness * 0.16
      ) > 0
      THEN (
        CASE
          WHEN stereotype_risk >= exclusion_risk AND stereotype_risk >= weak_evidence_risk AND stereotype_risk >= overgeneralization_risk THEN stereotype_risk
          WHEN exclusion_risk >= weak_evidence_risk AND exclusion_risk >= overgeneralization_risk THEN exclusion_risk
          WHEN weak_evidence_risk >= overgeneralization_risk THEN weak_evidence_risk
          ELSE overgeneralization_risk
        END
      ) - (
        evidence_strength * 0.28 +
        specificity * 0.18 +
        content_fit * 0.20 +
        segment_alignment * 0.18 +
        governance_readiness * 0.16
      )
      ELSE 0
    END,
    3
  ) AS revision_pressure,
  owner,
  status,
  review_date
FROM persona_records;
