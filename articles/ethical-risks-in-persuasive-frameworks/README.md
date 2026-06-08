# Ethical Risks in Persuasive Frameworks

This companion directory supports the article **Ethical Risks in Persuasive Frameworks**.

The workflows model persuasive ethics as governed communication infrastructure: agency, evidence support, pressure cues, urgency and scarcity checks, dark-pattern flags, audience vulnerability, accessibility review, responsible action paths, governance queues, and catalog exports.

## Repository Structure

- `config/` — scoring rules and persuasive-risk configuration
- `html/` — article components, GitHub block, footer navigation, method wrapper
- `css/` — reusable styling patterns
- `php/` — WordPress-oriented snippets
- `java/` — responsible-persuasion scoring example
- `python/` — professional persuasive-risk audit workflow
- `r/` — agency, pressure, evidence, and governance summaries
- `sql/` — schema and reporting queries
- `docs/` — article notes and governance notes
- `data/` — synthetic datasets
- `outputs/` — generated outputs
- `notebooks/` — notebook placeholders

## Quick Start

```bash
python3 python/run_all_persuasive_risk_workflows.py
Rscript r/run_all_persuasive_risk_workflows.R
javac java/PersuasiveRiskAudit.java && java -cp java PersuasiveRiskAudit
sqlite3 outputs/persuasive_framework_risk.sqlite < sql/persuasive_framework_risk_schema.sql
sqlite3 -header -csv outputs/persuasive_framework_risk.sqlite < sql/persuasive_framework_risk_queries.sql > outputs/tables/sql_persuasive_framework_risk_report.csv
```
