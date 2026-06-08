# Evidence Architecture in Explanatory Content

This companion directory supports the article **Evidence Architecture in Explanatory Content**.

The workflows model evidence architecture as a governed explanatory system: claim inventories, claim-to-source support, evidence type classification, source authority, uncertainty and limitation visibility, visual evidence support, review readiness, governance queues, and catalog exports.

## Repository Structure

- `config/` — scoring rules and evidence architecture configuration
- `html/` — article components, GitHub block, footer navigation, method wrapper
- `css/` — reusable styling patterns
- `php/` — WordPress-oriented snippets
- `java/` — evidence-readiness scoring example
- `python/` — professional evidence architecture audit workflow
- `r/` — claim support and governance summaries
- `sql/` — schema and reporting queries
- `docs/` — article notes and governance notes
- `data/` — synthetic datasets
- `outputs/` — generated outputs
- `notebooks/` — notebook placeholders

## Quick Start

```bash
python3 python/run_all_evidence_architecture_workflows.py
Rscript r/run_all_evidence_architecture_workflows.R
javac java/EvidenceArchitectureAudit.java && java -cp java EvidenceArchitectureAudit
sqlite3 outputs/evidence_architecture.sqlite < sql/evidence_architecture_schema.sql
sqlite3 -header -csv outputs/evidence_architecture.sqlite < sql/evidence_architecture_queries.sql > outputs/tables/sql_evidence_architecture_report.csv
```
