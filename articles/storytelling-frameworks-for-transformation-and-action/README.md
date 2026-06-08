# Storytelling Frameworks for Transformation and Action

This companion directory supports the article **Storytelling Frameworks for Transformation and Action**.

The workflows model storytelling frameworks as governed narrative infrastructure: setting, actors, agency, tension, sequence, transformation, evidence support, action fit, representation review, ethical-risk flags, governance queues, and catalog exports.

## Repository Structure

- `config/` — scoring rules and storytelling framework configuration
- `html/` — article components, GitHub block, footer navigation, method wrapper
- `css/` — reusable styling patterns
- `php/` — WordPress-oriented snippets
- `java/` — storytelling-readiness scoring example
- `python/` — professional storytelling framework audit workflow
- `r/` — narrative balance and governance summaries
- `sql/` — schema and reporting queries
- `docs/` — article notes and governance notes
- `data/` — synthetic datasets
- `outputs/` — generated outputs
- `notebooks/` — notebook placeholders

## Quick Start

```bash
python3 python/run_all_storytelling_framework_workflows.py
Rscript r/run_all_storytelling_framework_workflows.R
javac java/StorytellingFrameworkAudit.java && java -cp java StorytellingFrameworkAudit
sqlite3 outputs/storytelling_framework.sqlite < sql/storytelling_framework_schema.sql
sqlite3 -header -csv outputs/storytelling_framework.sqlite < sql/storytelling_framework_queries.sql > outputs/tables/sql_storytelling_framework_report.csv
```

## Catalyst Canvas Readiness Layer

This article folder includes `canvas/`, `python/content_framework_canvas/`, tests, JSON exports, and governance queue outputs for Catalyst Canvas integration.
