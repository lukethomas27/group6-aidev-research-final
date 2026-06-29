# Final Report Rubric Checklist

Generated as a final pre-submission audit against the provided SENG 404 rubric.

## Content

- Results and discussion depth: Covered. The report synthesizes RQ1 sentiment, RQ2 review engagement, RQ3 within-repository outcomes, RQ4 developer context, and Q6 imbalance into one argument about context-driven trust rather than agent leaderboards.
- Evidence of analysis competence: Covered. Methods include sentiment triangulation, coverage/scrutiny metrics, fixed-effects logit, Cox merge-speed models, GitHub enrichment, repository-clustered controls, and imbalance sensitivity checks.
- Ambition and related work: Covered. The report situates the work in pull-request mining, contribution evaluation, SE sentiment analysis, and AIDev. It includes 19 references.
- Software engineering: Covered. The report includes a reproducibility section, scripts, cached data, generated outputs, figures, and `Prompts.md`.
- Course concepts: Covered. The discussion explicitly addresses mining GitHub, sampling assumptions, observational validity, construct validity, and social/technical confounding.

## Presentation and Technical Writing

- Professional writing: Covered. The final report has coherent sections, clear terms, spell-checked prose, and no unfinished markers.
- Technical organization: Covered in structure and captions. The generated PDF is a readable 8-page main report plus appendices. The ReportLab generator used for the submitted PDF is stored in `reports/final/build_acm_final_report.py`; the editable LaTeX source is also included for ACM-style reference.
- Figures/tables: Covered. The report includes simple figures for review coverage, scrutiny, controlled merge effects, and dataset imbalance, with meaningful captions.

## Final Manual Checks Before Brightspace

- Push the current local changes to https://github.com/lukethomas27/group6-aidev-research-final and submit that URL with the Brightspace PDF.
- If exact ACM visual formatting is required, compile `final_report_submission.tex` on a machine with LaTeX/acmart installed. The submitted PDF in `reports/final/Project_Final_Report_ACM.pdf` is the generated final report version.
- Confirm `docs/replication_package_manifest.md`, `Prompts.md`, the scripts, and the generated outputs are visible in the pushed GitHub repository so the Software Engineering rubric item is fully satisfied.
- Have each teammate skim their contribution paragraph and confirm the team contribution table.
