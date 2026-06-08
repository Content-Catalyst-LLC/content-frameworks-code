# Why Frameworks Matter in Research, Education, and Strategic Communication

This companion directory supports the article **"Why Frameworks Matter in Research, Education, and Strategic Communication."**

The workflows operationalize framework value as a professional content-system problem: article-map coverage, framework-value scoring, metadata quality, internal-link graph diagnostics, taxonomy coverage, evidence readiness, governance review, and Catalyst Canvas-style catalog export.

## Core Claim

Frameworks matter because complex knowledge rarely becomes usable on its own. In research, frameworks help move from evidence to interpretation. In education, they help sequence learning. In strategic communication, they help align claims, audiences, proof points, and action.

## Professional Workflow Layer

The Python and R workflows are designed as Catalyst Canvas-ready scaffolds:

- configuration-driven audit rules
- schema validation for required article fields
- metadata completeness and quality scoring
- article-map coverage diagnostics
- framework value scoring across comprehension, comparison, retention, action, and governance
- internal-link graph metrics, hub detection, isolated-node checks, and link recommendations
- taxonomy coverage and category balance review
- governance queue generation
- CSV, JSON, Markdown, and catalog-export outputs
- non-destructive, reproducible synthetic data

## Repository Structure

- `config/` — audit configuration and scoring rules
- `html/` — article templates, metadata blocks, navigation patterns, tables, GitHub blocks, and footer navigation
- `css/` — reusable styling patterns for article maps, metadata blocks, tables, cards, and editorial wrappers
- `php/` — WordPress-oriented template parts, reusable snippets, article-footer logic, metadata rendering, and content-system helpers
- `java/` — content models, metadata-schema objects, article-map validators, framework classifiers, and editorial workflow logic
- `python/` — Catalyst Canvas-style audit engine, graph diagnostics, metadata checks, framework scoring, and catalog exports
- `r/` — framework-library comparison, content-audit summaries, editorial coverage analysis, taxonomy summaries, and figures
- `sql/` — schemas for articles, framework value, metadata, links, references, and editorial status
- `docs/` — article notes, modeling principles, implementation notes, and editorial documentation
- `data/` — synthetic datasets
- `outputs/` — generated outputs
- `notebooks/` — notebook placeholders

## Quick Start

From this article directory:

```bash
python3 python/run_all_framework_value_workflows.py
Rscript r/run_all_framework_value_workflows.R
javac java/FrameworkValueModel.java && java -cp java FrameworkValueModel
sqlite3 outputs/framework_value.sqlite < sql/framework_value_schema.sql
sqlite3 -header -csv outputs/framework_value.sqlite < sql/framework_value_queries.sql > outputs/tables/sql_framework_value_report.csv
```

Outputs are written to:

```text
outputs/tables/
outputs/reports/
outputs/figures/
outputs/audit_logs/
outputs/catalog_exports/
```

## Catalyst Canvas Readiness Layer

This article folder includes a Canvas-ready integration layer:

- `canvas/canvas_manifest.json`
- `canvas/input_schema.json`
- `canvas/output_schema.json`
- `canvas/canvas_cards.json`
- `canvas/governance_queue.json`
- `python/content_framework_canvas/`
- `python/tests/`
- `outputs/json/`
- `outputs/markdown/`

Run the audit from the article directory:

```bash
PYTHONPATH=python python3 -m content_framework_canvas.cli --article-root .
```

Run tests:

```bash
PYTHONPATH=python python3 -m unittest discover -s python/tests -p "test_*.py"
```
