# Framework Composition: How to Combine Models Without Confusion

Companion code for the Content Frameworks article **“Framework Composition: How to Combine Models Without Confusion.”**

This scaffold is Catalyst Canvas-ready. It includes html, css, php, java, python, r, sql, docs, data, outputs, notebooks, shared, and canvas layers, with package-style Python, JSON schemas, Canvas manifest metadata, UI-card exports, governance queue exports, tests, SQL views, synthetic data, and generated outputs.

## Run the Catalyst Canvas audit

From this article directory:

```bash
PYTHONPATH=python python3 -m framework_composition_canvas.cli --article-root .
```

Or:

```bash
python3 python/run_framework_composition_canvas_audit.py
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

- `outputs/tables/framework_composition_canvas_audit.csv`
- `outputs/json/catalog.json`
- `outputs/json/canvas_cards.json`
- `outputs/json/governance_queue.json`
- `outputs/json/framework_composition_canvas_export.json`
- `outputs/markdown/governance_queue.md`

## Purpose

The module treats framework composition as an auditable content-governance system. It evaluates purpose fit, role clarity, boundary clarity, sequence clarity, translation quality, evidence alignment, governance readiness, audience burden, conflict risk, confusion risk, review priority, and governance status.
