# PAS, BAB, and the Structure of Tension and Transformation

This companion directory supports the article **PAS, BAB, and the Structure of Tension and Transformation**.

The workflows model PAS and BAB as governed persuasive-sequence infrastructure: problem clarity, before-state specificity, agitation proportionality, after-state credibility, solution fit, bridge clarity, transformation-claim support, ethical-risk flags, audience agency, governance queues, and catalog exports.

## Repository Structure

- `config/` — scoring rules and PAS/BAB sequence configuration
- `html/` — article components, GitHub block, footer navigation, method wrapper
- `css/` — reusable styling patterns
- `php/` — WordPress-oriented snippets
- `java/` — PAS/BAB-readiness scoring example
- `python/` — professional PAS/BAB sequence audit workflow
- `r/` — tension balance and governance summaries
- `sql/` — schema and reporting queries
- `docs/` — article notes and governance notes
- `data/` — synthetic datasets
- `outputs/` — generated outputs
- `notebooks/` — notebook placeholders

## Quick Start

```bash
python3 python/run_all_pas_bab_sequence_workflows.py
Rscript r/run_all_pas_bab_sequence_workflows.R
javac java/PasBabSequenceAudit.java && java -cp java PasBabSequenceAudit
sqlite3 outputs/pas_bab_sequence.sqlite < sql/pas_bab_sequence_schema.sql
sqlite3 -header -csv outputs/pas_bab_sequence.sqlite < sql/pas_bab_sequence_queries.sql > outputs/tables/sql_pas_bab_sequence_report.csv
```

## Catalyst Canvas Readiness Layer

This article folder includes `canvas/`, `python/content_framework_canvas/`, tests, JSON exports, and governance queue outputs for Catalyst Canvas integration.
