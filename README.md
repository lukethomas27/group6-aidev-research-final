# SENG 404 Group 6 Research Repository

This repository contains the replication package for Group 6's SENG 404 final project on AI coding agents and pull request outcomes in the AIDev dataset.

GitHub repository: https://github.com/lukethomas27/group6-aidev-research-final

## Research Questions

| Folder | Owner | Focus |
|---|---|---|
| `RQ1/` | Amrinder Singh | Review sentiment across AI-authored pull requests. |
| `RQ2/` | Gabriel Taves | Review engagement, coverage, scrutiny, responsiveness, and low-friction approval. |
| `RQ3/` | Luke Thomas | Within-repository acceptance, merge speed, and specialization comparisons. |
| `RQ4/` | Kunwarbir Singh | Developer experience, PR complexity, author association, and imbalance checks. |

## Repository Layout

- `RQ1/` through `RQ4/`: scripts, generated results, figures, and supporting reports for each research question.
- `reports/final/`: final report PDF, PDF generator, supporting Markdown summary, and ACM LaTeX source.
- `reports/proposal/`: original project proposal artifact.
- `reports/interim/`: interim report artifact.
- `docs/`: replication-package and rubric notes.
- `Prompts.md`: AI assistance log used for report synthesis and checks.
- `CONTRIBUTIONS.md`: team ownership and attribution notes.
- `DATA.md`: dataset and cache instructions.

## Reproducing Analyses

Create an environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

The raw AIDev parquet caches are not committed because several files exceed normal GitHub size limits. See `DATA.md` for where to place local data files.

Most scripts can be run directly from the repository root:

```powershell
python RQ1/scripts/analyze_aidev_sentiment.py
python RQ2/scripts/analysis_pipeline.py
python RQ3/scripts/run_q4_analysis.py
python RQ4/scripts/analyze_aidev_experience.py
```

Some RQ1 scripts depend on `RQ1/results/filtered_sentiment_items.parquet`, which is produced by `RQ1/scripts/analyze_aidev_sentiment.py`.

## Final Report

The final report is available at `reports/final/Project_Final_Report_ACM.pdf`. The editable LaTeX source is in `reports/final/final_report_submission.tex`.
