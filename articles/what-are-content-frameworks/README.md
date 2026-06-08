# What Are Content Frameworks?

This companion directory supports the article **"What Are Content Frameworks?"**

The article defines content frameworks as structured models for organizing, explaining, sequencing, and scaling complex ideas. The companion materials model article maps, metadata systems, taxonomy categories, framework libraries, internal-link relationships, content-audit logic, governance records, and reusable publishing components.

## Core Claim

Content frameworks give knowledge a usable form by defining purpose, audience, scope, categories, sequence, relationships, evidence, examples, limitations, and governance.

## Repository Structure

- `html/` — article templates, pillar-page layouts, metadata blocks, navigation patterns, cards, tables, and reusable content components
- `css/` — reusable styling patterns for content frameworks, article maps, metadata blocks, tables, cards, and editorial wrappers
- `php/` — WordPress-oriented template parts, reusable snippets, article-footer logic, metadata rendering, and content-system helpers
- `java/` — content models, metadata-schema objects, article-map validators, framework classifiers, and editorial workflow logic
- `python/` — pillar maps, internal-link graphs, metadata audits, article-cluster examples, and framework classification workflows
- `r/` — framework-library comparison, content-audit summaries, editorial coverage analysis, and taxonomy summaries
- `sql/` — schemas for pillars, articles, clusters, frameworks, templates, links, references, and editorial status
- `docs/` — article notes, modeling principles, implementation notes, and editorial documentation
- `data/` — synthetic datasets
- `outputs/` — generated outputs
- `notebooks/` — notebook placeholders

## Quick Start

```bash
python3 python/run_all_content_framework_workflows.py
Rscript r/run_all_content_framework_workflows.R
javac java/ContentFrameworkModel.java && java -cp java ContentFrameworkModel
sqlite3 outputs/content_frameworks.sqlite < sql/content_frameworks_schema.sql
sqlite3 -header -csv outputs/content_frameworks.sqlite < sql/content_frameworks_queries.sql > outputs/tables/sql_content_framework_report.csv
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
