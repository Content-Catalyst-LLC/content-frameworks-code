# Internal Linking as Framework Infrastructure

This companion directory supports the article **"Internal Linking as Framework Infrastructure."**

The workflows operationalize internal linking as framework infrastructure: article inventory, semantic relationship typing, link graph diagnostics, orphan detection, link-depth scoring, cluster coherence, anchor-text governance, editorial review queues, and Catalyst Canvas-style catalog exports.

## Professional Workflow Layer

The Python and R workflows are designed as Catalyst Canvas-ready scaffolds:

- configuration-driven link-audit rules
- article inventory validation
- semantic link-type classification
- incoming, outgoing, and total degree diagnostics
- orphan and thinly linked article detection
- hub and bridge article classification
- shortest-path link-depth estimates from article-map hubs
- cluster coherence and bridge-link summaries
- anchor-text quality flags
- metadata readiness checks
- governance queue generation
- CSV, JSON, Markdown, and catalog-export outputs
- reproducible synthetic data for testing

## Repository Structure

- `config/` — link-audit configuration and scoring rules
- `html/` — article templates, GitHub blocks, footer navigation, tables, and methods wrappers
- `css/` — reusable styling patterns for content frameworks
- `php/` — WordPress-oriented template parts and content-system helpers
- `java/` — content graph model and link relationship validation examples
- `python/` — Catalyst Canvas-style internal-link graph audit engine
- `r/` — link coverage, cluster coherence, relationship-type summaries, and governance figures
- `sql/` — schemas for article inventory, internal links, link types, anchor text, and governance status
- `docs/` — article notes, modeling principles, implementation notes, and editorial documentation
- `data/` — synthetic datasets
- `outputs/` — generated outputs
- `notebooks/` — notebook placeholders

## Quick Start

```bash
python3 python/run_all_internal_link_workflows.py
Rscript r/run_all_internal_link_workflows.R
javac java/InternalLinkGraphModel.java && java -cp java InternalLinkGraphModel
sqlite3 outputs/internal_links.sqlite < sql/internal_link_schema.sql
sqlite3 -header -csv outputs/internal_links.sqlite < sql/internal_link_queries.sql > outputs/tables/sql_internal_link_report.csv
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
