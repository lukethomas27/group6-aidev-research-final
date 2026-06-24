# RQ4 Revised Work: Developer Experience, PR Complexity, and Repository Context

Prepared for Group 6 final report integration.

## Research Question

**RQ4:** To what extent does developer experience influence agent-assisted pull request outcomes after accounting for agent choice, task type, PR complexity, repository context, author association, and dataset imbalance?

This question supports the broader project question:

> To what extent does the choice of AI coding agent affect pull request outcomes, including review sentiment, review engagement, acceptance, review duration, and merge success, across different task categories after accounting for pull request complexity, repository characteristics, developer experience, and dataset imbalance?

## Purpose

This section contributes the developer-experience, pull-request complexity, and repository-context layer of the team's broader analysis of AI coding agents in open-source pull requests. It connects the sentiment, review-engagement, within-repository outcome, and imbalance analyses by asking whether apparent agent effects persist once author standing, PR size, and repository context are modeled directly.

## Data and Method

The analysis uses AIDev-pop, which contains 33,596 agent-authored pull requests from 2,807 repositories with more than 100 stars. The broader AIDev cache was also used to construct observed author-repository history and high-volume author-repository concentration checks.

Primary AIDev tables used:

- `pull_request.parquet`
- `user.parquet`
- `repository.parquet`
- `pr_reviews.parquet`
- `pr_comments.parquet`
- `pr_review_comments_v2.parquet`
- `pr_timeline.parquet`

GitHub-enriched subset:

- 2,025 PR rows queried through the GitHub REST API.
- 2,003 successful fetches.
- GitHub fields used: additions, deletions, changed files, commits, author association, state, and merge status.

Experience and context measures:

- Developer experience: GitHub account age at PR creation.
- Secondary reputation proxy: log follower count.
- PR complexity: GitHub total churn, changed files, and commit count.
- Repository relationship: GitHub `author_association`.
- Robustness controls: agent, task category, PR month, repository context, high-volume author-repo pair exclusion, and repository-clustered standard errors.

## Data Quality and High-Volume Account Check

Extreme author-repository pairs are defined as author-repo combinations with more than 100 observed PRs in the broader AIDev dataset. This captures repeated high-volume workflows that can distort naive agent comparisons.

| Agent | Extreme pairs | PRs in extreme pairs | Total PRs | Extreme PR share |
|---|---:|---:|---:|---:|
| Claude Code | 2 | 3 | 458 | 0.7% |
| Cursor | 3 | 112 | 1,541 | 7.3% |
| Devin | 10 | 2,023 | 4,827 | 41.9% |
| OpenAI Codex | 17 | 15,019 | 21,799 | 68.9% |

Extreme author-repo concentration is a major confound. OpenAI Codex and Devin have especially large shares of PRs in extreme author-repo pairs, so naive global agent comparisons can overstate agent effects.

## GitHub-Enriched PR Complexity Sample

The enriched subset shows that agents differ in PR scale and author association before outcomes are modeled.

| Agent | Enriched PRs | Median churn | Median files | Median commits | Owner/member/collab |
|---|---:|---:|---:|---:|---:|
| Claude Code | 117 | 561 | 7 | 2 | 47.9% |
| Cursor | 280 | 120 | 3 | 2 | 60.0% |
| OpenAI Codex | 1,606 | 47 | 2 | 1 | 74.9% |

Claude Code PRs in the enriched sample are much larger by median churn and changed files. OpenAI Codex PRs are smaller and more often come from owner, member, or collaborator author associations. This reinforces the need to control for PR complexity and author association before interpreting agent effects.

## Task Categories

Task categories were assigned with lightweight keyword rules over PR titles and limited body text. They are useful as descriptive strata and controls, not as gold-label annotations.

