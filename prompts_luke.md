# AI-Assistance Prompts — Luke Thomas (RQ4)

This file documents the prompts I used with an AI coding assistant (Claude Code) while
producing my contribution to the Group 6 project: **RQ4 — within-repo agent comparison and
specialization** on the AIDev dataset. It covers only my own deliverables. Each entry
describes the intent of the prompt and the file(s) it produced or modified; the assistant
worked against a written task brief (`CLAUDE.md` in this folder) that set the design,
data source, checkpoint, and guardrails.

---

## 1. Make the RQ4 notebook actually run against real data
**Produced/modified:** `SENG404_Q4_starter.ipynb` (executed, outputs preserved)

> I have a scaffold notebook (`SENG404_Q4_starter.ipynb`) for RQ4 with the join logic, a
> feasibility gate, and model stubs, but it has never been run against real data. Pull the
> needed tables from the `hao-li/AIDev` depth/curated set into `./aidev/`, then execute the
> notebook top to bottom and fix whatever breaks so it runs with zero errors and keeps its
> outputs. Don't fabricate any numbers — if a table, column, or join is missing, stop and
> tell me.

## 2. Verify the data before trusting any result
**Produced/modified:** `SENG404_Q4_starter.ipynb` (agent-normalization + join cells), `data_notes.md`

> Before running the analysis, verify the things most likely to be silently wrong: print the
> unique raw `agent` values and confirm all five agents normalize correctly; check that the
> `pr_id` join keys actually match `pull_request.id` on a sample; and confirm the timestamp
> columns parse as datetimes. Fix the agent-name mapping if it's broken and write up every
> schema mismatch, bug, and fix in a short `data_notes.md`.

## 3. Run the feasibility checkpoint at k=5 and k=10
**Produced/modified:** `checkpoint_feasibility.py`

> Run only the feasibility gate (Sections 0–3) at both k=5 and k=10 and report how many repos
> qualify, how many PRs they cover, and which agents are present — this decides whether RQ4 is
> even viable. Put it in a standalone script I can re-run. If very few repos qualify even at
> k=5, flag it and propose relaxing the design rather than pushing on.

## 4. Run the full pipeline co-primary at both thresholds
**Produced/modified:** `run_q4_analysis.py`, `figures/*.png`, `results.md`

> Now run the full analysis co-primary at k=5 and k=10: within-repo-centered acceptance by
> agent, raw vs task+size-adjusted acceptance effects (report the gap explicitly), a
> repo-stratified Cox model for merge speed that keeps open PRs as right-censored,
> task-specialization JSD, and within-repo size effects. Give me a headless `run_q4_analysis.py`
> that reproduces the whole pipeline and regenerates the figures, and write the findings up in
> `results.md` as prose, not raw dumps. Report per-(repo, agent) N and flag anywhere Codex's
> overrepresentation could be driving a result.

## 5. Generate the RQ4 figures
**Produced/modified:** `figures/acceptance_centered_k5.png`, `figures/acceptance_centered_k10.png`,
`figures/task_mix_k5.png`, `figures/task_mix_k10.png`, `figures/loc_box_k5.png`, `figures/loc_box_k10.png`

> Save the supporting figures as PNGs at both thresholds: within-repo-centered acceptance by
> agent, a stacked task-type mix by agent for the top qualifying repos, and boxplots of log LOC
> by agent.

## 6. Write the RQ4 report section
**Produced/modified:** `luke_thomas_Q4_section.md`, `luke_research_Q4.md` (and `.docx` export)

> Turn the RQ4 results into a written report section authored under my name. Frame it as the
> within-repository comparison part of the team's broader analysis (so it slots in alongside
> the other RQs), state the research question and design, present the feasibility counts and
> each result with its caveats, and be explicit about the raw-vs-adjusted acceptance gap and
> the Codex-imbalance limitation. Keep every number consistent with the executed notebook.

## 7. Build the poster panel for the RQ4 contribution
**Produced/modified:** `luke_q4_poster_panel.html`, `luke_q4_poster_panel.pdf`

> Build a standalone poster panel for my RQ4 contribution for the poster session — a
> self-contained HTML page (printable to PDF) with the question, the within-repo design, the
> key figures, and the headline findings, sized to drop into the group poster. Don't invent
> any numbers; pull them from `results.md` and the figures.

---

*Note on use:* the assistant generated and ran code and drafted prose; I reviewed the data
verification, the threshold/feasibility decision, and every reported number against the
executed notebook before including anything in the submission.
