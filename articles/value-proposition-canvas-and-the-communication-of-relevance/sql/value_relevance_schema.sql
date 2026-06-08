DROP TABLE IF EXISTS value_relevance_items;

CREATE TABLE value_relevance_items (
  item_id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  audience_segment TEXT NOT NULL,
  status TEXT NOT NULL,
  job_alignment REAL NOT NULL,
  pain_relief_alignment REAL NOT NULL,
  gain_creation_alignment REAL NOT NULL,
  evidence_strength REAL NOT NULL,
  communication_clarity REAL NOT NULL,
  ethical_fit REAL NOT NULL,
  primary_risk TEXT NOT NULL
);

INSERT INTO value_relevance_items VALUES
('VPC001','Value Proposition Canvas article introduction','content strategists','published',0.91,0.84,0.86,0.76,0.90,0.88,'none'),
('VPC002','Generic feature summary','broad audience','draft',0.42,0.38,0.50,0.35,0.61,0.54,'feature_translation_failure'),
('VPC003','Research communication framework overview','research communicators','published',0.86,0.81,0.80,0.83,0.78,0.84,'none'),
('VPC004','Audience journey explainer','editors','published',0.79,0.75,0.83,0.70,0.81,0.82,'missing_limitations'),
('VPC005','Promotional platform landing page','prospects','draft',0.65,0.58,0.74,0.46,0.68,0.49,'promotional_drift'),
('VPC006','Public policy explainer','civic readers','planned',0.88,0.82,0.77,0.85,0.74,0.90,'none');