| Task | PRs | Merge | Human review | Approval | Discussion | Median events |
|---|---:|---:|---:|---:|---:|---:|
| feature | 9,988 | 75.4% | 11.4% | 7.9% | 17.4% | 5 |
| bugfix | 5,020 | 70.6% | 15.3% | 11.4% | 25.7% | 6 |
| docs | 3,549 | 85.0% | 12.9% | 10.9% | 16.5% | 5 |
| test | 3,110 | 80.4% | 6.3% | 4.7% | 9.9% | 5 |
| other | 2,264 | 80.2% | 8.8% | 6.8% | 13.0% | 5 |
| ci_build | 1,892 | 77.5% | 12.9% | 10.4% | 17.8% | 5 |
| dependency | 1,411 | 76.0% | 15.5% | 12.0% | 21.6% | 5 |
| refactor | 927 | 71.0% | 15.7% | 12.1% | 21.6% | 5 |
| security | 259 | 64.1% | 25.5% | 21.2% | 37.5% | 8 |
| performance | 205 | 54.6% | 14.6% | 10.7% | 24.9% | 6 |

Security, feature, and bugfix PRs receive more review activity than test or documentation PRs. Documentation and test PRs merge at higher rates, while performance and security PRs have lower merge rates.

## Key Controlled Results

The strongest model uses the GitHub-enriched, human-account-linked, non-extreme sample. It controls for agent, task category, account age, followers, GitHub total churn, changed files, commits, author association, PR month, and repository-clustered standard errors.

### Human Review and Approval

| Outcome | Effect | OR | 95% CI | p |
|---|---|---:|---:|---:|
| Human review | account age, per SD | 0.949 | 0.740-1.217 | 0.679 |
| Human review | GitHub total churn, log1p per SD | 0.627 | 0.492-0.798 | <0.001 |
| Human review | GitHub commits, log1p per SD | 1.926 | 1.553-2.388 | <0.001 |
| Approval | account age, per SD | 0.925 | 0.702-1.220 | 0.582 |
| Approval | GitHub total churn, log1p per SD | 0.659 | 0.518-0.837 | <0.001 |
| Approval | GitHub commits, log1p per SD | 1.537 | 1.256-1.881 | <0.001 |

Account age does not robustly predict human review or approval. PR complexity matters more: higher churn is associated with lower review/approval odds, while commit count is associated with higher review/approval odds.

### Merge Success

Merge success is modeled only among closed PRs in the GitHub-enriched, human-account-linked, non-extreme sample.

| Merge model effect | OR | 95% CI | p |
|---|---:|---:|---:|
| account age, per SD | 1.132 | 0.917-1.399 | 0.248 |
| GitHub total churn, log1p per SD | 0.635 | 0.525-0.768 | <0.001 |
| GitHub commits, log1p per SD | 1.292 | 1.078-1.549 | 0.006 |
| author_association=OWNER vs CONTRIBUTOR | 2.453 | 1.622-3.710 | <0.001 |
| author_association=NONE vs CONTRIBUTOR | 0.046 | 0.012-0.171 | <0.001 |
| agent=Claude Code vs OpenAI Codex | 1.875 | 0.845-4.157 | 0.122 |
| agent=Cursor vs OpenAI Codex | 1.072 | 0.645-1.784 | 0.788 |

Account age is not significant for merge success. The strongest predictors are PR complexity and repository relationship. Larger PRs, measured by total churn, have lower merge odds. More commits have higher merge odds, possibly because they capture iteration or active engagement. Owner authors have much higher merge odds, while authors with no repository association have much lower merge odds.

Agent effects weaken after controls. Claude Code and Cursor do not show stable merge advantages over OpenAI Codex in this enriched controlled model.

## Review Duration

Review duration was modeled as log1p hours to first human review among PRs that received a human review. In the non-extreme human-linked sample, the median time to first human review was 3.60 hours.

| Effect | Duration ratio | 95% CI | p |
|---|---:|---:|---:|
| account age, per SD | 0.984 | 0.765-1.267 | 0.901 |
| GitHub total churn, log1p per SD | 1.339 | 0.964-1.862 | 0.082 |
| GitHub commits, log1p per SD | 1.557 | 1.185-2.045 | 0.001 |
| author_association=NONE vs CONTRIBUTOR | 7.834 | 2.548-24.091 | <0.001 |
| agent=Claude Code vs OpenAI Codex | 0.751 | 0.343-1.644 | 0.473 |
| agent=Cursor vs OpenAI Codex | 0.724 | 0.426-1.228 | 0.230 |

