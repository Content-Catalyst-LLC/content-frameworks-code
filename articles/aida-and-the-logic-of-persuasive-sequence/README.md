# AIDA and the Logic of Persuasive Sequence

This companion directory supports the article **AIDA and the Logic of Persuasive Sequence**.

The workflows model AIDA as persuasive-sequence infrastructure: attention clarity, interest development, desire support, call-to-action transparency, stage balance, ethical-risk flags, audience readiness, governance queues, and catalog exports.

## Repository Structure

- `config/` — scoring rules and AIDA sequence configuration
- `html/` — article components, GitHub block, footer navigation, method wrapper
- `css/` — reusable styling patterns
- `php/` — WordPress-oriented snippets
- `java/` — AIDA-readiness scoring example
- `python/` — professional AIDA sequence audit workflow
- `r/` — stage balance and governance summaries
- `sql/` — schema and reporting queries
- `docs/` — article notes and governance notes
- `data/` — synthetic datasets
- `outputs/` — generated outputs
- `notebooks/` — notebook placeholders

## Quick Start

```bash
python3 python/run_all_aida_sequence_workflows.py
Rscript r/run_all_aida_sequence_workflows.R
javac java/AidaSequenceAudit.java && java -cp java AidaSequenceAudit
sqlite3 outputs/aida_sequence.sqlite < sql/aida_sequence_schema.sql
sqlite3 -header -csv outputs/aida_sequence.sqlite < sql/aida_sequence_queries.sql > outputs/tables/sql_aida_sequence_report.csv
```

## Catalyst Canvas Readiness Layer

This article folder includes `canvas/`, `python/content_framework_canvas/`, tests, JSON exports, and governance queue outputs for Catalyst Canvas integration.
