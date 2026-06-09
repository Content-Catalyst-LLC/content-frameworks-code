# SWOT Analysis: Strengths, Uses, and Limits

Companion code for the Content Frameworks article **“SWOT Analysis: Strengths, Uses, and Limits.”**

This scaffold is Catalyst Canvas-ready. It includes html, css, php, java, python, r, sql, docs, data, outputs, notebooks, shared, and canvas layers, with package-style Python, JSON schemas, Canvas manifest metadata, UI-card exports, governance queue exports, tests, SQL views, synthetic data, and generated outputs.

## Run the Catalyst Canvas audit

From this article directory:

```bash
PYTHONPATH=python python3 -m swot_canvas.cli --article-root .
```

Or:

```bash
python3 python/run_swot_canvas_audit.py
```

## Run tests

```bash
PYTHONPATH=python python3 -m unittest discover -s python/tests -p "test_*.py"
```

## Key Canvas files

- `canvas/canvas_manifest.json`
- `canvas/input_schema.json`
- `canvas/output_schema.json`
- `canvas/canvas_cards.json`
- `canvas/governance_queue.json`

## Baseline folders

- `html/`
- `css/`
- `php/`
- `java/`
- `python/`
- `r/`
- `sql/`
- `docs/`
- `data/`
- `outputs/`
- `notebooks/`
- `shared/`
- `canvas/`

## Generated outputs

- `outputs/tables/swot_canvas_audit.csv`
- `outputs/json/catalog.json`
- `outputs/json/canvas_cards.json`
- `outputs/json/governance_queue.json`
- `outputs/json/swot_canvas_export.json`
- `outputs/markdown/governance_queue.md`

## Purpose

The module treats SWOT analysis as an auditable strategic content-framework asset. It evaluates quadrant classification, internal/external orientation, impact, confidence, urgency, feasibility, strategic fit, evidence strength, claim strength, evidence gaps, governance priority, and review status.
