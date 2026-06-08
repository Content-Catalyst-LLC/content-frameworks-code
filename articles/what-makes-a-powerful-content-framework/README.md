# What Makes a Powerful Content Framework?

This companion directory supports the article **"What Makes a Powerful Content Framework?"**

The workflows operationalize framework quality as a professional content-system problem: clarity, coherence, transferability, adaptability, explanatory depth, domain fit, audience fit, evidence alignment, ethical safety, and governability.

## Core Claim

A powerful content framework organizes knowledge clearly while preserving evidence, context, limitations, ethical responsibility, and maintainability. It is not merely simple or memorable; it is fit for purpose, fit for audience, evidence-aware, and governable.

## Catalyst Canvas-Style Professional Workflow Layer

The Python and R workflows are designed as professional product scaffolds:

- configuration-driven quality rules
- framework-quality scoring
- readiness and maturity diagnostics
- evidence-alignment checks
- ethical-safety and manipulation-risk review
- governance review queues
- metadata completeness and article-map diagnostics
- internal-link and taxonomy support
- CSV, JSON, Markdown, SQL, and catalog-export outputs
- reproducible synthetic datasets

## Repository Structure

- `config/` — audit configuration and scoring rules
- `html/` — article templates, GitHub block, footer navigation, metadata blocks, and method-wrapper snippets
- `css/` — reusable styling patterns for article maps, metadata blocks, tables, cards, and editorial wrappers
- `php/` — WordPress-oriented template parts and reusable snippets
- `java/` — framework-quality model objects and validation logic
- `python/` — Catalyst Canvas-style framework-quality audit engine
- `r/` — framework maturity, risk, and quality-comparison workflows
- `sql/` — schemas and analytical queries
- `docs/` — article notes, modeling principles, implementation notes, and governance documentation
- `data/` — synthetic datasets
- `outputs/` — generated tables, reports, figures, audit logs, and catalog exports
- `notebooks/` — notebook placeholders

## Quick Start

From this article directory:

```bash
python3 python/run_all_framework_quality_workflows.py
Rscript r/run_all_framework_quality_workflows.R
javac java/FrameworkQualityModel.java && java -cp java FrameworkQualityModel
sqlite3 outputs/framework_quality.sqlite < sql/framework_quality_schema.sql
sqlite3 -header -csv outputs/framework_quality.sqlite < sql/framework_quality_queries.sql > outputs/tables/sql_framework_quality_report.csv
```
