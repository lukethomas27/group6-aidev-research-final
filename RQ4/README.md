# RQ4: Developer Context

Owner: Kunwarbir Singh

RQ4 asks whether developer experience, repository relationship, PR complexity, and dataset imbalance explain apparent differences in AI-agent pull request outcomes.

## Scripts

- `scripts/analyze_aidev_experience.py`: main developer-context, model, robustness, and Q6 imbalance pipeline.
- `scripts/enrich_github_pr_metrics.py`: GitHub REST API enrichment script for PR complexity and author association.
- `scripts/summarize_github_pr_metrics.py`: summary tables for the enrichment cache.

## Results

The committed `results/` folder contains CSV, JSON, Markdown, PDF, and SVG outputs used in the final report.

## Data

`data/github_pr_metrics.csv` is included. Raw AIDev parquet files are not committed; place them in `RQ4/data/` to rerun with local caches. The main RQ4 script can fall back to Hugging Face for missing AIDev tables.
