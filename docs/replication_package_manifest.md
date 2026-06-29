# Replication Package Manifest

This repository contains the replication artifacts for the SENG 404 Group 6 final report.

GitHub repository: https://github.com/lukethomas27/group6-aidev-research-final

## Inputs

- Raw AIDev parquet files are not committed because several exceed normal GitHub file-size limits. See `DATA.md` for placement instructions.
- `RQ4/data/github_pr_metrics.csv`: GitHub REST API enrichment cache.

## Analysis Scripts

- `RQ1/scripts/*.py`: review-sentiment analysis, triangulation, and imbalance robustness checks.
- `RQ2/scripts/analysis_pipeline.py`: review engagement, coverage, scrutiny, responsiveness, and low-friction approval pipeline.
- `RQ3/scripts/run_q4_analysis.py`: within-repository acceptance, merge-speed, and specialization pipeline. The script name preserves the original teammate handoff label.
- `RQ4/scripts/analyze_aidev_experience.py`: developer-experience, task-category, imbalance, controlled logistic, and review-duration analyses.
- `RQ4/scripts/enrich_github_pr_metrics.py`: GitHub PR enrichment script.
- `RQ4/scripts/summarize_github_pr_metrics.py`: summary tables for the GitHub-enriched subset.

## Outputs

- `RQ1/results/*` and `RQ1/figures/*`: generated sentiment tables, robustness outputs, and figures.
- `RQ2/results/*`: generated review-engagement tables and figures.
- `RQ3/results/*`: generated within-repository results summary and figures.
- `RQ4/results/*`: generated model coefficients, model metadata, task summaries, robustness outputs, and figures.
- `reports/final/Project_Final_Report_ACM.pdf`: final report PDF.
- `reports/final/build_acm_final_report.py`: generator used for the final PDF version.
- `reports/final/final_report_submission.tex`: ACM-style LaTeX source.
- `reports/proposal/SENG404_Proposal_Group_6.pdf`: original project proposal artifact.
- `reports/interim/Interim_Report_Group_6.pdf`: interim report artifact.
- `Prompts.md`: AI assistance log.
