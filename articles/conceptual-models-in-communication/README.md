# Conceptual Models in Communication

This companion directory supports the article **Conceptual Models in Communication**.

The workflows model conceptual communication frameworks as auditable assets: model inventories, model-type classification, element coverage, relationship mapping, audience/context representation, feedback-loop review, evidence and limitation visibility, abstraction-risk scoring, domain-fit review, governance queues, and catalog exports.

## Repository Structure

- `config/` — scoring rules and model-type configuration
- `html/` — article components, GitHub block, footer navigation, method wrapper
- `css/` — reusable styling patterns
- `php/` — WordPress-oriented snippets
- `java/` — communication-model scoring example
- `python/` — professional audit workflow
- `r/` — model coverage and governance summaries
- `sql/` — schema and reporting queries
- `docs/` — article notes and governance notes
- `data/` — synthetic datasets
- `outputs/` — generated outputs
- `notebooks/` — notebook placeholders

## Quick Start

```bash
python3 python/run_all_communication_model_workflows.py
Rscript r/run_all_communication_model_workflows.R
javac java/CommunicationModelAudit.java && java -cp java CommunicationModelAudit
sqlite3 outputs/conceptual_models.sqlite < sql/conceptual_models_schema.sql
sqlite3 -header -csv outputs/conceptual_models.sqlite < sql/conceptual_models_queries.sql > outputs/tables/sql_conceptual_models_report.csv
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
