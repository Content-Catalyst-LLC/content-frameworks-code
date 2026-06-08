# Jobs to Be Done and the Problem of Audience Need

This companion directory supports the article **Jobs to Be Done and the Problem of Audience Need**.

The workflows model Jobs to Be Done as governed content infrastructure: audience job statements, situation clarity, desired outcomes, content fit, evidence support, functional/emotional/social/strategic/learning jobs, next-step fit, audience agency, governance queues, and catalog exports.

## Repository Structure

- `config/` — scoring rules and JTBD configuration
- `html/` — article components, GitHub block, footer navigation, method wrapper
- `css/` — reusable styling patterns
- `php/` — WordPress-oriented snippets
- `java/` — JTBD readiness scoring example
- `python/` — professional JTBD content audit workflow
- `r/` — audience job, outcome, and content-fit summaries
- `sql/` — schema and reporting queries
- `docs/` — article notes and governance notes
- `data/` — synthetic datasets
- `outputs/` — generated outputs
- `notebooks/` — notebook placeholders

## Quick Start

```bash
python3 python/run_all_jtbd_content_workflows.py
Rscript r/run_all_jtbd_content_workflows.R
javac java/JTBDContentAudit.java && java -cp java JTBDContentAudit
sqlite3 outputs/jtbd_content.sqlite < sql/jtbd_content_schema.sql
sqlite3 -header -csv outputs/jtbd_content.sqlite < sql/jtbd_content_queries.sql > outputs/tables/sql_jtbd_content_report.csv
```
