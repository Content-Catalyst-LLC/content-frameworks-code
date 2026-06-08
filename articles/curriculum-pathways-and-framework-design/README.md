# Curriculum Pathways and Framework Design

This companion directory supports the article **Curriculum Pathways and Framework Design**.

The workflows model curriculum pathways as learning-system infrastructure: pathway inventories, prerequisite mapping, learning-objective coverage, learning-stage distribution, accessibility checks, feedback and assessment support, transfer support, governance queues, and catalog exports.

## Repository Structure

- `config/` — scoring rules and pathway configuration
- `html/` — article components, GitHub block, footer navigation, method wrapper
- `css/` — reusable styling patterns
- `php/` — WordPress-oriented snippets
- `java/` — pathway-readiness scoring example
- `python/` — professional pathway audit workflow
- `r/` — pathway coverage and governance summaries
- `sql/` — schema and reporting queries
- `docs/` — article notes and governance notes
- `data/` — synthetic datasets
- `outputs/` — generated outputs
- `notebooks/` — notebook placeholders

## Quick Start

```bash
python3 python/run_all_curriculum_pathway_workflows.py
Rscript r/run_all_curriculum_pathway_workflows.R
javac java/CurriculumPathwayAudit.java && java -cp java CurriculumPathwayAudit
sqlite3 outputs/curriculum_pathways.sqlite < sql/curriculum_pathway_schema.sql
sqlite3 -header -csv outputs/curriculum_pathways.sqlite < sql/curriculum_pathway_queries.sql > outputs/tables/sql_curriculum_pathway_report.csv
```

## Catalyst Canvas Readiness Layer

This article folder includes `canvas/`, `python/content_framework_canvas/`, tests, JSON exports, and governance queue outputs for Catalyst Canvas integration.