Account age and agent choice do not robustly predict review duration. More commits are associated with longer time to first human review, and authors with no GitHub association to the repository wait substantially longer.

## Final RQ4 Narrative

Developer experience, measured by GitHub account age, is not a robust independent predictor of agent-assisted pull request outcomes after controlling for task type, PR complexity, repository context, author association, and high-volume account behavior.

The apparent experience effects in raw summaries are mostly explained by confounding. Outcomes are better explained by whether the PR is reviewable and appropriately scoped, whether the author has standing in the repository, and whether the contribution occurs in a high-volume repeated workflow.

The strongest evidence points to context-driven trust rather than agent-driven trust. Maintainer-like authors are trusted more. Smaller PRs are more likely to merge. More iterative PRs, measured by commits, receive more review activity and are somewhat more likely to merge. Agent effects are weaker and less stable after controls.

Therefore, OSS acceptance of AI-assisted PRs appears to depend less on which AI agent was used and more on whether the PR is reviewable, scoped appropriately, submitted by a trusted project participant, and situated in a repository context where the author has standing.

## Connection to Other Research Questions

RQ4 connects the rest of the report by explaining why raw agent-level results need context:

- RQ1 shows that sentiment rankings differ depending on method.
- RQ2 shows that review coverage and scrutiny vary strongly by agent.
- RQ3 shows that some within-repository outcome differences persist after repository controls.
- RQ4 shows that PR complexity and author association explain more than broad developer account age.
- Q6 shows that dataset imbalance and high-volume author-repo pairs can distort naive agent comparisons.

The combined interpretation is that AI coding agent trust is not one-dimensional. It is shaped by review process, task type, PR size, author relationship, repository norms, and dataset imbalance.

## Suggested Figures

Use these visuals if the report or poster needs RQ4-specific figures:

- `outputs/figures/rq4_extreme_author_repo_share.svg`
- `outputs/figures/rq4_github_enriched_complexity_by_agent.svg`
- `outputs/figures/rq4_outcomes_by_experience_quartile.svg`
- `outputs/figures/rq4_merge_model_key_effects.svg`
- `outputs/figures/rq4_review_duration_key_effects.svg`

Suggested captions:

**Figure: High-volume author-repository concentration by agent.** Extreme author-repo pairs account for a large share of OpenAI Codex and Devin PRs, showing why naive agent-level comparisons are confounded.

**Figure: GitHub-enriched PR complexity by agent.** Median churn, changed files, and commits differ across agents in the enriched sample, motivating explicit complexity controls.

**Figure: Outcomes by developer-experience quartile.** Raw outcome rates do not form a simple monotonic experience gradient, especially after excluding centralized/non-human-linked agent rows.

**Figure: Controlled merge model key effects.** In the enriched closed-PR model, author association and PR complexity are stronger predictors of merge success than account age or agent label.

**Figure: Review-duration model key effects.** Authors with no repository association wait substantially longer for first human review, while account age and agent label are not robust duration predictors.

## Limitations Specific to RQ4

- GitHub enrichment covers a 2,003-PR subset, not the full AIDev-pop dataset.
- Account age is a broad proxy for developer experience and does not capture repository-specific expertise.
- Follower count is a reputation-like proxy, but it may not reflect follower count at PR creation time.
- GitHub `author_association` is a useful trust-context proxy, but it is not a complete model of maintainer identity or informal authority.
- Agent labels may hide different levels of human involvement.
- The analysis is observational and should not be interpreted causally.
- Some agents are thinly represented in the enriched sample, especially Claude Code.

## Appendix-Ready Contribution Line

Kunwarbir Singh led RQ4 developer-experience and GitHub-enriched PR-complexity models, including account-age and follower proxies, author-association controls, high-volume author-repo robustness checks, controlled outcome models, review-duration models, and final synthesis with the Q6 imbalance audit.

