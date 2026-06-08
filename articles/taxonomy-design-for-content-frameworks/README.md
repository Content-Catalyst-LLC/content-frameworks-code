# Taxonomy Design for Content Frameworks

This companion directory supports the article **"Taxonomy Design for Content Frameworks."**

The article explains how categories, tags, hierarchies, facets, semantic relationships, conceptual boundaries, metadata fields, and governance rules shape the usability of content frameworks and digital knowledge systems.

## Core Claim

A taxonomy is not just a tag list. It is a conceptual structure that determines how content belongs, how readers discover relationships, how editors plan coverage, and how the system can grow without losing clarity.

## Catalyst Canvas-Style Professional Workflow Layer

The workflows in this folder treat taxonomy design as auditable editorial infrastructure:

- article inventory records
- taxonomy category records
- primary and secondary assignment audits
- category coverage and balance analysis
- taxonomy metadata readiness checks
- tag-sprawl diagnostics
- category boundary review support
- taxonomy relationship summaries
- governance review queue generation
- Catalyst Canvas-style catalog exports
- reproducible CSV, JSON, Markdown, SQL, Java, Python, and R outputs

## Repository Structure

- `config/` — taxonomy rules and governance thresholds
- `html/` — top navigation, GitHub block, footer navigation, method-wrapper snippets, and article components
- `css/` — reusable styling patterns
- `php/` — WordPress-oriented helper snippets
- `java/` — taxonomy model and validation logic
- `python/` — Catalyst Canvas-style taxonomy audit engine
- `r/` — taxonomy coverage, category balance, metadata readiness, and editorial readiness analysis
- `sql/` — schema and analytical queries
- `docs/` — article notes, modeling principles, governance documentation, and product notes
- `data/` — synthetic datasets
- `outputs/` — generated outputs
- `notebooks/` — notebook placeholders

## Quick Start

From this article directory:

```bash
python3 python/run_all_taxonomy_design_workflows.py
Rscript r/run_all_taxonomy_design_workflows.R
javac java/TaxonomyDesignModel.java && java -cp java TaxonomyDesignModel
sqlite3 outputs/taxonomy_design.sqlite < sql/taxonomy_design_schema.sql
sqlite3 -header -csv outputs/taxonomy_design.sqlite < sql/taxonomy_design_queries.sql > outputs/tables/sql_taxonomy_design_report.csv
```
