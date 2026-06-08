# Framework Literacy and the Structure of Usable Knowledge

This companion directory supports the article **"Framework Literacy and the Structure of Usable Knowledge."**

The article defines framework literacy as the ability to understand what frameworks clarify, what they hide, what assumptions they carry, when they should be used, and when they should be adapted, combined, or rejected.

## Core Claim

Framework literacy helps people use frameworks without being used by them. It turns frameworks from mechanical templates into tools for disciplined judgment, evidence-aware communication, ethical interpretation, and sustainable knowledge architecture.

## Catalyst Canvas-Style Professional Workflow Layer

The workflows in this folder treat framework literacy as an auditable content-system capability:

- assumption-awareness scoring
- blind-spot documentation checks
- boundary clarity review
- use-condition diagnostics
- evidence-alignment checks
- ethical-safety checks
- audience-fit and domain-fit review
- adaptability and governance-readiness scoring
- internal-link diagnostics
- metadata completeness review
- taxonomy coverage summaries
- governance review queue generation
- Catalyst Canvas-style catalog exports
- reproducible CSV, JSON, Markdown, SQL, and figure outputs

## Repository Structure

- `config/` — audit configuration and scoring rules
- `html/` — GitHub block, footer navigation, method-wrapper snippets, and reusable article components
- `css/` — reusable styling patterns
- `php/` — WordPress-oriented helper snippets
- `java/` — framework-literacy model objects and validation logic
- `python/` — Catalyst Canvas-style framework-literacy audit engine
- `r/` — framework-literacy scoring, risk summaries, and domain analysis
- `sql/` — schema and analytical queries
- `docs/` — article notes, modeling principles, governance documentation, and product notes
- `data/` — synthetic datasets
- `outputs/` — generated outputs
- `notebooks/` — notebook placeholders

## Quick Start

From this article directory:

```bash
python3 python/run_all_framework_literacy_workflows.py
Rscript r/run_all_framework_literacy_workflows.R
javac java/FrameworkLiteracyModel.java && java -cp java FrameworkLiteracyModel
sqlite3 outputs/framework_literacy.sqlite < sql/framework_literacy_schema.sql
sqlite3 -header -csv outputs/framework_literacy.sqlite < sql/framework_literacy_queries.sql > outputs/tables/sql_framework_literacy_report.csv
```
