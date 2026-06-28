# Final Report Rubric Checklist

Generated as a final pre-submission audit against the provided SENG 404 rubric.

## Content

- Results and discussion depth: Covered. The report synthesizes RQ1 sentiment, RQ2 review engagement, RQ3 within-repository outcomes, RQ4 developer context, and Q6 imbalance into one argument about context-driven trust rather than agent leaderboards.
- Evidence of analysis competence: Covered. Methods include sentiment triangulation, coverage/scrutiny metrics, fixed-effects logit, Cox merge-speed models, GitHub enrichment, repository-clustered controls, and imbalance sensitivity checks.
- Ambition and related work: Covered. The report situates the work in pull-request mining, contribution evaluation, SE sentiment analysis, and AIDev. It includes 10 references.
- Software engineering: Covered. The report includes a reproducibility section, scripts, cached data, generated outputs, figures, and `Prompts.md`.
- Course concepts: Covered. The discussion explicitly addresses mining GitHub, sampling assumptions, observational validity, construct validity, and social/technical confounding.

## Presentation and Technical Writing

- Professional writing: Needs human read-through for final team voice, but the generated report has coherent sections, clear terms, spell-checked prose, and no placeholder TODOs except the repository URL note in Appendix A.
- Technical organization: Covered in structure and captions. The generated PDF is a readable 8-page main report plus appendices. The editable LaTeX source uses `\documentclass[sigconf,nonacm]{acmart}` for ACM-style compilation.
- Figures/tables: Covered. The report includes simple figures for review coverage, scrutiny, controlled merge effects, and dataset imbalance, with meaningful captions.

## Final Manual Checks Before Brightspace

- Add the final GitHub or course repository URL in Appendix A after pushing this local repository.
- If exact ACM visual formatting is required, compile `final_report_submission.tex` on a machine with LaTeX/acmart installed. This workspace does not have a LaTeX engine, so the generated PDF is a submission-ready readable PDF draft and the `.tex` file is the ACM-template source.
- Confirm `docs/replication_package_manifest.md`, `Prompts.md`, the scripts, and the generated outputs are visible in the pushed GitHub repository so the Software Engineering rubric item is fully satisfied.
- Have each teammate skim their contribution paragraph and confirm the team contribution table.
