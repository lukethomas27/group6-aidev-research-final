# Q4 — Within-repo agent comparison & specialization (AIDev)

**Question.** In repositories where ≥2 agents each appear with ≥k PRs, which agents get
higher acceptance and faster merges, and do agents specialize within a repo (by task type
or change size)? Comparisons are made **within the same repo** so repo culture / maintainer
strictness / domain are held fixed.

**Data.** AIDev *depth/curated* set (`hao-li/AIDev`): 33,596 PRs, 2,807 repos, 5 agents.
Run **co-primary at k=5 and k=10** per the threshold decision. Reference agent in all
models = **OpenAI Codex** (the hub agent, present in nearly every qualifying repo).
All numbers below are reproduced by the executed notebook `SENG404_Q4_starter.ipynb`.

---

## 1. Feasibility (Section 3)

| | k = 5 | k = 10 |
|---|---|---|
| Qualifying repos (≥2 agents, each ≥k PRs) | **37** | **17** |
| PRs in working panel | **2,481** | **1,456** |
| Codex present in (repos) | 30 | 13 |
| Cursor | 21 | 10 |
| Devin | 17 | 11 |
| GitHub Copilot | 10 | 3 |
| Claude Code | 4 | **0 (drops out)** |

Q4 is **viable**. Most shared agent pairs (k=5): Cursor↔Codex (16 repos), Devin↔Codex (13),
Cursor↔Devin (8), Copilot↔Codex (6). Because Codex co-occurs with almost everyone, most
within-repo contrasts are effectively *“X vs Codex.”* Per-(repo,agent) N is reported in the
notebook (Section 3). **Codex is overrepresented** (21,799 of 33,596 PRs dataset-wide); the
within-repo design is the main control for this, and Codex is the regression reference.

---

## 2. Part A — Within-repo acceptance

### Within-repo-centered acceptance (descriptive, Section 4)
Mean of each agent’s per-repo acceptance minus its repo’s baseline (>0 = above baseline).

| Agent | k=5 (n repos) | k=10 (n repos) |
|---|---|---|
| Claude Code | **+0.097** (4) | — (0) |
| OpenAI Codex | +0.050 (30) | +0.014 (13) |
| Cursor | +0.011 (21) | **+0.042** (10) |
| Devin | −0.047 (17) | −0.015 (11) |
| GitHub Copilot | **−0.132** (10) | **−0.148** (3) |

This unweighted descriptive is noisy (each repo-cell weighted equally) and **disagrees with
the PR-weighted model on the Codex-vs-Cursor ordering** — see below. It is reported because
it is a required figure (`figures/acceptance_centered_k{5,10}.png`), but the FE logit and
paired tests are the inferential evidence.

### Paired Wilcoxon on per-repo acceptance (pairs with ≥6 shared repos)
- **k=5:** the only significant contrast is **Codex > GitHub Copilot** (16→ n=6 repos, median
  diff +0.38, p=0.031). Codex vs Cursor n.s. (n=16, p=0.56; Cursor higher by 0.065 median),
  Codex vs Devin n.s. (n=13, p=0.31).
- **k=10:** **Cursor > Codex is significant** (n=7, median diff +0.122, p=0.016). Codex vs
  Devin n.s. (p=0.94), Cursor vs Devin n.s. (p=0.84).

### Within-repo FE logit — RAW vs task+size-ADJUSTED (Section 5)
`is_merged ~ C(agent) + C(repo_id)` (raw) and `+ C(task_type) + log_loc + files_touched`
(adjusted), MLE, odds ratios vs Codex. **Claude Code is excluded from the logit** (perfect
separation: only 4 repos at k=5, 0 at k=10); it remains in the descriptive / JSD / size
analyses where it is stable.

**k=5** (n_decided = 2,313 raw / 2,310 adjusted):

| Agent | OR raw | p raw | OR adjusted | p adj | RAW→ADJ shift |
|---|---|---|---|---|---|
| Cursor | 1.92 | <0.001 | 2.01 | <0.001 | +0.10 |
| Devin | 0.72 | 0.046 | 0.78 | 0.149 | +0.06 |
| GitHub Copilot | 0.29 | <0.001 | 0.25 | <0.001 | −0.04 |

**k=10** (n_decided = 1,385 / 1,384):

| Agent | OR raw | p raw | OR adjusted | p adj | RAW→ADJ shift |
|---|---|---|---|---|---|
| Cursor | 2.94 | <0.001 | 3.23 | <0.001 | +0.28 |
| Devin | 0.88 | 0.48 | 0.94 | 0.74 | +0.06 |
| GitHub Copilot | 0.29 | 0.017 | 0.37 | 0.063 | +0.07 |

**The raw→adjusted gap is small and never reverses a sign.** Controlling for task type and PR
size barely changes (and slightly strengthens) the agent acceptance effects — so the
acceptance differences are **not** an artifact of task mix or change size.

