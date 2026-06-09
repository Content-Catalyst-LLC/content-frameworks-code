# AI-Assisted Framework Design

Companion code for the Content Frameworks article **“AI-Assisted Framework Design.”**

This scaffold is Catalyst Canvas-ready. It includes html, css, php, java, python, r, sql, docs, data, outputs, notebooks, shared, and canvas layers, with package-style Python, JSON schemas, Canvas manifest metadata, UI-card exports, governance queue exports, tests, SQL views, synthetic data, and generated outputs.

## Run the Catalyst Canvas audit

From this article directory:

```bash
PYTHONPATH=python python3 -m ai_assisted_framework_design_canvas.cli --article-root .
```

Or:

```bash
python3 python/run_ai_assisted_framework_design_canvas_audit.py
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

- `outputs/tables/ai_assisted_framework_design_canvas_audit.csv`
- `outputs/json/catalog.json`
- `outputs/json/canvas_cards.json`
- `outputs/json/governance_queue.json`
- `outputs/json/ai_assisted_framework_design_canvas_export.json`
- `outputs/markdown/governance_queue.md`

## Purpose

The module treats AI-assisted framework design as an auditable content-governance system. It evaluates conceptual clarity, evidence grounding, metadata consistency, human review strength, bias review, governance maturity, platform readiness, drift control, unsupported-claim risk, generic-structure risk, output validation, audience impact, readiness score, AI framework risk, governance priority, and publication status.

AI belongs in the toolkit, never in control.
