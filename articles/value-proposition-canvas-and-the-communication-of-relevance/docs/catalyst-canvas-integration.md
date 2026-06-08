# Catalyst Canvas Integration Notes

This article folder has been upgraded with a generic Content Frameworks Catalyst Canvas readiness layer.

## Article

- Title: Value Proposition Canvas and the Communication of Relevance
- Slug: value-proposition-canvas-and-the-communication-of-relevance
- Module kind: audience_relevance

## Canvas files

- `canvas/canvas_manifest.json`
- `canvas/input_schema.json`
- `canvas/output_schema.json`
- `canvas/canvas_cards.json`
- `canvas/governance_queue.json`

## Python package

- `python/content_framework_canvas/`
- `python/tests/`
- `python/run_canvas_audit.py`

## Run

From this article directory:

```bash
PYTHONPATH=python python3 -m content_framework_canvas.cli --article-root .
```

Or:

```bash
python3 python/run_canvas_audit.py
```

## Outputs

- `outputs/tables/article_canvas_audit.csv`
- `outputs/json/catalog.json`
- `outputs/json/canvas_cards.json`
- `outputs/json/governance_queue.json`
- `outputs/json/article_canvas_export.json`
- `outputs/markdown/governance_queue.md`

## Purpose

The Canvas layer evaluates content value, audience value, evidence strength, repository support, governance pressure, and ethical risk so the article can be surfaced inside Catalyst Canvas as an auditable knowledge object.
