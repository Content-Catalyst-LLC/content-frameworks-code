# Content Audits and Framework Governance

This companion directory supports the article **"Content Audits and Framework Governance."**

The workflows operationalize content audits and framework governance as professional editorial infrastructure: content inventories, metadata validation, article-map coverage, evidence readiness, freshness review, internal-link health, taxonomy balance, duplication signals, framework-health scoring, governance review queues, and Catalyst Canvas-style catalog exports.

## Core Claim

Content audits reveal the condition of a knowledge system. Framework governance determines how that system should be reviewed, corrected, extended, and maintained.

## Professional Workflow Layer

The Python and R workflows are designed as Catalyst Canvas-ready scaffolds:

- configuration-driven audit rules
- required metadata validation
- article-map and cluster coverage diagnostics
- planned, draft, review, published, needs-update, and archive-candidate status tracking
- evidence readiness and limitation checks
- internal-link health and orphan detection
- freshness review using content-type-specific review cycles
- taxonomy coverage and category-balance analysis
- duplication and overlap risk flags
- framework-health scoring across metadata, links, evidence, freshness, governance, and accessibility
- governance queue generation with severity, issue type, and recommended action
- CSV, JSON, Markdown, and catalog-export outputs
- non-destructive synthetic datasets for reproducible testing

## Repository Structure

- `config/` — audit configuration and scoring rules
- `html/` — article templates, GitHub blocks, footer navigation, tables, and methods wrappers
- `css/` — reusable styling patterns for article maps, metadata blocks, tables, cards, and editorial wrappers
- `php/` — WordPress-oriented template parts, footer logic, metadata rendering, and content-system helpers
- `java/` — content audit model and framework-health scoring examples
- `python/` — Catalyst Canvas-style content-audit and governance engine
- `r/` — coverage, metadata, risk, health, and governance summaries
- `sql/` — schemas for inventory, metadata, links, evidence, taxonomy, and governance status
- `docs/` — article notes, modeling principles, implementation notes, and editorial documentation
- `data/` — synthetic datasets
- `outputs/` — generated outputs
- `notebooks/` — notebook placeholders

## Quick Start

From this article directory:

```bash
python3 python/run_all_content_audit_workflows.py
Rscript r/run_all_content_audit_workflows.R
javac java/ContentAuditGovernanceModel.java && java -cp java ContentAuditGovernanceModel
sqlite3 outputs/content_audits.sqlite < sql/content_audit_schema.sql
sqlite3 -header -csv outputs/content_audits.sqlite < sql/content_audit_queries.sql > outputs/tables/sql_content_audit_report.csv
```

Outputs are written to:

```text
outputs/tables/
outputs/reports/
outputs/figures/
outputs/audit_logs/
outputs/catalog_exports/
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
