# RQ2 — AI Assistance Log (Gabriel Taves)

This file documents the AI-assisted prompts and tasks used to finalize the RQ2 (Review Engagement) section of the final report and poster. All statistical results, model decisions, and interpretations are Gabe's own; AI was used to help structure, write, and refine prose, and to help prepare presentation materials.

---

## Understanding the Interim State and Remaining Work

The interim report flagged two main remaining items for RQ2: (1) the write-up needed to more comprehensively describe and justify the statistical methodology, and (2) RQ2 needed a stronger connection to RQ3's merge-speed findings — specifically, testing whether lower scrutiny predicts faster merge after controls.

- Asked Claude to read the full interim report and summarize the scope and completion status of RQ2, and identify what was flagged as remaining.
- Asked Claude to read the RQ2 draft (`rq2_section.md`) and `gabe_report_outline.md` alongside the final report submission instructions (ACM format, 8–12 pages) to understand what a finalized version of the section needed to look like.

---

## Writing the Final Report Section

The interim RQ2 write-up had all the numbers but lacked sufficient justification of model choices and the two-stage framework structure. The main task was producing a clean, well-justified write-up suitable for the final paper.

- Asked Claude to draft the full RQ2 section in Markdown from scratch, structured for integration into the shared ACM-format paper. Sections produced: dataset and preprocessing decisions, Review Engagement Framework (two-stage structure with construct definitions), statistical models table with justifications, results for all five constructs, discussion, and limitations.
- Iteratively refined the methods section to more explicitly justify model choices — particularly why a Weibull AFT survival model was used for responsiveness (rather than Cox), why negative binomial was chosen for comment count outcomes, and why the Stage 2 constructs are conditioned on reviewed PRs rather than applied to the full dataset.
- Asked Claude to strengthen the RQ2–RQ3 connection in the discussion section, specifically framing the low-friction approval null result as evidence that merge rate differences (RQ3) are likely driven by the coverage gate rather than by differential evaluation of reviewed PRs.
- Asked Claude to clarify and plain-language several passages that were flagged as unclear, including what "after controls" means operationally and what the Stage 2 conditioning implies for interpretation.
- Output saved to `final_report_rq2.md`.

---

## Poster (RQ2 Section)

The group produced a shared poster draft using AI tools. Upon reviewing it, the RQ2 section (Finding 2) was found to significantly underrepresent the actual findings — the 48× responsiveness result, all model odds ratios and time ratios, the low-friction approval null result, and the task type effects were all absent. The raw low-friction approval rates were presented without noting the null model result, which was actively misleading.

- Asked Claude to assess the group poster PDF for how well it covered RQ2 findings.
- Asked Claude to comprehensively inventory all RQ2 findings before writing any poster text — going construct-by-construct and flagging what was missing, understated, or misrepresented.
- Asked Claude to draft a full poster section for RQ2 without cutting any critical findings, then iteratively condense to approximately two printed pages while preserving all model results, caveats, and the interpretive null result.
- Output saved to `poster_rq2_concise.md`.

---

## Poster Extension Sheet

Because the group poster was assembled from individual printed pages, additional pages could be added alongside the existing poster without looking out of place. A one-page extension sheet was prepared covering the model results that the main poster omitted.

- Asked Claude to write a concise extension page covering: scrutiny odds ratios by agent and task type, PR complexity as the strongest predictor, the agent × repository interaction, the responsiveness table with time ratios and the 48× Copilot result, task type effects on responsiveness, and the low-friction approval null result with plain-language explanation.
- Iteratively refined to ensure every technical term was explained inline (what a confidence interval means, what a time ratio means, what "after controls" actually controlled for) so the sheet could be read without additional context.
- Output saved to `RQ2/finding2_extended.md`.

---

## Technical Reference Notes

- Asked Claude to write a plain-language technical reference covering: the data source and key preprocessing decisions (human review filter, task type labels), the two-stage Review Engagement Framework, each statistical model and why it was chosen, the shared covariate set and why each control was included, and key design decisions likely to come up as questions during presentation.
- Refined to remove jargon and make the notes readable at a glance for presenting at the poster session.
- Output saved to `RQ2/rq2_technical_notes.md`.

---

## Human Oversight Applied

- All statistical results (ORs, TRs, CIs, p-values, concordance) verified against the original analysis outputs in `interim report/output/`.
- Model descriptions and covariate sets verified against `gabe_report_outline.md` Section 3.3.
- The RQ2–RQ3 connection framing verified against the interim report's Section 1.5 (Coordination Note) and Section 5.2 (Coverage Reframes the Codex Story).
- Figure recommendations for the poster (engagement profile stacked bar, KM curves) selected based on figures confirmed to exist in `interim report/output/`.
- All AI-drafted prose was reviewed and edited by Gabe before use.
