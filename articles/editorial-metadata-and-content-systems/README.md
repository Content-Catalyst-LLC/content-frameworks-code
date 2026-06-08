# Editorial Metadata and Content Systems

This companion directory supports the article **"Editorial Metadata and Content Systems."**

The workflows operationalize editorial metadata as content-system infrastructure: article records, schema validation, controlled vocabularies, article-map sequence checks, footer-navigation validation, repository alignment, image metadata, accessibility metadata, evidence records, freshness review, governance queues, and catalog exports.

## Core Claim

Editorial metadata turns articles into managed knowledge objects. It lets a content framework be found, understood, linked, audited, reused, maintained, and governed over time.

## Professional Workflow Layer

The Python and R workflows are designed as product-grade editorial-system scaffolds:

- required metadata validation
- controlled vocabulary checks
- article-map order and footer-navigation validation
- slug, URL, and repository-path alignment
- image metadata readiness
- accessibility metadata readiness
- evidence and reference metadata checks
- review-cycle and freshness reporting
- relationship completeness scoring
- governance queue generation
- catalog exports
- CSV, JSON, Markdown, and figure outputs
- non-destructive synthetic datasets for reproducible testing

## Repository Structure

- `config/` — metadata schema configuration and governance rules
- `html/` — article templates, GitHub blocks, footer navigation, tables, and methods wrappers
- `css/` — reusable styling patterns for article maps, metadata blocks, tables, cards, and editorial wrappers
- `php/` — WordPress-oriented template parts, footer logic, metadata rendering, and content-system helpers
- `java/` — metadata record and validation model examples
- `python/` — metadata validation and content-system audit engine
- `r/` — metadata readiness, cluster coverage, and governance summaries
- `sql/` — schemas for metadata records, article maps, image records, references, repositories, and review status
- `docs/` — article notes, modeling principles, implementation notes, and editorial documentation
- `data/` — synthetic datasets
- `outputs/` — generated outputs
- `notebooks/` — notebook placeholders

## Quick Start

From this article directory:

```bash
python3 python/run_all_metadata_workflows.py
Rscript r/run_all_metadata_workflows.R
javac java/EditorialMetadataModel.java && java -cp java EditorialMetadataModel
sqlite3 outputs/editorial_metadata.sqlite < sql/editorial_metadata_schema.sql
sqlite3 -header -csv outputs/editorial_metadata.sqlite < sql/editorial_metadata_queries.sql > outputs/tables/sql_editorial_metadata_report.csv
```

Outputs are written to:

```text
outputs/tables/
outputs/reports/
outputs/figures/
outputs/audit_logs/
outputs/catalog_exports/
```
