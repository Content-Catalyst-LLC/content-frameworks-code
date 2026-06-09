# The Limits of Framework Thinking Canvas Module Contract

## Input

Primary input file:

`data/framework_limits_items.csv`

Required numeric fields must be normalized from 0 to 1.

## Output

The module writes:

- `outputs/tables/framework_limits_canvas_audit.csv`
- `outputs/json/catalog.json`
- `outputs/json/canvas_cards.json`
- `outputs/json/governance_queue.json`
- `outputs/json/framework_limits_canvas_export.json`
- `outputs/markdown/governance_queue.md`
- `canvas/canvas_cards.json`
- `canvas/governance_queue.json`

## CLI

```bash
PYTHONPATH=python python3 -m framework_limits_canvas.cli --article-root .
```

## Test command

```bash
PYTHONPATH=python python3 -m unittest discover -s python/tests -p "test_*.py"
```
