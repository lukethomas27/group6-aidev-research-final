# AI Coding Agent Trust and Pull Request Outcomes in OSS

## Executive Summary

This report analyzes the AIDev dataset to understand how AI coding agents are associated with pull request outcomes in open-source software. The broader research question is:

> To what extent does the choice of AI coding agent affect pull request outcomes, including review sentiment, acceptance, review duration, and merge success, across different task categories after accounting for pull request complexity, repository characteristics, and developer experience?

Our analysis finds that raw differences between agents are strongly confounded by account behavior, pull request size, and repository/social context. In descriptive results, agents appear to differ substantially in merge and review rates. However, after excluding high-volume author-repo pairs, enriching a 2,003-PR subset with GitHub pull request metrics, and controlling for task type, PR complexity, author association, and developer experience, broad developer experience and agent choice are not consistently robust predictors of merge success.

The strongest predictors are PR and repository context:

- Larger PRs, measured by total churn, have lower merge odds.
- PRs with more commits receive more review/discussion and have slightly higher merge odds.
- GitHub author association matters strongly: `OWNER` authors are more likely to merge, while `NONE` authors are much less likely to merge.
- Account age, our broad proxy for developer experience, is not a robust predictor once other controls are included.
- Agent effects weaken substantially after controls. `Claude_Code` and `Cursor` do not show stable merge advantages over `OpenAI_Codex` in the GitHub-enriched controlled model.

## Data Sources

