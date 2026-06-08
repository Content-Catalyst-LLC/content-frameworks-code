# Content Frameworks Canvas Module Contract

Input: `data/article_canvas_inputs.csv`

Command:

```bash
PYTHONPATH=python python3 -m content_framework_canvas.cli --article-root .
```

Tests:

```bash
PYTHONPATH=python python3 -m unittest discover -s python/tests -p "test_*.py"
```
