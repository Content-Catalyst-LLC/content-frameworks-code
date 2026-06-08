# Narrative Pathways and Knowledge Architecture

This companion directory supports the article **"Narrative Pathways and Knowledge Architecture."**

The article explains how readers move through complex knowledge systems over time, and how narrative pathways connect article maps, pillar pages, topic clusters, internal links, reader states, prerequisites, transitions, metadata, and governance.

## Core Claim

Narrative pathways are not decorative reading journeys. They are knowledge-architecture structures that guide movement, preserve orientation, support learning progression, reveal broken transitions, and help editors maintain coherent content systems as publications scale.

## Catalyst Canvas-Style Professional Workflow Layer

The workflows in this folder treat narrative pathways as auditable editorial infrastructure:

- pathway article inventory
- reader-state mapping
- article-role and pathway-role diagnostics
- prerequisite and next-step checks
- internal-link graph diagnostics
- transition coverage analysis
- pathway readiness scoring
- metadata completeness checks
- orientation and bridge-quality review
- governance review queue generation
- Catalyst Canvas-style catalog exports
- reproducible CSV, JSON, Markdown, SQL, Java, Python, and R outputs

## Repository Structure

- `config/` — pathway rules and governance thresholds
- `html/` — top navigation, GitHub block, footer navigation, method-wrapper snippets, and article components
- `css/` — reusable styling patterns
- `php/` — WordPress-oriented helper snippets
- `java/` — narrative pathway model and validation logic
- `python/` — Catalyst Canvas-style pathway audit engine
- `r/` — pathway coverage, transition quality, and editorial readiness analysis
- `sql/` — schema and analytical queries
- `docs/` — article notes, modeling principles, governance documentation, and product notes
- `data/` — synthetic datasets
- `outputs/` — generated outputs
- `notebooks/` — notebook placeholders

## Quick Start

From this article directory:

```bash
python3 python/run_all_narrative_pathway_workflows.py
Rscript r/run_all_narrative_pathway_workflows.R
javac java/NarrativePathwayModel.java && java -cp java NarrativePathwayModel
sqlite3 outputs/narrative_pathways.sqlite < sql/narrative_pathway_schema.sql
sqlite3 -header -csv outputs/narrative_pathways.sqlite < sql/narrative_pathway_queries.sql > outputs/tables/sql_narrative_pathway_report.csv
```

## Catalyst Canvas Readiness Layer

This article folder includes `canvas/`, `python/content_framework_canvas/`, tests, JSON exports, and governance queue outputs for Catalyst Canvas integration.
