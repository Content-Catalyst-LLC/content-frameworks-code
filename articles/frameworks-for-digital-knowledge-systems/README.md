# Frameworks for Digital Knowledge Systems

This companion directory supports the article **"Frameworks for Digital Knowledge Systems."**

The article explains how frameworks help digital knowledge systems organize articles, records, taxonomies, metadata, links, templates, repositories, search, accessibility, evidence, editorial workflows, and governance.

## Core Claim

A digital knowledge system is not just a website with many pages. It is an architecture for organizing, retrieving, interpreting, maintaining, and scaling knowledge. Frameworks make that architecture visible, auditable, reproducible, and governable.

## Catalyst Canvas-Style Professional Workflow Layer

The workflows in this folder treat digital knowledge systems as auditable content-system infrastructure:

- content inventory records
- taxonomy coverage diagnostics
- metadata completeness checks
- internal-link degree and relationship summaries
- repository readiness scoring
- review currency checks
- system-health scoring
- evidence and accessibility field review
- governance review queue generation
- Catalyst Canvas-style catalog exports
- reproducible CSV, JSON, Markdown, SQL, Java, Python, and R outputs

## Repository Structure

- `config/` — digital knowledge-system rules and governance thresholds
- `html/` — top navigation, GitHub block, footer navigation, method-wrapper snippets, and article components
- `css/` — reusable styling patterns
- `php/` — WordPress-oriented helper snippets
- `java/` — digital knowledge-system model and validation logic
- `python/` — Catalyst Canvas-style digital knowledge-system audit engine
- `r/` — coverage analysis, metadata readiness, repository readiness, and system-health reporting
- `sql/` — schema and analytical queries
- `docs/` — article notes, modeling principles, governance documentation, and product notes
- `data/` — synthetic datasets
- `outputs/` — generated outputs
- `notebooks/` — notebook placeholders

## Quick Start

From this article directory:

```bash
python3 python/run_all_digital_knowledge_system_workflows.py
Rscript r/run_all_digital_knowledge_system_workflows.R
javac java/DigitalKnowledgeSystemModel.java && java -cp java DigitalKnowledgeSystemModel
sqlite3 outputs/digital_knowledge_system.sqlite < sql/digital_knowledge_system_schema.sql
sqlite3 -header -csv outputs/digital_knowledge_system.sqlite < sql/digital_knowledge_system_queries.sql > outputs/tables/sql_digital_knowledge_system_report.csv
```

## Catalyst Canvas Readiness Layer

This article folder includes `canvas/`, `python/content_framework_canvas/`, tests, JSON exports, and governance queue outputs for Catalyst Canvas integration.
