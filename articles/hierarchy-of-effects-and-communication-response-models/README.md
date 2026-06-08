# Hierarchy of Effects and Communication Response Models

This companion directory supports the article **Hierarchy of Effects and Communication Response Models**.

The workflows model communication response as governed staged infrastructure: awareness, knowledge, liking, preference, conviction, action, follow-through, evidence support, audience readiness, measurement alignment, ethical-risk flags, governance queues, and catalog exports.

## Repository Structure

- `config/` — scoring rules and communication response configuration
- `html/` — article components, GitHub block, footer navigation, method wrapper
- `css/` — reusable styling patterns
- `php/` — WordPress-oriented snippets
- `java/` — communication-response readiness scoring example
- `python/` — professional response-stage audit workflow
- `r/` — stage balance and governance summaries
- `sql/` — schema and reporting queries
- `docs/` — article notes and governance notes
- `data/` — synthetic datasets
- `outputs/` — generated outputs
- `notebooks/` — notebook placeholders

## Quick Start

```bash
python3 python/run_all_communication_response_workflows.py
Rscript r/run_all_communication_response_workflows.R
javac java/CommunicationResponseAudit.java && java -cp java CommunicationResponseAudit
sqlite3 outputs/communication_response.sqlite < sql/communication_response_schema.sql
sqlite3 -header -csv outputs/communication_response.sqlite < sql/communication_response_queries.sql > outputs/tables/sql_communication_response_report.csv
```
