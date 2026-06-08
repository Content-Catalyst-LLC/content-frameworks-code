# Frameworks, Templates, and Models

This companion directory supports the article **"Frameworks, Templates, and Models."**

The article distinguishes frameworks, templates, models, methods, and workflows as different kinds of structures used in professional content systems.

## Core Claim

Frameworks organize reasoning, templates standardize outputs, models represent relationships, methods define procedures, and workflows coordinate work across time. Content systems become weaker when these structures are confused.

## Catalyst Canvas-Style Professional Workflow Layer

The workflows in this folder treat structural clarity as an auditable product capability:

- declared-vs-observed structure classification
- framework/template/model/method/workflow signal scoring
- structural misuse detection
- template-overreach checks
- model-assumption review
- framework-fit diagnostics
- governance completion scoring
- metadata completeness review
- internal-link diagnostics
- taxonomy coverage analysis
- governance review queue generation
- Catalyst Canvas-style catalog exports
- reproducible CSV, JSON, Markdown, SQL, Java, Python, and R outputs

## Repository Structure

- `config/` — classification rules and governance thresholds
- `html/` — GitHub block, footer navigation, method-wrapper snippets, and article components
- `css/` — reusable styling patterns
- `php/` — WordPress-oriented helper snippets
- `java/` — structure-type model and validation logic
- `python/` — Catalyst Canvas-style structure classification engine
- `r/` — structure-type analysis, risk summaries, and governance summaries
- `sql/` — schema and analytical queries
- `docs/` — article notes, modeling principles, governance documentation, and product notes
- `data/` — synthetic datasets
- `outputs/` — generated outputs
- `notebooks/` — notebook placeholders

## Quick Start

From this article directory:

```bash
python3 python/run_all_structure_workflows.py
Rscript r/run_all_structure_workflows.R
javac java/StructureTypeModel.java && java -cp java StructureTypeModel
sqlite3 outputs/structure_classification.sqlite < sql/structure_classification_schema.sql
sqlite3 -header -csv outputs/structure_classification.sqlite < sql/structure_classification_queries.sql > outputs/tables/sql_structure_classification_report.csv
```
