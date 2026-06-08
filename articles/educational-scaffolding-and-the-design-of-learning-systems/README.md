# Educational Scaffolding and the Design of Learning Systems

This companion directory supports the article **"Educational Scaffolding and the Design of Learning Systems."**

The workflows operationalize educational scaffolding as learning-system infrastructure: article sequence, prerequisite relationships, concept coverage, cognitive-load indicators, orientation support, worked examples, feedback prompts, transfer support, accessibility metadata, scaffold-readiness scoring, governance queues, and catalog exports.

## Core Claim

Educational scaffolding turns a content framework into a learning system by helping readers move from orientation to understanding, guided practice, transfer, and independent use.

## Professional Workflow Layer

The Python and R workflows are designed as product-grade learning-system scaffolds:

- learning-path inventory
- prerequisite mapping
- article sequence validation
- concept-cluster coverage analysis
- orientation support checks
- worked-example coverage
- feedback prompt review
- transfer support review
- cognitive-load risk flags
- accessibility scaffold indicators
- scaffold-readiness scoring
- governance review queues
- catalog exports
- CSV, JSON, Markdown, and figure outputs
- non-destructive synthetic datasets for reproducible testing

## Repository Structure

- `config/` — scaffolding audit configuration and scoring rules
- `html/` — article templates, GitHub blocks, footer navigation, tables, and methods wrappers
- `css/` — reusable styling patterns for article maps, metadata blocks, tables, cards, and editorial wrappers
- `php/` — WordPress-oriented template parts, footer logic, metadata rendering, and learning-system helpers
- `java/` — learning-path and scaffold-readiness model examples
- `python/` — learning-path and educational-scaffolding audit engine
- `r/` — concept coverage, sequence readiness, and learning-system reporting
- `sql/` — schemas for learning-path inventory, prerequisites, scaffold features, and governance status
- `docs/` — article notes, modeling principles, implementation notes, and editorial documentation
- `data/` — synthetic datasets
- `outputs/` — generated outputs
- `notebooks/` — notebook placeholders

## Quick Start

From this article directory:

```bash
python3 python/run_all_scaffolding_workflows.py
Rscript r/run_all_scaffolding_workflows.R
javac java/EducationalScaffoldingModel.java && java -cp java EducationalScaffoldingModel
sqlite3 outputs/educational_scaffolding.sqlite < sql/educational_scaffolding_schema.sql
sqlite3 -header -csv outputs/educational_scaffolding.sqlite < sql/educational_scaffolding_queries.sql > outputs/tables/sql_educational_scaffolding_report.csv
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
