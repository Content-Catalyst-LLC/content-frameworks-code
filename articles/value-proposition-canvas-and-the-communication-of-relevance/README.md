# Value Proposition Canvas and the Communication of Relevance

This companion directory supports the article **Value Proposition Canvas and the Communication of Relevance**.

The workflows model value-proposition communication as auditable content infrastructure: audience jobs, pains, gains, products and services, pain relievers, gain creators, evidence support, claim strength, message clarity, ethical risk, and relevance fit.

## Repository Structure

- `config/` — scoring rules and value-proposition dimensions
- `html/` — article components, GitHub block, footer navigation, method wrapper
- `css/` — reusable styling patterns
- `php/` — WordPress-oriented snippets
- `java/` — value-relevance scoring example
- `python/` — professional value-relevance audit workflow
- `r/` — canvas coverage and relevance reporting workflow
- `sql/` — schema and reporting queries
- `c/`, `cpp/`, `go/`, `rust/`, `julia/`, `fortran/` — small cross-language scoring examples
- `docs/` — article notes and governance notes
- `data/` — synthetic datasets
- `outputs/` — generated outputs
- `notebooks/` — notebook placeholders

## Quick Start

```bash
python3 python/run_all_value_relevance_workflows.py
Rscript r/run_all_value_relevance_workflows.R
sqlite3 outputs/value_relevance.sqlite < sql/value_relevance_schema.sql
sqlite3 -header -csv outputs/value_relevance.sqlite < sql/value_relevance_queries.sql > outputs/tables/sql_value_relevance_report.csv
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