**Acceptance verdict (both thresholds):** **Cursor highest, GitHub Copilot clearly lowest**
(OR ≈ 0.25–0.37 vs Codex, i.e. roughly a third the odds of merging within the same repo);
Devin slightly below Codex but not robustly significant once adjusted. (Note the descriptive
centered-mean ranks Codex above Cursor; the PR-weighted FE logit + the k=10 paired test put
Cursor first — we trust the model.)

---

## 3. Part A — Merge speed (Cox PH, Section 5)

Time-to-merge, **stratified by repo**; event = merged; open and closed-unmerged PRs are
**right-censored, not dropped** (k=5: 721 of 2,338 censored; k=10: 472 of 1,385). HR > 1 =
merges **faster** than Codex.

| Covariate | HR k=5 | p | HR k=10 | p |
|---|---|---|---|---|
| Cursor | **1.45** | <0.001 | **1.56** | <0.001 |
| Devin | **0.78** | 0.001 | **0.77** | 0.003 |
| GitHub Copilot | 0.94 | 0.72 | 0.70 | 0.23 |
| Claude Code | 0.97 | 0.88 | — | — |
| log_loc (per unit) | 0.87 | <0.001 | 0.86 | <0.001 |

**Speed verdict (both thresholds):** **Cursor merges fastest** (~45–56% higher merge hazard
than Codex), **Devin slowest** (~22% lower). Copilot/Claude not distinguishable from Codex
(wide CIs, thin support). **Larger PRs merge slower** (≈13–14% lower hazard per log-LOC).

---

## 4. Part B — Task-type specialization (Section 6)

Jensen–Shannon divergence of each (repo,agent) task distribution from the repo-wide
distribution (higher = more specialized). Divergences are **modest** (0.21–0.38) — agents
lean toward niches rather than occupying disjoint ones.

| Agent | JSD k=5 (n) | JSD k=10 (n) |
|---|---|---|
| Claude Code | **0.381** (4) | — |
| Cursor | 0.286 (21) | 0.256 (10) |
| GitHub Copilot | 0.264 (10) | **0.322** (3) |
| OpenAI Codex | 0.250 (30) | 0.222 (13) |
| Devin | 0.232 (17) | 0.214 (11) |

Task-share tendencies (k=5 row-normalized): **Devin is the most feature-skewed** (54% `feat`),
**Copilot leans fixes/CI** (44% `fix`, highest `ci`/`build`), **Cursor does more docs/fixes**
(13% `docs`, 33% `fix`), **Codex is the most balanced**, and **Claude Code skews feat+refactor**
(48% `feat`, 12% `refactor`, small n). See `figures/task_mix_k{5,10}.png` for the per-repo
stacked mix in the top qualifying repos.

---

## 5. Part B — Size specialization (Section 7)

`log_loc ~ C(agent) + C(repo_id)`; coefficient = within-repo difference in log LOC vs Codex
(+ = larger PRs). Kruskal–Wallis is a per-repo non-parametric cross-check.

| Agent | coef k=5 | p | coef k=10 | p |
|---|---|---|---|---|
| Cursor | +0.72 | <0.001 | +0.67 | <0.001 |
| Devin | +0.88 | <0.001 | +0.74 | <0.001 |
| GitHub Copilot | −0.30 | 0.32 | −0.17 | 0.72 |
| Claude Code | **+1.76** | <0.001 | — | — |

Median raw LOC (k=5): **Codex 57 < Copilot 74 < Devin 150 ≈ Cursor 162 < Claude Code 620**.
Within-repo size differences are significant in **12/37 repos (k=5)** and **7/17 (k=10)**.

**Size verdict:** strong, consistent specialization. **Codex is the small-change agent**;
**Cursor and Devin handle larger changes**; **Claude Code makes by far the largest PRs**
(small n). This is the **A↔B confound made concrete**: the bigger-PR agents (Cursor, Devin)
diverge in acceptance/speed in opposite directions (Cursor up, Devin down), and the FE-logit
size adjustment (Section 2) shows size does **not** drive the acceptance gap.

---

## 6. Robustness & caveats

- **Conclusions hold across k=5 and k=10** for every headline: Cursor highest acceptance &
  fastest; Copilot lowest acceptance; Devin slowest & feature-skewed; Codex smallest PRs;
  size differences significant in ~⅓–⅖ of repos. The k=10 paired test additionally confirms
  Cursor > Codex acceptance.
- **Codex overrepresentation:** Codex is the reference and co-occurs with nearly all agents,
  so most contrasts are vs Codex; results are *relative to Codex* by construction. The
  within-repo FE design is the control. (Feeds the group’s Q6 robustness discussion.)
- **Claude Code is fragile:** 4 repos at k=5, 0 at k=10; excluded from the FE logit
  (separation). Treat its acceptance as indicative only; its size/specialization signal is
  large but rests on few repos.
- **Censoring handled:** open + closed-unmerged PRs are censored in the Cox model, not
  dropped from the speed analysis.
- **Descriptive vs model disagreement** on Codex-vs-Cursor acceptance is real and reported;
  the PR-weighted FE logit + paired test are the basis for the verdict.
