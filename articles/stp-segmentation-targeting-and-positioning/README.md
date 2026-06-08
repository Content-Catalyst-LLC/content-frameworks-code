# STP: Segmentation, Targeting, and Positioning

Companion code for the Content Frameworks article **“STP: Segmentation, Targeting, and Positioning.”**

This upgraded scaffold is designed for Catalyst Canvas integration. It includes package-style Python, JSON schemas, Canvas manifest metadata, UI-card exports, governance queue exports, tests, SQL views, synthetic data, and generated outputs.

## Run the Catalyst Canvas audit

From this article directory:

```bash
PYTHONPATH=python python3 -m stp_canvas.cli --article-root .
```

Or:

```bash
python3 python/run_stp_canvas_audit.py
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

## Generated outputs

- `outputs/tables/stp_canvas_audit.csv`
- `outputs/json/catalog.json`
- `outputs/json/canvas_cards.json`
- `outputs/json/governance_queue.json`
- `outputs/json/stp_canvas_export.json`
- `outputs/markdown/governance_queue.md`

## Purpose

The module treats STP as an auditable communication-governance framework. It evaluates segmentation logic, target-priority fit, positioning strength, ethical review risk, and governance priorities for content-framework strategy.