Primary data came from the Hugging Face dataset [`hao-li/AIDev`](https://huggingface.co/datasets/hao-li/AIDev). We used the following tables:

- `all_pull_request.parquet`
- `all_user.parquet`
- `pull_request.parquet`
- `user.parquet`
- `repository.parquet`
- `pr_reviews.parquet`
- `pr_comments.parquet`
- `pr_review_comments_v2.parquet`
- `pr_timeline.parquet`

We also enriched a subset of AIDev-pop PRs using the GitHub REST API pull request endpoint, which provides fields such as `additions`, `deletions`, `changed_files`, `commits`, and `author_association`. Documentation: [GitHub REST Pulls API](https://docs.github.com/en/rest/pulls/pulls?apiVersion=2022-11-28).

## Measures

### Outcomes

We measured five outcomes:

- `merged`: whether the PR was merged, modeled only on closed PRs.
- `has_human_review`: whether a human review was submitted.
- `has_approval`: whether a human approval review was submitted.
- `has_changes_requested`: whether a human change-request review was submitted.
- `has_human_discussion`: whether there was any human review, issue comment, or inline review comment.

We also modeled review duration:

- `time_to_first_human_review_hours`: hours from PR creation to first human review, modeled as `log1p(hours)` among PRs with a human review.

### Main Predictors and Controls

Agent labels came from the AIDev `agent` field. The primary agents observed in the analysis were:

- `OpenAI_Codex`
- `Claude_Code`
- `Cursor`
- `Devin`
- `Copilot`

Developer experience was measured using GitHub account age at PR creation. We also considered followers as a reputation-like proxy.

Repository and PR controls included:

- repository stars and forks
- repository language
- PR creation month
- prior observed author-repo PR count
- prior observed author-repo merge rate
- timeline commits/events/force pushes
- GitHub-enriched total churn: `additions + deletions`
- GitHub-enriched changed files
- GitHub-enriched commit count
- GitHub `author_association`

Standard errors were clustered by repository.

## Data Quality and Confounding Checks

### Centralized and High-Volume Accounts

The dataset contains extreme author-repo concentration for some agents. We defined extreme author-repo pairs as pairs with more than 100 observed PRs in AIDev, roughly the top 1% tail.

| Agent | PRs in Extreme Pairs | Total PRs | Extreme Pair Share |
|---|---:|---:|---:|
| Claude_Code | 3 | 458 | 0.66% |
| Cursor | 112 | 1,541 | 7.27% |
| Devin | 2,023 | 4,827 | 41.91% |
| OpenAI_Codex | 15,019 | 21,799 | 68.90% |

This is a major threat to naive comparisons. For example, a large share of `OpenAI_Codex` PRs in AIDev-pop come from a small number of high-volume author-repo pairs. We therefore used human-account-linked, non-extreme samples for robustness models.

### GitHub-Enriched Sample

We enriched 2,025 PR rows through the GitHub API. Of these, 2,003 were successfully fetched, a 98.9% success rate.

In the enriched sample:

- median total churn was 57 lines
- median changed files was 2
- median commits was 1
- 71.2% of PRs were from `OWNER`, `MEMBER`, or `COLLABORATOR` author associations

By agent:

| Agent | Enriched PRs | Median Total Churn | Median Changed Files | Median Commits | Owner/Member/Collaborator Rate |
|---|---:|---:|---:|---:|---:|
| Claude_Code | 117 | 561 | 7 | 2 | 47.86% |
| Cursor | 280 | 120 | 3 | 2 | 60.00% |
| OpenAI_Codex | 1,606 | 47 | 2 | 1 | 74.91% |

This suggests the enriched sample still differs by agent in task/PR scale. Therefore, complexity controls are necessary.

## Task Categories

Task categories were assigned using lightweight keyword rules over PR title and limited body text. These categories are useful for stratification and controls, but they are not gold-label annotations.

| Task Category | PRs | Merge Rate | Human Review Rate | Approval Rate | Human Discussion Rate |
|---|---:|---:|---:|---:|---:|
| feature | 9,988 | 75.37% | 11.36% | 7.93% | 17.39% |
| bugfix | 5,020 | 70.56% | 15.30% | 11.39% | 25.74% |
| docs | 3,549 | 84.95% | 12.91% | 10.93% | 16.46% |
| test | 3,110 | 80.35% | 6.33% | 4.69% | 9.90% |
| ci_build | 1,892 | 77.54% | 12.90% | 10.36% | 17.81% |
| dependency | 1,411 | 75.97% | 15.45% | 12.05% | 21.62% |
| refactor | 927 | 70.98% | 15.75% | 12.08% | 21.57% |
| security | 259 | 64.09% | 25.48% | 21.24% | 37.45% |
| performance | 205 | 54.63% | 14.63% | 10.73% | 24.88% |

Security and feature-like PRs received more human review and discussion, while documentation and test PRs had higher merge rates. Performance PRs had the lowest merge rate, though the sample size was small.

## Controlled Results

The strongest model uses the GitHub-enriched, human-account-linked, non-extreme sample. It controls for agent, task category, account age, followers, GitHub total churn, changed files, commits, author association, PR month, and repository-clustered standard errors.

### Human Review

In the enriched model, account age did not predict human review:

- account age: OR 0.95, p = 0.679

PR complexity was more important:

- total churn: OR 0.63, p < 0.001
- commits: OR 1.93, p < 0.001

Agent effects were weak:

- `Claude_Code` vs `OpenAI_Codex`: OR 1.13, p = 0.795
- `Cursor` vs `OpenAI_Codex`: OR 1.81, p = 0.050

### Approval

Account age was again not significant:

- account age: OR 0.93, p = 0.582

Complexity remained important:

- total churn: OR 0.66, p < 0.001
- commits: OR 1.54, p < 0.001

Agent effects were not robust at conventional levels:

- `Claude_Code` vs `OpenAI_Codex`: OR 1.28, p = 0.597
- `Cursor` vs `OpenAI_Codex`: OR 1.79, p = 0.068

### Human Discussion

Account age was not significant:

- account age: OR 0.97, p = 0.772

Complexity again mattered:

- total churn: OR 0.78, p = 0.018
- commits: OR 1.73, p < 0.001

`Claude_Code` showed a positive but not conventionally significant association with human discussion:

- `Claude_Code` vs `OpenAI_Codex`: OR 2.04, p = 0.080

### Merge Success

Among closed PRs, account age was not significant:

- account age: OR 1.13, p = 0.248

The strongest predictors were PR complexity and author association:

- total churn: OR 0.64, p < 0.001
- commits: OR 1.29, p = 0.006
- `OWNER` vs `CONTRIBUTOR`: OR 2.45, p < 0.001
- `NONE` vs `CONTRIBUTOR`: OR 0.046, p < 0.001

Agent effects were not significant:

- `Claude_Code` vs `OpenAI_Codex`: OR 1.87, p = 0.122
- `Cursor` vs `OpenAI_Codex`: OR 1.07, p = 0.788

### Review Duration

Review duration was modeled as log-hours to first human review. In the non-extreme human-linked sample, the median time to first human review was 3.60 hours.

Agent choice was not a robust predictor of review duration:

- `Claude_Code` vs `OpenAI_Codex`: duration ratio 1.23, p = 0.383
- `Cursor` vs `OpenAI_Codex`: duration ratio 0.81, p = 0.209

Account age also did not predict duration:

- account age: duration ratio 1.04, p = 0.590

In the GitHub-enriched duration model, commit count lengthened review duration:

- commits: duration ratio 1.56, p = 0.001

Authors with `NONE` association had much longer time to first review:

- `NONE` vs `CONTRIBUTOR`: duration ratio 7.83, p < 0.001

## Interpretation

The raw dataset appears to suggest differences by developer experience and by agent. However, these apparent effects are substantially reduced after accounting for:

- centralized or high-volume account behavior
- task category
- true PR size
- commit count
- author association
- repository clustering

This means that the observed outcomes of AI-assisted PRs are better explained by the social and technical context of the PR than by the agent label alone.

The findings suggest the following:

1. OSS communities seem to evaluate agent-assisted PRs through ordinary project-maintenance signals: author trust, PR size, and reviewability.
2. AI agent choice may influence workflow and task mix, but it does not independently dominate merge success after controls.
3. Developer experience measured by GitHub account age is too broad to explain outcomes once repository-specific and PR-specific factors are included.
4. Author association is a particularly strong proxy for trust. Owners merge more readily, while authors with no association face lower merge odds and longer review times.
5. Larger PRs are riskier. Higher churn reduces merge odds, while more commits may indicate iteration/review engagement.

## Answer to the Research Question

Agent choice alone does not robustly explain pull request outcomes once task type, PR complexity, repository context, author association, high-volume account artifacts, and developer experience are taken into account.

The strongest evidence points to context-driven trust rather than agent-driven trust:

- Maintainer-like authors are trusted more.
- Smaller PRs are more likely to merge.
- More iterative PRs, measured by commits, receive more review activity and are somewhat more likely to merge.
- Agent effects are weaker and less stable after controls.
- Developer account age is not a robust independent predictor.

Therefore, OSS acceptance of AI-assisted PRs appears to depend less on which AI agent was used and more on whether the PR is reviewable, scoped appropriately, submitted by a trusted project participant, and situated in a repository context where the author has standing.

## Limitations

This study has several limitations:

- Task categories are keyword-based and should be treated as approximate.
- GitHub enrichment was performed on a subset, not the full dataset.
- `author_association` is a proxy for maintainer status, not a complete membership model.
- Review sentiment is approximated through approvals, change requests, comments, and discussion. We did not perform full natural language sentiment analysis over review text.
- The AIDev dataset includes centralized and service-account behavior that complicates human-level preference inference.
- Follower counts are snapshot-based and may not reflect the follower count at PR creation time.
- The results are associational, not causal.
