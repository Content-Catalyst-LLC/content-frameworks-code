# Frameworks for Research Communication

This companion directory supports the article **Frameworks for Research Communication**.

The workflows model research communication as an auditable content-system practice: claim-support review, source classification, evidence strength, method visibility, uncertainty and limitation checks, audience-context mapping, visualization accessibility, governance queues, and catalog exports.

## Repository Structure

- `config/` — scoring rules and audit configuration
- `html/` — article components, GitHub block, footer navigation, method wrapper
- `css/` — reusable styling patterns
- `php/` — WordPress-oriented snippets
- `java/` — research communication scoring example
- `python/` — professional audit workflow
- `r/` — evidence coverage and governance summaries
- `sql/` — schema and reporting queries
- `docs/` — article notes and governance notes
- `data/` — synthetic datasets
- `outputs/` — generated outputs
- `notebooks/` — notebook placeholders

## Quick Start

```bash
python3 python/run_all_research_communication_workflows.py
Rscript r/run_all_research_communication_workflows.R
javac java/ResearchCommunicationAudit.java && java -cp java ResearchCommunicationAudit
sqlite3 outputs/research_communication.sqlite < sql/research_communication_schema.sql
sqlite3 -header -csv outputs/research_communication.sqlite < sql/research_communication_queries.sql > outputs/tables/sql_research_communication_report.csv
```
