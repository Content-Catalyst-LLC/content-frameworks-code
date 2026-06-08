.headers on
.mode csv

SELECT model_type, status, COUNT(*) AS model_count
FROM communication_model_inventory
GROUP BY model_type, status
ORDER BY model_type, status;

SELECT abstraction_risk, COUNT(*) AS model_count
FROM communication_model_inventory
GROUP BY abstraction_risk
ORDER BY abstraction_risk;

SELECT
  m.model_id,
  m.model_name,
  m.model_type,
  COUNT(e.element) AS element_records,
  SUM(CASE WHEN e.present = 'yes' THEN 1 ELSE 0 END) AS present_elements
FROM communication_model_inventory m
LEFT JOIN model_elements e ON m.model_id = e.model_id
GROUP BY m.model_id, m.model_name, m.model_type
ORDER BY present_elements ASC, m.model_id;

SELECT
  m.model_id,
  m.model_name,
  COUNT(r.relationship_type) AS active_relationships
FROM communication_model_inventory m
LEFT JOIN model_relationships r
  ON m.model_id = r.model_id AND r.active = 'yes'
GROUP BY m.model_id, m.model_name
ORDER BY active_relationships ASC, m.model_id;
