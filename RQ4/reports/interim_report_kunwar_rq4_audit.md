# Interim report audit: Kunwar / RQ4-Q5

Source read: `interim_report_draft_formatted (1).pdf`
Extracted text used: `interim_report_draft_formatted_extracted.txt`

## Main issue

The draft assigns Kunwar to `RQ4`, but our local section is currently written as `Q5: Developer Experience, PR Complexity, and Agent-Assisted PR Outcomes` in `kunwar_research_Q5.pdf` and `final_report.md`.

This is probably just numbering drift from the proposal. The content fits the interim report's RQ4 wording, but the team should standardize the label before submission:

- Option A: rename our local section from `Q5` to `RQ4`.
- Option B: keep it as `Q5` and update the interim report's research-question table/timeline to show Kunwar as Q5.

Given the current interim draft already uses `RQ4` throughout, the simplest fix is to relabel Kunwar's section as `RQ4` while preserving our research content.

## Spots in the draft

### Page 1

- Team line includes `Kunwarbir Singh`; no issue.

### Page 2

- Research question table:
  - Current: `RQ4 Do more experienced developers / maintainers treat AI contributions differently, and how robust are all findings to dataset imbalance... Kunwar [SKELETON]`
  - Action: replace `[SKELETON]` with `[IN PROGRESS]` or `[ANALYSIS DRAFT COMPLETE]`.
  - Suggested wording:
    - `RQ4: To what extent does developer experience influence agent-assisted pull request outcomes after accounting for agent choice, task type, PR complexity, repository context, and author association?`

### Page 3

- TODO ownership note:
  - Current: `[TODO: confirm ownership of RQ4 - proposal left Q5 (developer experience) and Q6 (imbalance) unassigned; we have provisionally given both to Kunwar.]`
  - Action: remove this TODO once the team accepts the numbering.
  - Suggested replacement:
    - `Coordination note: the developer-experience and imbalance-robustness analyses have been consolidated under Kunwar's RQ4 section.`

### Page 4

- Related work line:
  - Current: `Background for RQ1 and RQ4.`
  - Action: keep if we standardize on RQ4; otherwise change to Q5/RQ5.

- Dataset section:
  - Current: says all current analyses use `AIDev-pop` and Codex imbalance is addressed per-section and in RQ4.
  - Action: keep, but add one sentence that Kunwar's current GitHub enrichment is a subset.
  - Suggested addition:
    - `For Kunwar's current complexity and author-association controls, we enriched a 2,025-PR sample through the GitHub API, with 2,003 successful fetches; the final phase will expand this enrichment to the largest feasible AIDev-pop coverage under GitHub API limits and public-repository availability.`

### Page 5

- Methods placeholder:
  - Current: `RQ4 - Experience & imbalance robustness (Kunwar) [SKELETON]... [TODO @Kunwar: specify experience proxies...]`
  - Action: replace placeholder with actual method summary.
  - Suggested replacement:
    - `RQ4 - Developer experience, PR complexity, and robustness (Kunwar) [ANALYSIS DRAFT COMPLETE]. Experience is proxied by GitHub account age at PR creation, with followers as a secondary reputation proxy. Current models control for agent, task category, PR month, high-volume author-repo pairs, and repository-clustered standard errors. A GitHub-enriched subset adds total churn, changed files, commits, and author association. Remaining work will scale GitHub enrichment beyond the current subset and test whether results hold across broader repository coverage.`

### Page 6

- Luke section:
  - Current: `4.2 RQ3 ... Full write-up: luke_research_Q4.md`
  - Action: not Kunwar, but the `Q4` filename could confuse the report numbering. Consider renaming/linking as `luke_research_RQ3` or adding a note that this is Luke's file name, not Kunwar's RQ4.

### Page 7

- Kunwar findings placeholder:
  - Current: `4.4 RQ4 - Developer experience & dataset-imbalance robustness (Kunwar) [SKELETON - @Kunwar]`
  - Action: replace with the actual result summary.
  - Suggested compact section text:
    - `Developer experience does not appear to be a robust independent predictor once PR complexity and repository/social context are included. In the GitHub-enriched, human-account-linked, non-extreme sample, account age is not significant for human review, approval, discussion, merge success, or review duration. PR complexity and repository relationship matter more: larger churn lowers merge odds, more commits increase review/discussion activity, OWNER authors have higher merge odds, and authors with no GitHub association to the repository have much lower merge odds and longer review times. Agent effects weaken after these controls; Claude Code and Cursor do not show stable merge advantages over OpenAI Codex in the enriched model.`

- Discussion note:
  - Current: `[PARTIAL - to extend once RQ2/RQ4 land]`
  - Action: change to `once RQ4 final enrichment lands` or similar, since exploratory/full-section results now exist.

### Page 8

- Discussion and threats:
  - Current: says `RQ4's normalization strategies` are one response to GitHub-mining threats.
  - Action: keep, but make it more specific.
  - Suggested wording:
    - `RQ4's response is to model high-volume author-repo concentration, add GitHub PR complexity fields, and separate broad account age from repository relationship via author association.`

- External validity:
  - Current threat: `popular-repo-only AIDev-pop`.
  - Action: keep and add subset limitation:
    - `The GitHub-enriched complexity analysis is currently based on a successful 2,003-PR subset, so final claims should be treated as provisional until enrichment is expanded.`

### Pages 9-11

- Responsibilities/timeline:
  - Current:
    - `Kunwar Pending - RQ4 normalization & experience models`
    - `Kunwar RQ4 Experience / robustness Scope defined Implement experience + normalization analyses, write section`
    - `RQ4 experience + normalization Kunwar`
    - `RQ4 section write-up Kunwar`
  - Action: update status from pending/scope-defined to current state.
  - Suggested replacement:
    - `Kunwar: RQ4 experience / robustness - exploratory and controlled models complete on AIDev-pop plus a GitHub-enriched 2,003-PR subset; remaining work is to expand enrichment coverage, polish tables/figures, and integrate into final discussion.`

## Recommended interim framing

Do not say we will analyze "all GitHub repos" unless the team truly means the full public GitHub universe. More accurate wording:

`Current limitation: the PR-complexity and author-association controls use a GitHub-enriched subset of AIDev-pop. For the final report, we plan to expand enrichment to the largest feasible set of AIDev-pop pull requests, subject to GitHub API rate limits, public repository availability, and missing/deleted PRs.`

## One-paragraph team update

`Kunwar's RQ4 section is no longer just a skeleton. I have exploratory and controlled analyses for developer experience, PR complexity, author association, task category, and agent choice. The main finding so far is that developer experience measured by GitHub account age is not a robust independent predictor after controls. PR complexity and repository/social context matter more: higher churn lowers merge odds, commit count is associated with more review activity, and GitHub author association strongly affects merge and review duration. The current complexity/author-association model uses a GitHub-enriched 2,003-PR subset, so the final phase should scale enrichment to the largest feasible AIDev-pop coverage and check whether the conclusions hold.`
