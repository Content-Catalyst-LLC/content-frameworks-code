# STP: Segmentation, Targeting, and Positioning

Companion code for the Content Frameworks article **“STP: Segmentation, Targeting, and Positioning.”**

This scaffold supports audience-strategy analysis across segmentation logic, target-priority scoring, positioning strength, evidence fit, ethical review flags, and content-framework governance.

## Repository structure

- `python/` — STP scoring, positioning-gap checks, and audit workflows
- `r/` — segment-fit reporting, target-priority summaries, and plots
- `sql/` — schema and sample queries for STP audit tables
- `data/` — synthetic segment and positioning dataset
- `outputs/` — generated tables and figures
- `docs/` — method notes and editorial governance notes
- `notebooks/` — notebook placeholders
- `julia/`, `rust/`, `go/`, `c/`, `cpp/`, `fortran/` — portable workflow stubs

## Run the core workflows

From this article directory:

```bash
python3 python/stp_audience_positioning_audit.py
Rscript r/stp_segment_positioning_report.R
```

The scripts write generated outputs to `outputs/tables/` and `outputs/figures/`.

## Conceptual model

STP connects three communication decisions:

1. **Segmentation** — which audience differences matter?
2. **Targeting** — which audiences should receive priority?
3. **Positioning** — how should the offer, article, framework, or institution be understood by the target audience?

The companion workflows treat STP as an auditable content-framework practice rather than a static marketing label.
