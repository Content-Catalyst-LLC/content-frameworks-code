# 5W1H and the Architecture of Explanatory Completeness

This companion directory supports the article **5W1H and the Architecture of Explanatory Completeness**.

The workflows model 5W1H as governed explanatory-completeness infrastructure: who, what, when, where, why, and how coverage; evidence support; explanatory balance; audience fit; freshness risk; governance queues; and catalog exports.

## Repository Structure

- `config/` — scoring rules and 5W1H completeness configuration
- `html/` — article components, GitHub block, footer navigation, method wrapper
- `css/` — reusable styling patterns
- `php/` — WordPress-oriented snippets
- `java/` — explanatory-readiness scoring example
- `python/` — professional 5W1H completeness audit workflow
- `r/` — question coverage and governance summaries
- `sql/` — schema and reporting queries
- `docs/` — article notes and governance notes
- `data/` — synthetic datasets
- `outputs/` — generated outputs
- `notebooks/` — notebook placeholders

## Quick Start

```bash
python3 python/run_all_five_w_one_h_workflows.py
Rscript r/run_all_five_w_one_h_workflows.R
javac java/FiveWOneHAudit.java && java -cp java FiveWOneHAudit
sqlite3 outputs/five_w_one_h.sqlite < sql/five_w_one_h_schema.sql
sqlite3 -header -csv outputs/five_w_one_h.sqlite < sql/five_w_one_h_queries.sql > outputs/tables/sql_five_w_one_h_report.csv
```

## Catalyst Canvas Readiness Layer

This article folder includes `canvas/`, `python/content_framework_canvas/`, tests, JSON exports, and governance queue outputs for Catalyst Canvas integration.
