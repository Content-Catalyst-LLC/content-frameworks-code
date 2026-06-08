# Catalyst Canvas Integration Notes

This article folder includes a Canvas-ready STP module.

## What is included

- `canvas/canvas_manifest.json`
- `canvas/input_schema.json`
- `canvas/output_schema.json`
- generated `canvas/canvas_cards.json`
- generated `canvas/governance_queue.json`
- package-style Python under `python/stp_canvas/`
- unit tests under `python/tests/`
- JSON, CSV, and markdown exports under `outputs/`
- SQL schema and views for Canvas-style relational storage

## Run the module

From the article directory:

```bash
PYTHONPATH=python python3 -m stp_canvas.cli --article-root .
```

Or:

```bash
python3 python/run_stp_canvas_audit.py
```

## Canvas rendering contract

Catalyst Canvas can consume:

- `canvas/canvas_manifest.json` for module metadata
- `canvas/input_schema.json` for expected input shape
- `canvas/output_schema.json` for output expectations
- `canvas/canvas_cards.json` for UI cards
- `canvas/governance_queue.json` for review workflow
- `outputs/json/stp_canvas_export.json` for the complete audit payload
