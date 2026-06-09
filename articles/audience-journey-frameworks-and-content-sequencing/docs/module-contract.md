# Audience Journey Canvas Module Contract

## Input

Primary input file:

`data/audience_journey_stages.csv`

Required numeric fields must be normalized from 0 to 1. Link counts must be non-negative integers.

## Output

The module writes:

- `outputs/tables/audience_journey_canvas_audit.csv`
- `outputs/json/catalog.json`
- `outputs/json/canvas_cards.json`
- `outputs/json/governance_queue.json`
- `outputs/json/audience_journey_canvas_export.json`
- `outputs/markdown/governance_queue.md`
- `canvas/canvas_cards.json`
- `canvas/governance_queue.json`

## CLI

```bash
PYTHONPATH=python python3 -m audience_journey_canvas.cli --article-root .
```

## Test command

```bash
PYTHONPATH=python python3 -m unittest discover -s python/tests -p "test_*.py"
```
