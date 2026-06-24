# AIDev Developer Experience Analysis

Research question: Which agents do more experienced developers prefer? Does developer experience influence how AI-generated contributions are reviewed and accepted?

Experience is operationalized as GitHub account age at PR creation. Follower count is included as a secondary robustness proxy. Preference is approximated from the agent label on each PR and, for user-weighted results, the agent with the most PRs for each author account.

Important caveat: this dataset records the GitHub account that opened the PR. Some agents are heavily concentrated in one bot/service account, so their rows do not always reveal the underlying human developer's preference.

## Experience Coverage

Rows without a valid author-account creation date are excluded from experience-based summaries.

All PR table:

| agent | raw_prs | prs_with_experience | raw_authors | authors_with_experience | experience_coverage_pct |
| --- | --- | --- | --- | --- | --- |
| Copilot | 50447 | 608 | 379 | 378 | 1.21 |
| Claude_Code | 5137 | 5121 | 1643 | 1641 | 99.69 |
| Cursor | 32941 | 32916 | 9658 | 9655 | 99.92 |
| OpenAI_Codex | 814522 | 813990 | 61653 | 61636 | 99.93 |
| Devin | 29744 | 29744 | 1 | 1 | 100.00 |

AIDev-pop PR table:

| agent | raw_prs | prs_with_experience | raw_authors | authors_with_experience | experience_coverage_pct |
| --- | --- | --- | --- | --- | --- |
| Copilot | 4970 | 0 | 1 | 0 | 0.00 |
| Claude_Code | 459 | 458 | 236 | 235 | 99.78 |
| Cursor | 1541 | 1541 | 363 | 363 | 100.00 |
| Devin | 4827 | 4827 | 1 | 1 | 100.00 |
| OpenAI_Codex | 21799 | 21799 | 1284 | 1284 | 100.00 |

## Agent Preference by Experience

| agent | prs | unique_authors | median_account_age_years | median_followers | merged_rate |
| --- | --- | --- | --- | --- | --- |
| Claude_Code | 5121 | 1641 | 10.49 | 9.00 | 77.00 |
| Copilot | 608 | 378 | 5.68 | 2.00 | 78.45 |
| OpenAI_Codex | 813990 | 61636 | 4.66 | 0.00 | 87.66 |
| Cursor | 32916 | 9655 | 3.50 | 0.00 | 70.54 |
| Devin | 29744 | 1 | 1.24 | 0.00 | 64.45 |

## Account Concentration Check

| agent | prs | authors | user | top_author_pr_share_pct |
| --- | --- | --- | --- | --- |
| Devin | 29744 | 1 | devin-ai-integration[bot] | 100.00 |
| Claude_Code | 5121 | 1641 | randallb | 9.92 |
| Cursor | 32916 | 9655 | cursor[bot] | 7.28 |
| Copilot | 608 | 378 | GaryOcean428 | 2.30 |
| OpenAI_Codex | 813990 | 61636 | tamnd | 1.09 |

## Dominant Agent Within Developer Experience Quartiles

| experience_quartile | agent | developers | share_within_quartile_pct |
| --- | --- | --- | --- |
| Q1 least | OpenAI_Codex | 14856 | 82.34 |
| Q1 least | Cursor | 2965 | 16.43 |
| Q1 least | Claude_Code | 136 | 0.75 |
| Q1 least | Copilot | 84 | 0.47 |
| Q1 least | Devin | 1 | 0.01 |
| Q2 | OpenAI_Codex | 15507 | 85.95 |
| Q2 | Cursor | 2292 | 12.70 |
| Q2 | Claude_Code | 176 | 0.98 |
| Q2 | Copilot | 67 | 0.37 |
| Q3 | OpenAI_Codex | 15655 | 86.77 |
| Q3 | Cursor | 1985 | 11.00 |
| Q3 | Claude_Code | 317 | 1.76 |
| Q3 | Copilot | 84 | 0.47 |
| Q4 most | OpenAI_Codex | 15192 | 84.20 |
| Q4 most | Cursor | 1929 | 10.69 |
| Q4 most | Claude_Code | 816 | 4.52 |
| Q4 most | Copilot | 105 | 0.58 |

## Review and Acceptance by Experience Quartile, AIDev-pop

| experience_quartile | prs | merged_rate | human_review_rate | approval_rate | changes_requested_rate | human_discussion_rate | median_human_reviews | median_human_comments | median_inline_comments | median_time_to_first_human_review_hours | median_followers |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 least | 7157 | 57.97 | 29.44 | 23.07 | 3.51 | 42.00 | 0.00 | 0.00 | 0.00 | 1.25 | 0.00 |
| Q2 | 7156 | 85.70 | 7.21 | 5.53 | 0.42 | 12.37 | 0.00 | 0.00 | 0.00 | 3.56 | 178.00 |
| Q3 | 7156 | 79.84 | 5.48 | 2.93 | 0.22 | 7.49 | 0.00 | 0.00 | 0.00 | 1.09 | 132.00 |
| Q4 most | 7156 | 82.15 | 6.23 | 4.88 | 0.24 | 10.89 | 0.00 | 0.00 | 0.00 | 2.61 | 132.00 |

## Review and Acceptance by Agent and Experience Quartile, AIDev-pop

| agent | experience_quartile | prs | merged_rate | human_review_rate | approval_rate | changes_requested_rate | human_discussion_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Claude_Code | Q1 least | 97 | 46.39 | 31.96 | 26.80 | 5.15 | 58.76 |
| Claude_Code | Q2 | 203 | 70.44 | 20.20 | 13.30 | 0.99 | 39.90 |
| Claude_Code | Q3 | 57 | 28.07 | 24.56 | 10.53 | 1.75 | 54.39 |
| Claude_Code | Q4 most | 101 | 65.35 | 26.73 | 17.82 | 2.97 | 51.49 |
| Cursor | Q1 least | 336 | 61.61 | 26.49 | 22.92 | 1.49 | 38.10 |
| Cursor | Q2 | 634 | 65.46 | 26.34 | 23.19 | 1.10 | 38.96 |
| Cursor | Q3 | 352 | 72.16 | 17.05 | 11.36 | 1.70 | 23.30 |
| Cursor | Q4 most | 219 | 58.90 | 35.16 | 25.11 | 1.83 | 54.34 |
| Devin | Q1 least | 4827 | 53.76 | 36.86 | 28.36 | 4.62 | 50.90 |
| OpenAI_Codex | Q1 least | 1897 | 68.63 | 10.96 | 9.44 | 0.95 | 19.19 |
| OpenAI_Codex | Q2 | 6319 | 88.23 | 4.87 | 3.51 | 0.33 | 8.81 |
| OpenAI_Codex | Q3 | 6747 | 80.67 | 4.71 | 2.43 | 0.13 | 6.27 |
| OpenAI_Codex | Q4 most | 6836 | 83.15 | 5.00 | 4.04 | 0.15 | 8.89 |

## Human-Account-Linked Sensitivity

This excludes Devin and Copilot rows because Devin is represented by one centralized bot account and Copilot lacks author-account creation dates in AIDev-pop.

| experience_quartile | prs | merged_rate | human_review_rate | approval_rate | changes_requested_rate | human_discussion_rate | median_human_reviews | median_human_comments | median_inline_comments | median_time_to_first_human_review_hours | median_followers |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 least | 5950 | 84.07 | 6.24 | 5.24 | 0.49 | 10.79 | 0.00 | 0.00 | 0.00 | 6.04 | 178.00 |
| Q2 | 5949 | 74.15 | 14.37 | 9.60 | 0.72 | 22.04 | 0.00 | 0.00 | 0.00 | 2.38 | 132.00 |
| Q3 | 5949 | 84.48 | 0.22 | 0.10 | 0.03 | 0.34 | 0.00 | 0.00 | 0.00 | 7.93 | 132.00 |
| Q4 most | 5950 | 81.34 | 7.45 | 5.85 | 0.29 | 13.04 | 0.00 | 0.00 | 0.00 | 2.58 | 132.00 |

## Prior History and Timeline Complexity

Prior history is counted within the observed AIDev PR universe before each PR's creation time. Timeline fields are proxies for PR activity/complexity, not true code churn.

| experience_quartile | prs | median_prior_repo_prs | mean_prior_repo_prs | median_prior_repo_merged_prs | median_prior_repo_merge_rate | median_prior_user_prs | median_timeline_commits | mean_timeline_commits | median_timeline_events | median_force_pushes | median_distinct_actors |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 least | 7157 | 19.00 | 47.91 | 10.00 | 0.61 | 2689.00 | 2.00 | 3.75 | 9.00 | 0.00 | 4.00 |
| Q2 | 7156 | 112.50 | 899.22 | 111.00 | 0.98 | 161.50 | 1.00 | 1.84 | 4.00 | 0.00 | 2.00 |
| Q3 | 7156 | 1056.50 | 1523.84 | 954.00 | 0.86 | 1056.50 | 1.00 | 1.51 | 5.00 | 0.00 | 2.00 |
| Q4 most | 7156 | 5334.50 | 4062.88 | 4517.00 | 0.85 | 5334.50 | 1.00 | 1.46 | 5.00 | 0.00 | 2.00 |

## Centralized and High-Volume Account Check

Extreme author-repo pairs are defined as more than 100 observed PRs in the AIDev universe, roughly the top 1% of author-repo pairs in AIDev-pop.

Summary by agent:

| agent | author_repo_pairs | extreme_pairs | prs_in_extreme_pairs | total_prs | extreme_pair_pr_share_pct |
| --- | --- | --- | --- | --- | --- |
| Claude_Code | 253 | 2 | 3 | 458 | 0.66 |
| Cursor | 434 | 3 | 112 | 1541 | 7.27 |
| Devin | 288 | 10 | 2023 | 4827 | 41.91 |
| OpenAI_Codex | 1417 | 17 | 15019 | 21799 | 68.90 |

Largest author-repo pairs:

| agent | user | user_id | repo_id | pair_prs | observed_pair_prs_all_aidev | merged_rate | median_account_age_years | human_review_rate | human_discussion_rate | is_extreme_pair |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OpenAI_Codex | tamnd | 1218621 | 985853139 | 8913 | 8913 | 85.65 | 13.62 | 0.00 | 0.08 | True |
| OpenAI_Codex | MontrealAI | 24208299 | 922805069 | 3569 | 3569 | 98.49 | 8.53 | 0.00 | 0.00 | True |
| OpenAI_Codex | buddhika75 | 1226946 | 21764480 | 419 | 421 | 97.37 | 13.58 | 4.06 | 4.30 | True |
| Claude_Code | buddhika75 | 1226946 | 21764480 | 2 | 421 | 100.00 | 13.66 | 0.00 | 0.00 | True |
| Devin | devin-ai-integration[bot] | 158243242 | 839216423 | 343 | 343 | 71.43 | 1.34 | 76.97 | 79.30 | True |
| Devin | devin-ai-integration[bot] | 158243242 | 710601088 | 327 | 327 | 12.84 | 1.19 | 15.60 | 81.04 | True |
| Cursor | wieslawsoltes | 2297442 | 134182879 | 1 | 306 | 0.00 | 12.88 | 0.00 | 0.00 | True |
| OpenAI_Codex | wieslawsoltes | 2297442 | 134182879 | 305 | 306 | 56.07 | 12.84 | 0.33 | 0.33 | True |
| OpenAI_Codex | jdereg | 5373774 | 12670630 | 228 | 228 | 98.25 | 11.78 | 0.44 | 0.88 | True |
| OpenAI_Codex | MihaiCristianCondrea | 61864357 | 600355571 | 227 | 227 | 96.04 | 5.34 | 1.76 | 1.76 | True |
| Devin | devin-ai-integration[bot] | 158243242 | 350360184 | 220 | 220 | 35.91 | 1.30 | 52.73 | 57.27 | True |
| Devin | devin-ai-integration[bot] | 158243242 | 283046497 | 216 | 216 | 50.00 | 1.19 | 58.80 | 67.59 | True |
| Devin | devin-ai-integration[bot] | 158243242 | 955904085 | 205 | 205 | 78.54 | 1.31 | 14.15 | 39.02 | True |
| OpenAI_Codex | ryokun6 | 2830514 | 923332984 | 88 | 174 | 63.64 | 12.51 | 0.00 | 0.00 | True |
| Cursor | ryokun6 | 2830514 | 923332984 | 86 | 174 | 77.91 | 12.64 | 0.00 | 1.16 | True |
| Devin | devin-ai-integration[bot] | 158243242 | 941289933 | 171 | 171 | 82.46 | 1.24 | 32.16 | 43.27 | True |
| OpenAI_Codex | wieslawsoltes | 2297442 | 792160692 | 165 | 165 | 70.91 | 12.72 | 0.00 | 0.00 | True |
| OpenAI_Codex | peter-lawrey | 1070321 | 29301872 | 164 | 164 | 92.68 | 13.69 | 0.00 | 0.00 | True |
| Devin | devin-ai-integration[bot] | 158243242 | 959682770 | 148 | 148 | 83.11 | 1.38 | 6.76 | 22.30 | True |
| Devin | devin-ai-integration[bot] | 158243242 | 820087727 | 145 | 145 | 33.79 | 1.08 | 0.69 | 8.97 | True |

## Task Categories

Task categories are lightweight keyword classifications from PR title/body, intended as controls and descriptive strata rather than gold labels.

| task_category | prs | merged_rate | human_review_rate | approval_rate | changes_requested_rate | human_discussion_rate | median_account_age_years | median_timeline_events |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| feature | 9988 | 75.37 | 11.36 | 7.93 | 1.39 | 17.39 | 13.25 | 5.00 |
| bugfix | 5020 | 70.56 | 15.30 | 11.39 | 1.14 | 25.74 | 10.70 | 6.00 |
| docs | 3549 | 84.95 | 12.91 | 10.93 | 1.41 | 16.46 | 12.13 | 5.00 |
| test | 3110 | 80.35 | 6.33 | 4.69 | 0.45 | 9.90 | 13.56 | 5.00 |
| other | 2264 | 80.17 | 8.79 | 6.76 | 0.35 | 13.03 | 13.55 | 5.00 |
| ci_build | 1892 | 77.54 | 12.90 | 10.36 | 0.90 | 17.81 | 8.63 | 5.00 |
| dependency | 1411 | 75.97 | 15.45 | 12.05 | 1.13 | 21.62 | 8.56 | 5.00 |
| refactor | 927 | 70.98 | 15.75 | 12.08 | 0.86 | 21.57 | 10.87 | 5.00 |
| security | 259 | 64.09 | 25.48 | 21.24 | 0.77 | 37.45 | 5.29 | 8.00 |
| performance | 205 | 54.63 | 14.63 | 10.73 | 1.46 | 24.88 | 11.15 | 6.00 |

Task categories by agent:

| agent | task_category | prs | merged_rate | human_review_rate | approval_rate | human_discussion_rate | share_within_agent_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Claude_Code | feature | 196 | 52.55 | 23.98 | 14.29 | 52.55 | 42.79 |
| Claude_Code | bugfix | 101 | 58.42 | 23.76 | 15.84 | 48.51 | 22.05 |
| Claude_Code | ci_build | 45 | 60.00 | 26.67 | 22.22 | 40.00 | 9.83 |
| Claude_Code | docs | 34 | 76.47 | 26.47 | 17.65 | 50.00 | 7.42 |
| Claude_Code | dependency | 30 | 80.00 | 16.67 | 13.33 | 30.00 | 6.55 |
| Claude_Code | test | 21 | 71.43 | 38.10 | 28.57 | 52.38 | 4.59 |
| Claude_Code | refactor | 14 | 42.86 | 21.43 | 21.43 | 35.71 | 3.06 |
| Claude_Code | other | 10 | 70.00 | 40.00 | 40.00 | 50.00 | 2.18 |
| Claude_Code | security | 5 | 40.00 | 0.00 | 0.00 | 60.00 | 1.09 |
| Claude_Code | performance | 2 | 50.00 | 50.00 | 0.00 | 50.00 | 0.44 |
| Cursor | feature | 419 | 63.72 | 28.16 | 22.43 | 41.29 | 27.19 |
| Cursor | bugfix | 377 | 64.19 | 27.59 | 22.55 | 40.58 | 24.46 |
| Cursor | docs | 230 | 73.04 | 25.65 | 23.04 | 33.48 | 14.93 |
| Cursor | other | 156 | 73.08 | 20.51 | 17.31 | 26.92 | 10.12 |
| Cursor | ci_build | 100 | 67.00 | 26.00 | 18.00 | 37.00 | 6.49 |
| Cursor | dependency | 83 | 61.45 | 20.48 | 15.66 | 36.14 | 5.39 |
| Cursor | test | 73 | 57.53 | 17.81 | 15.07 | 38.36 | 4.74 |
| Cursor | refactor | 46 | 58.70 | 32.61 | 23.91 | 36.96 | 2.99 |
| Cursor | performance | 31 | 32.26 | 12.90 | 6.45 | 32.26 | 2.01 |
| Cursor | security | 26 | 65.38 | 19.23 | 19.23 | 34.62 | 1.69 |
| Devin | feature | 1654 | 57.32 | 36.82 | 26.84 | 49.88 | 34.27 |
| Devin | bugfix | 1099 | 41.22 | 29.39 | 22.02 | 51.68 | 22.77 |
| Devin | docs | 518 | 67.37 | 55.60 | 47.10 | 65.25 | 10.73 |
| Devin | dependency | 379 | 57.26 | 39.05 | 30.61 | 48.28 | 7.85 |
| Devin | ci_build | 307 | 54.07 | 41.37 | 35.50 | 52.44 | 6.36 |
| Devin | other | 278 | 70.14 | 26.62 | 20.50 | 38.13 | 5.76 |
| Devin | test | 253 | 45.85 | 28.85 | 19.76 | 41.50 | 5.24 |
| Devin | refactor | 184 | 45.65 | 41.30 | 30.43 | 48.91 | 3.81 |
| Devin | security | 106 | 44.34 | 40.57 | 33.02 | 54.72 | 2.20 |
| Devin | performance | 49 | 40.82 | 36.73 | 32.65 | 46.94 | 1.02 |
| OpenAI_Codex | feature | 7719 | 80.45 | 4.68 | 2.93 | 8.24 | 35.41 |
| OpenAI_Codex | bugfix | 3443 | 80.98 | 9.21 | 6.65 | 15.16 | 15.79 |
| OpenAI_Codex | docs | 2767 | 89.34 | 3.69 | 3.07 | 5.49 | 12.69 |
| OpenAI_Codex | test | 2763 | 84.18 | 3.73 | 2.86 | 5.94 | 12.67 |
| OpenAI_Codex | other | 1820 | 82.36 | 4.89 | 3.57 | 7.80 | 8.35 |
| OpenAI_Codex | ci_build | 1440 | 83.82 | 5.49 | 4.10 | 8.40 | 6.61 |
| OpenAI_Codex | dependency | 919 | 84.87 | 5.22 | 4.03 | 9.03 | 4.22 |
| OpenAI_Codex | refactor | 683 | 79.21 | 7.61 | 6.15 | 12.88 | 3.13 |
| OpenAI_Codex | performance | 123 | 65.85 | 5.69 | 3.25 | 13.82 | 0.56 |
| OpenAI_Codex | security | 122 | 81.97 | 14.75 | 12.30 | 22.13 | 0.56 |

## Controlled Logistic Models

Models include account age, followers, agent, repo stars, repo forks, observed prior author-repo history, timeline activity/complexity proxies, repository language, and PR creation month. Merge models are fit only on closed PRs, and standard errors are clustered by repository.

| sample | outcome | term | effect | coef_log_odds | odds_ratio | ci_low | ci_high | p_value | n | event_rate_pct | aic |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all_valid_accounts | has_human_review | C(agent, Treatment(reference='OpenAI_Codex'))[T.Claude_Code] | agent=Claude_Code vs OpenAI_Codex | 0.01 | 1.01 | 0.63 | 1.62 | 0.97 | 28625 | 12.09 | 11315.16 |
| all_valid_accounts | has_human_review | C(agent, Treatment(reference='OpenAI_Codex'))[T.Cursor] | agent=Cursor vs OpenAI_Codex | 0.53 | 1.70 | 1.07 | 2.71 | 0.02 | 28625 | 12.09 | 11315.16 |
| all_valid_accounts | has_human_review | C(agent, Treatment(reference='OpenAI_Codex'))[T.Devin] | agent=Devin vs OpenAI_Codex | 0.87 | 2.39 | 1.15 | 4.96 | 0.02 | 28625 | 12.09 | 11315.16 |
| all_valid_accounts | has_human_review | account_age_z | account age, per SD | 0.34 | 1.40 | 1.05 | 1.87 | 0.02 | 28625 | 12.09 | 11315.16 |
| all_valid_accounts | has_human_review | log_followers_z | followers, log1p per SD | -0.53 | 0.59 | 0.43 | 0.81 | 0.00 | 28625 | 12.09 | 11315.16 |
| all_valid_accounts | has_human_review | log_prior_repo_prs_z | prior observed author-repo PRs, log1p per SD | -1.02 | 0.36 | 0.25 | 0.53 | 0.00 | 28625 | 12.09 | 11315.16 |
| all_valid_accounts | has_human_review | prior_repo_merge_rate_z | prior observed author-repo merge rate, per SD | 0.11 | 1.11 | 0.98 | 1.27 | 0.10 | 28625 | 12.09 | 11315.16 |
| all_valid_accounts | has_human_review | log_timeline_commits_z | timeline commits, log1p per SD | -0.63 | 0.53 | 0.46 | 0.61 | 0.00 | 28625 | 12.09 | 11315.16 |
| all_valid_accounts | has_human_review | log_timeline_events_z | timeline events, log1p per SD | 1.90 | 6.67 | 5.05 | 8.82 | 0.00 | 28625 | 12.09 | 11315.16 |
| all_valid_accounts | has_human_review | log_timeline_force_pushes_z | timeline force pushes, log1p per SD | -0.02 | 0.98 | 0.92 | 1.04 | 0.52 | 28625 | 12.09 | 11315.16 |
| all_valid_accounts | has_approval | C(agent, Treatment(reference='OpenAI_Codex'))[T.Claude_Code] | agent=Claude_Code vs OpenAI_Codex | -0.08 | 0.92 | 0.53 | 1.59 | 0.77 | 28625 | 9.10 | 9561.88 |
| all_valid_accounts | has_approval | C(agent, Treatment(reference='OpenAI_Codex'))[T.Cursor] | agent=Cursor vs OpenAI_Codex | 0.53 | 1.70 | 1.03 | 2.79 | 0.04 | 28625 | 9.10 | 9561.88 |
| all_valid_accounts | has_approval | C(agent, Treatment(reference='OpenAI_Codex'))[T.Devin] | agent=Devin vs OpenAI_Codex | 0.50 | 1.65 | 0.77 | 3.51 | 0.20 | 28625 | 9.10 | 9561.88 |
| all_valid_accounts | has_approval | account_age_z | account age, per SD | 0.23 | 1.26 | 0.92 | 1.74 | 0.16 | 28625 | 9.10 | 9561.88 |
| all_valid_accounts | has_approval | log_followers_z | followers, log1p per SD | -0.54 | 0.58 | 0.45 | 0.75 | 0.00 | 28625 | 9.10 | 9561.88 |
| all_valid_accounts | has_approval | log_prior_repo_prs_z | prior observed author-repo PRs, log1p per SD | -1.01 | 0.36 | 0.26 | 0.51 | 0.00 | 28625 | 9.10 | 9561.88 |
| all_valid_accounts | has_approval | prior_repo_merge_rate_z | prior observed author-repo merge rate, per SD | 0.14 | 1.15 | 1.03 | 1.28 | 0.02 | 28625 | 9.10 | 9561.88 |
| all_valid_accounts | has_approval | log_timeline_commits_z | timeline commits, log1p per SD | -0.71 | 0.49 | 0.42 | 0.57 | 0.00 | 28625 | 9.10 | 9561.88 |
| all_valid_accounts | has_approval | log_timeline_events_z | timeline events, log1p per SD | 1.87 | 6.46 | 4.65 | 8.97 | 0.00 | 28625 | 9.10 | 9561.88 |
| all_valid_accounts | has_approval | log_timeline_force_pushes_z | timeline force pushes, log1p per SD | -0.06 | 0.94 | 0.88 | 1.00 | 0.06 | 28625 | 9.10 | 9561.88 |
| all_valid_accounts | has_changes_requested | C(agent, Treatment(reference='OpenAI_Codex'))[T.Claude_Code] | agent=Claude_Code vs OpenAI_Codex | -0.09 | 0.92 | 0.42 | 1.99 | 0.82 | 28625 | 1.10 | 2466.39 |
| all_valid_accounts | has_changes_requested | C(agent, Treatment(reference='OpenAI_Codex'))[T.Cursor] | agent=Cursor vs OpenAI_Codex | -0.25 | 0.78 | 0.34 | 1.77 | 0.55 | 28625 | 1.10 | 2466.39 |
| all_valid_accounts | has_changes_requested | C(agent, Treatment(reference='OpenAI_Codex'))[T.Devin] | agent=Devin vs OpenAI_Codex | 1.02 | 2.76 | 0.96 | 7.98 | 0.06 | 28625 | 1.10 | 2466.39 |
| all_valid_accounts | has_changes_requested | account_age_z | account age, per SD | -0.00 | 1.00 | 0.71 | 1.40 | 0.98 | 28625 | 1.10 | 2466.39 |
| all_valid_accounts | has_changes_requested | log_followers_z | followers, log1p per SD | -0.35 | 0.70 | 0.48 | 1.03 | 0.07 | 28625 | 1.10 | 2466.39 |
| all_valid_accounts | has_changes_requested | log_prior_repo_prs_z | prior observed author-repo PRs, log1p per SD | -0.94 | 0.39 | 0.28 | 0.55 | 0.00 | 28625 | 1.10 | 2466.39 |
| all_valid_accounts | has_changes_requested | prior_repo_merge_rate_z | prior observed author-repo merge rate, per SD | 0.02 | 1.02 | 0.86 | 1.22 | 0.82 | 28625 | 1.10 | 2466.39 |
| all_valid_accounts | has_changes_requested | log_timeline_commits_z | timeline commits, log1p per SD | 0.10 | 1.10 | 0.93 | 1.31 | 0.25 | 28625 | 1.10 | 2466.39 |
| all_valid_accounts | has_changes_requested | log_timeline_events_z | timeline events, log1p per SD | 0.83 | 2.29 | 1.55 | 3.38 | 0.00 | 28625 | 1.10 | 2466.39 |
| all_valid_accounts | has_changes_requested | log_timeline_force_pushes_z | timeline force pushes, log1p per SD | 0.05 | 1.05 | 0.98 | 1.13 | 0.16 | 28625 | 1.10 | 2466.39 |
| all_valid_accounts | has_human_discussion | C(agent, Treatment(reference='OpenAI_Codex'))[T.Claude_Code] | agent=Claude_Code vs OpenAI_Codex | 0.60 | 1.82 | 1.23 | 2.69 | 0.00 | 28625 | 18.19 | 14246.90 |
| all_valid_accounts | has_human_discussion | C(agent, Treatment(reference='OpenAI_Codex'))[T.Cursor] | agent=Cursor vs OpenAI_Codex | 0.39 | 1.48 | 0.93 | 2.37 | 0.10 | 28625 | 18.19 | 14246.90 |
| all_valid_accounts | has_human_discussion | C(agent, Treatment(reference='OpenAI_Codex'))[T.Devin] | agent=Devin vs OpenAI_Codex | 1.05 | 2.86 | 1.35 | 6.09 | 0.01 | 28625 | 18.19 | 14246.90 |
| all_valid_accounts | has_human_discussion | account_age_z | account age, per SD | 0.30 | 1.35 | 1.01 | 1.79 | 0.04 | 28625 | 18.19 | 14246.90 |
| all_valid_accounts | has_human_discussion | log_followers_z | followers, log1p per SD | -0.30 | 0.74 | 0.52 | 1.06 | 0.10 | 28625 | 18.19 | 14246.90 |
| all_valid_accounts | has_human_discussion | log_prior_repo_prs_z | prior observed author-repo PRs, log1p per SD | -0.93 | 0.39 | 0.25 | 0.62 | 0.00 | 28625 | 18.19 | 14246.90 |
| all_valid_accounts | has_human_discussion | prior_repo_merge_rate_z | prior observed author-repo merge rate, per SD | -0.10 | 0.90 | 0.78 | 1.04 | 0.16 | 28625 | 18.19 | 14246.90 |
| all_valid_accounts | has_human_discussion | log_timeline_commits_z | timeline commits, log1p per SD | -0.55 | 0.58 | 0.50 | 0.67 | 0.00 | 28625 | 18.19 | 14246.90 |
| all_valid_accounts | has_human_discussion | log_timeline_events_z | timeline events, log1p per SD | 1.72 | 5.60 | 4.32 | 7.25 | 0.00 | 28625 | 18.19 | 14246.90 |
| all_valid_accounts | has_human_discussion | log_timeline_force_pushes_z | timeline force pushes, log1p per SD | -0.03 | 0.97 | 0.91 | 1.03 | 0.29 | 28625 | 18.19 | 14246.90 |
| all_valid_accounts_closed_only | merged | C(agent, Treatment(reference='OpenAI_Codex'))[T.Claude_Code] | agent=Claude_Code vs OpenAI_Codex | 0.13 | 1.14 | 0.70 | 1.86 | 0.61 | 27392 | 79.86 | 20229.73 |
| all_valid_accounts_closed_only | merged | C(agent, Treatment(reference='OpenAI_Codex'))[T.Cursor] | agent=Cursor vs OpenAI_Codex | -0.04 | 0.96 | 0.65 | 1.40 | 0.83 | 27392 | 79.86 | 20229.73 |
| all_valid_accounts_closed_only | merged | C(agent, Treatment(reference='OpenAI_Codex'))[T.Devin] | agent=Devin vs OpenAI_Codex | -1.34 | 0.26 | 0.10 | 0.67 | 0.00 | 27392 | 79.86 | 20229.73 |
| all_valid_accounts_closed_only | merged | account_age_z | account age, per SD | -0.31 | 0.73 | 0.53 | 1.01 | 0.06 | 27392 | 79.86 | 20229.73 |
| all_valid_accounts_closed_only | merged | log_followers_z | followers, log1p per SD | 0.36 | 1.44 | 1.11 | 1.86 | 0.01 | 27392 | 79.86 | 20229.73 |
| all_valid_accounts_closed_only | merged | log_prior_repo_prs_z | prior observed author-repo PRs, log1p per SD | 0.13 | 1.14 | 0.83 | 1.56 | 0.43 | 27392 | 79.86 | 20229.73 |
| all_valid_accounts_closed_only | merged | prior_repo_merge_rate_z | prior observed author-repo merge rate, per SD | 0.60 | 1.82 | 1.60 | 2.08 | 0.00 | 27392 | 79.86 | 20229.73 |
| all_valid_accounts_closed_only | merged | log_timeline_commits_z | timeline commits, log1p per SD | -0.92 | 0.40 | 0.15 | 1.07 | 0.07 | 27392 | 79.86 | 20229.73 |
| all_valid_accounts_closed_only | merged | log_timeline_events_z | timeline events, log1p per SD | 1.68 | 5.36 | 1.01 | 28.42 | 0.05 | 27392 | 79.86 | 20229.73 |
| all_valid_accounts_closed_only | merged | log_timeline_force_pushes_z | timeline force pushes, log1p per SD | -0.07 | 0.93 | 0.78 | 1.11 | 0.42 | 27392 | 79.86 | 20229.73 |
| all_valid_accounts_no_extreme_pairs | has_human_review | C(agent, Treatment(reference='OpenAI_Codex'))[T.Claude_Code] | agent=Claude_Code vs OpenAI_Codex | 0.15 | 1.16 | 0.76 | 1.76 | 0.49 | 11468 | 21.15 | 8183.15 |
| all_valid_accounts_no_extreme_pairs | has_human_review | C(agent, Treatment(reference='OpenAI_Codex'))[T.Cursor] | agent=Cursor vs OpenAI_Codex | 0.59 | 1.80 | 1.16 | 2.77 | 0.01 | 11468 | 21.15 | 8183.15 |
| all_valid_accounts_no_extreme_pairs | has_human_review | C(agent, Treatment(reference='OpenAI_Codex'))[T.Devin] | agent=Devin vs OpenAI_Codex | 0.63 | 1.88 | 0.96 | 3.68 | 0.07 | 11468 | 21.15 | 8183.15 |
| all_valid_accounts_no_extreme_pairs | has_human_review | account_age_z | account age, per SD | 0.19 | 1.21 | 0.94 | 1.57 | 0.14 | 11468 | 21.15 | 8183.15 |
| all_valid_accounts_no_extreme_pairs | has_human_review | log_followers_z | followers, log1p per SD | -0.51 | 0.60 | 0.48 | 0.75 | 0.00 | 11468 | 21.15 | 8183.15 |
| all_valid_accounts_no_extreme_pairs | has_human_review | log_prior_repo_prs_z | prior observed author-repo PRs, log1p per SD | -0.29 | 0.75 | 0.62 | 0.90 | 0.00 | 11468 | 21.15 | 8183.15 |
| all_valid_accounts_no_extreme_pairs | has_human_review | prior_repo_merge_rate_z | prior observed author-repo merge rate, per SD | 0.01 | 1.01 | 0.89 | 1.16 | 0.83 | 11468 | 21.15 | 8183.15 |
| all_valid_accounts_no_extreme_pairs | has_human_review | log_timeline_commits_z | timeline commits, log1p per SD | -0.72 | 0.49 | 0.41 | 0.58 | 0.00 | 11468 | 21.15 | 8183.15 |
| all_valid_accounts_no_extreme_pairs | has_human_review | log_timeline_events_z | timeline events, log1p per SD | 1.88 | 6.56 | 4.90 | 8.79 | 0.00 | 11468 | 21.15 | 8183.15 |
| all_valid_accounts_no_extreme_pairs | has_human_review | log_timeline_force_pushes_z | timeline force pushes, log1p per SD | -0.01 | 0.99 | 0.90 | 1.08 | 0.76 | 11468 | 21.15 | 8183.15 |
| all_valid_accounts_no_extreme_pairs | has_approval | C(agent, Treatment(reference='OpenAI_Codex'))[T.Claude_Code] | agent=Claude_Code vs OpenAI_Codex | 0.01 | 1.01 | 0.62 | 1.66 | 0.96 | 11468 | 16.19 | 7270.45 |
| all_valid_accounts_no_extreme_pairs | has_approval | C(agent, Treatment(reference='OpenAI_Codex'))[T.Cursor] | agent=Cursor vs OpenAI_Codex | 0.61 | 1.84 | 1.16 | 2.93 | 0.01 | 11468 | 16.19 | 7270.45 |
| all_valid_accounts_no_extreme_pairs | has_approval | C(agent, Treatment(reference='OpenAI_Codex'))[T.Devin] | agent=Devin vs OpenAI_Codex | 0.24 | 1.27 | 0.61 | 2.62 | 0.52 | 11468 | 16.19 | 7270.45 |
| all_valid_accounts_no_extreme_pairs | has_approval | account_age_z | account age, per SD | 0.15 | 1.16 | 0.86 | 1.57 | 0.34 | 11468 | 16.19 | 7270.45 |
| all_valid_accounts_no_extreme_pairs | has_approval | log_followers_z | followers, log1p per SD | -0.61 | 0.54 | 0.42 | 0.70 | 0.00 | 11468 | 16.19 | 7270.45 |
| all_valid_accounts_no_extreme_pairs | has_approval | log_prior_repo_prs_z | prior observed author-repo PRs, log1p per SD | -0.33 | 0.72 | 0.58 | 0.89 | 0.00 | 11468 | 16.19 | 7270.45 |
| all_valid_accounts_no_extreme_pairs | has_approval | prior_repo_merge_rate_z | prior observed author-repo merge rate, per SD | 0.10 | 1.10 | 0.96 | 1.26 | 0.16 | 11468 | 16.19 | 7270.45 |
| all_valid_accounts_no_extreme_pairs | has_approval | log_timeline_commits_z | timeline commits, log1p per SD | -0.83 | 0.44 | 0.37 | 0.52 | 0.00 | 11468 | 16.19 | 7270.45 |
| all_valid_accounts_no_extreme_pairs | has_approval | log_timeline_events_z | timeline events, log1p per SD | 1.84 | 6.30 | 4.59 | 8.65 | 0.00 | 11468 | 16.19 | 7270.45 |
| all_valid_accounts_no_extreme_pairs | has_approval | log_timeline_force_pushes_z | timeline force pushes, log1p per SD | -0.09 | 0.91 | 0.83 | 1.00 | 0.06 | 11468 | 16.19 | 7270.45 |
| all_valid_accounts_no_extreme_pairs | has_changes_requested | C(agent, Treatment(reference='OpenAI_Codex'))[T.Claude_Code] | agent=Claude_Code vs OpenAI_Codex | -0.08 | 0.92 | 0.41 | 2.06 | 0.84 | 11468 | 2.31 | 1992.56 |
| all_valid_accounts_no_extreme_pairs | has_changes_requested | C(agent, Treatment(reference='OpenAI_Codex'))[T.Cursor] | agent=Cursor vs OpenAI_Codex | -0.26 | 0.77 | 0.35 | 1.71 | 0.52 | 11468 | 2.31 | 1992.56 |
| all_valid_accounts_no_extreme_pairs | has_changes_requested | C(agent, Treatment(reference='OpenAI_Codex'))[T.Devin] | agent=Devin vs OpenAI_Codex | 0.56 | 1.75 | 0.64 | 4.76 | 0.28 | 11468 | 2.31 | 1992.56 |
| all_valid_accounts_no_extreme_pairs | has_changes_requested | account_age_z | account age, per SD | -0.09 | 0.92 | 0.63 | 1.33 | 0.65 | 11468 | 2.31 | 1992.56 |
| all_valid_accounts_no_extreme_pairs | has_changes_requested | log_followers_z | followers, log1p per SD | -0.60 | 0.55 | 0.38 | 0.79 | 0.00 | 11468 | 2.31 | 1992.56 |
| all_valid_accounts_no_extreme_pairs | has_changes_requested | log_prior_repo_prs_z | prior observed author-repo PRs, log1p per SD | -0.19 | 0.83 | 0.63 | 1.09 | 0.18 | 11468 | 2.31 | 1992.56 |
| all_valid_accounts_no_extreme_pairs | has_changes_requested | prior_repo_merge_rate_z | prior observed author-repo merge rate, per SD | 0.01 | 1.01 | 0.83 | 1.23 | 0.93 | 11468 | 2.31 | 1992.56 |
| all_valid_accounts_no_extreme_pairs | has_changes_requested | log_timeline_commits_z | timeline commits, log1p per SD | 0.08 | 1.09 | 0.90 | 1.31 | 0.39 | 11468 | 2.31 | 1992.56 |
| all_valid_accounts_no_extreme_pairs | has_changes_requested | log_timeline_events_z | timeline events, log1p per SD | 0.91 | 2.49 | 1.69 | 3.68 | 0.00 | 11468 | 2.31 | 1992.56 |
| all_valid_accounts_no_extreme_pairs | has_changes_requested | log_timeline_force_pushes_z | timeline force pushes, log1p per SD | 0.08 | 1.08 | 0.97 | 1.20 | 0.14 | 11468 | 2.31 | 1992.56 |
| all_valid_accounts_no_extreme_pairs | has_human_discussion | C(agent, Treatment(reference='OpenAI_Codex'))[T.Claude_Code] | agent=Claude_Code vs OpenAI_Codex | 0.66 | 1.94 | 1.36 | 2.78 | 0.00 | 11468 | 32.05 | 10179.02 |
| all_valid_accounts_no_extreme_pairs | has_human_discussion | C(agent, Treatment(reference='OpenAI_Codex'))[T.Cursor] | agent=Cursor vs OpenAI_Codex | 0.36 | 1.43 | 0.92 | 2.22 | 0.11 | 11468 | 32.05 | 10179.02 |
| all_valid_accounts_no_extreme_pairs | has_human_discussion | C(agent, Treatment(reference='OpenAI_Codex'))[T.Devin] | agent=Devin vs OpenAI_Codex | 0.43 | 1.53 | 0.82 | 2.87 | 0.18 | 11468 | 32.05 | 10179.02 |
| all_valid_accounts_no_extreme_pairs | has_human_discussion | account_age_z | account age, per SD | 0.13 | 1.14 | 0.91 | 1.44 | 0.26 | 11468 | 32.05 | 10179.02 |
| all_valid_accounts_no_extreme_pairs | has_human_discussion | log_followers_z | followers, log1p per SD | -0.38 | 0.69 | 0.54 | 0.88 | 0.00 | 11468 | 32.05 | 10179.02 |
| all_valid_accounts_no_extreme_pairs | has_human_discussion | log_prior_repo_prs_z | prior observed author-repo PRs, log1p per SD | -0.24 | 0.79 | 0.68 | 0.92 | 0.00 | 11468 | 32.05 | 10179.02 |
| all_valid_accounts_no_extreme_pairs | has_human_discussion | prior_repo_merge_rate_z | prior observed author-repo merge rate, per SD | -0.17 | 0.84 | 0.74 | 0.95 | 0.01 | 11468 | 32.05 | 10179.02 |
| all_valid_accounts_no_extreme_pairs | has_human_discussion | log_timeline_commits_z | timeline commits, log1p per SD | -0.73 | 0.48 | 0.41 | 0.56 | 0.00 | 11468 | 32.05 | 10179.02 |
| all_valid_accounts_no_extreme_pairs | has_human_discussion | log_timeline_events_z | timeline events, log1p per SD | 1.83 | 6.25 | 4.91 | 7.95 | 0.00 | 11468 | 32.05 | 10179.02 |
| all_valid_accounts_no_extreme_pairs | has_human_discussion | log_timeline_force_pushes_z | timeline force pushes, log1p per SD | -0.05 | 0.95 | 0.87 | 1.04 | 0.29 | 11468 | 32.05 | 10179.02 |
| all_valid_accounts_no_extreme_pairs_closed_only | merged | C(agent, Treatment(reference='OpenAI_Codex'))[T.Claude_Code] | agent=Claude_Code vs OpenAI_Codex | -0.04 | 0.97 | 0.68 | 1.38 | 0.85 | 10528 | 70.53 | 10494.63 |
| all_valid_accounts_no_extreme_pairs_closed_only | merged | C(agent, Treatment(reference='OpenAI_Codex'))[T.Cursor] | agent=Cursor vs OpenAI_Codex | -0.10 | 0.91 | 0.71 | 1.16 | 0.44 | 10528 | 70.53 | 10494.63 |
| all_valid_accounts_no_extreme_pairs_closed_only | merged | C(agent, Treatment(reference='OpenAI_Codex'))[T.Devin] | agent=Devin vs OpenAI_Codex | -0.05 | 0.95 | 0.64 | 1.40 | 0.79 | 10528 | 70.53 | 10494.63 |
| all_valid_accounts_no_extreme_pairs_closed_only | merged | account_age_z | account age, per SD | 0.01 | 1.01 | 0.86 | 1.17 | 0.93 | 10528 | 70.53 | 10494.63 |
| all_valid_accounts_no_extreme_pairs_closed_only | merged | log_followers_z | followers, log1p per SD | 0.38 | 1.46 | 1.25 | 1.69 | 0.00 | 10528 | 70.53 | 10494.63 |
| all_valid_accounts_no_extreme_pairs_closed_only | merged | log_prior_repo_prs_z | prior observed author-repo PRs, log1p per SD | -0.23 | 0.80 | 0.70 | 0.90 | 0.00 | 10528 | 70.53 | 10494.63 |
| all_valid_accounts_no_extreme_pairs_closed_only | merged | prior_repo_merge_rate_z | prior observed author-repo merge rate, per SD | 0.68 | 1.98 | 1.78 | 2.20 | 0.00 | 10528 | 70.53 | 10494.63 |
| all_valid_accounts_no_extreme_pairs_closed_only | merged | log_timeline_commits_z | timeline commits, log1p per SD | -0.58 | 0.56 | 0.47 | 0.66 | 0.00 | 10528 | 70.53 | 10494.63 |
| all_valid_accounts_no_extreme_pairs_closed_only | merged | log_timeline_events_z | timeline events, log1p per SD | 1.00 | 2.72 | 2.19 | 3.39 | 0.00 | 10528 | 70.53 | 10494.63 |
| all_valid_accounts_no_extreme_pairs_closed_only | merged | log_timeline_force_pushes_z | timeline force pushes, log1p per SD | -0.02 | 0.98 | 0.90 | 1.07 | 0.64 | 10528 | 70.53 | 10494.63 |
| human_account_linked | has_human_review | C(agent, Treatment(reference='OpenAI_Codex'))[T.Claude_Code] | agent=Claude_Code vs OpenAI_Codex | -0.33 | 0.72 | 0.44 | 1.18 | 0.19 | 23798 | 7.07 | 6579.54 |
| human_account_linked | has_human_review | C(agent, Treatment(reference='OpenAI_Codex'))[T.Cursor] | agent=Cursor vs OpenAI_Codex | 0.59 | 1.80 | 1.12 | 2.88 | 0.02 | 23798 | 7.07 | 6579.54 |
| human_account_linked | has_human_review | account_age_z | account age, per SD | 0.22 | 1.24 | 1.04 | 1.49 | 0.02 | 23798 | 7.07 | 6579.54 |
| human_account_linked | has_human_review | log_followers_z | followers, log1p per SD | -0.31 | 0.73 | 0.61 | 0.88 | 0.00 | 23798 | 7.07 | 6579.54 |
| human_account_linked | has_human_review | log_prior_repo_prs_z | prior observed author-repo PRs, log1p per SD | -1.21 | 0.30 | 0.17 | 0.54 | 0.00 | 23798 | 7.07 | 6579.54 |
| human_account_linked | has_human_review | prior_repo_merge_rate_z | prior observed author-repo merge rate, per SD | 0.07 | 1.07 | 0.90 | 1.27 | 0.43 | 23798 | 7.07 | 6579.54 |
| human_account_linked | has_human_review | log_timeline_commits_z | timeline commits, log1p per SD | -0.50 | 0.60 | 0.52 | 0.70 | 0.00 | 23798 | 7.07 | 6579.54 |
| human_account_linked | has_human_review | log_timeline_events_z | timeline events, log1p per SD | 1.57 | 4.80 | 3.66 | 6.30 | 0.00 | 23798 | 7.07 | 6579.54 |
| human_account_linked | has_human_review | log_timeline_force_pushes_z | timeline force pushes, log1p per SD | -0.02 | 0.98 | 0.91 | 1.05 | 0.58 | 23798 | 7.07 | 6579.54 |
| human_account_linked | has_approval | C(agent, Treatment(reference='OpenAI_Codex'))[T.Claude_Code] | agent=Claude_Code vs OpenAI_Codex | -0.48 | 0.62 | 0.35 | 1.09 | 0.10 | 23798 | 5.20 | 5148.79 |
| human_account_linked | has_approval | C(agent, Treatment(reference='OpenAI_Codex'))[T.Cursor] | agent=Cursor vs OpenAI_Codex | 0.54 | 1.71 | 1.06 | 2.76 | 0.03 | 23798 | 5.20 | 5148.79 |
| human_account_linked | has_approval | account_age_z | account age, per SD | 0.15 | 1.16 | 0.95 | 1.43 | 0.15 | 23798 | 5.20 | 5148.79 |
| human_account_linked | has_approval | log_followers_z | followers, log1p per SD | -0.29 | 0.74 | 0.64 | 0.86 | 0.00 | 23798 | 5.20 | 5148.79 |
| human_account_linked | has_approval | log_prior_repo_prs_z | prior observed author-repo PRs, log1p per SD | -1.24 | 0.29 | 0.16 | 0.53 | 0.00 | 23798 | 5.20 | 5148.79 |
| human_account_linked | has_approval | prior_repo_merge_rate_z | prior observed author-repo merge rate, per SD | 0.05 | 1.05 | 0.92 | 1.19 | 0.49 | 23798 | 5.20 | 5148.79 |
| human_account_linked | has_approval | log_timeline_commits_z | timeline commits, log1p per SD | -0.54 | 0.58 | 0.50 | 0.67 | 0.00 | 23798 | 5.20 | 5148.79 |
| human_account_linked | has_approval | log_timeline_events_z | timeline events, log1p per SD | 1.57 | 4.78 | 3.57 | 6.41 | 0.00 | 23798 | 5.20 | 5148.79 |
| human_account_linked | has_approval | log_timeline_force_pushes_z | timeline force pushes, log1p per SD | -0.06 | 0.94 | 0.87 | 1.01 | 0.10 | 23798 | 5.20 | 5148.79 |
| human_account_linked | has_changes_requested | C(agent, Treatment(reference='OpenAI_Codex'))[T.Claude_Code] | agent=Claude_Code vs OpenAI_Codex | -0.39 | 0.68 | 0.26 | 1.77 | 0.43 | 23798 | 0.38 | 864.08 |
| human_account_linked | has_changes_requested | C(agent, Treatment(reference='OpenAI_Codex'))[T.Cursor] | agent=Cursor vs OpenAI_Codex | -0.06 | 0.94 | 0.42 | 2.12 | 0.88 | 23798 | 0.38 | 864.08 |
| human_account_linked | has_changes_requested | account_age_z | account age, per SD | -0.01 | 0.99 | 0.81 | 1.23 | 0.96 | 23798 | 0.38 | 864.08 |
| human_account_linked | has_changes_requested | log_followers_z | followers, log1p per SD | -0.28 | 0.75 | 0.62 | 0.91 | 0.00 | 23798 | 0.38 | 864.08 |
| human_account_linked | has_changes_requested | log_prior_repo_prs_z | prior observed author-repo PRs, log1p per SD | -0.46 | 0.63 | 0.26 | 1.50 | 0.30 | 23798 | 0.38 | 864.08 |
| human_account_linked | has_changes_requested | prior_repo_merge_rate_z | prior observed author-repo merge rate, per SD | -0.04 | 0.96 | 0.73 | 1.26 | 0.78 | 23798 | 0.38 | 864.08 |
| human_account_linked | has_changes_requested | log_timeline_commits_z | timeline commits, log1p per SD | -0.01 | 0.99 | 0.86 | 1.14 | 0.89 | 23798 | 0.38 | 864.08 |
| human_account_linked | has_changes_requested | log_timeline_events_z | timeline events, log1p per SD | 0.99 | 2.70 | 1.97 | 3.70 | 0.00 | 23798 | 0.38 | 864.08 |
| human_account_linked | has_changes_requested | log_timeline_force_pushes_z | timeline force pushes, log1p per SD | 0.06 | 1.06 | 0.99 | 1.14 | 0.12 | 23798 | 0.38 | 864.08 |
| human_account_linked | has_human_discussion | C(agent, Treatment(reference='OpenAI_Codex'))[T.Claude_Code] | agent=Claude_Code vs OpenAI_Codex | 0.54 | 1.72 | 1.14 | 2.59 | 0.01 | 23798 | 11.55 | 8783.20 |
| human_account_linked | has_human_discussion | C(agent, Treatment(reference='OpenAI_Codex'))[T.Cursor] | agent=Cursor vs OpenAI_Codex | 0.37 | 1.44 | 0.90 | 2.30 | 0.13 | 23798 | 11.55 | 8783.20 |
| human_account_linked | has_human_discussion | account_age_z | account age, per SD | 0.19 | 1.20 | 1.01 | 1.43 | 0.04 | 23798 | 11.55 | 8783.20 |
| human_account_linked | has_human_discussion | log_followers_z | followers, log1p per SD | -0.17 | 0.84 | 0.71 | 1.00 | 0.05 | 23798 | 11.55 | 8783.20 |
| human_account_linked | has_human_discussion | log_prior_repo_prs_z | prior observed author-repo PRs, log1p per SD | -1.17 | 0.31 | 0.17 | 0.55 | 0.00 | 23798 | 11.55 | 8783.20 |
| human_account_linked | has_human_discussion | prior_repo_merge_rate_z | prior observed author-repo merge rate, per SD | -0.12 | 0.89 | 0.75 | 1.05 | 0.18 | 23798 | 11.55 | 8783.20 |
| human_account_linked | has_human_discussion | log_timeline_commits_z | timeline commits, log1p per SD | -0.54 | 0.58 | 0.51 | 0.67 | 0.00 | 23798 | 11.55 | 8783.20 |
| human_account_linked | has_human_discussion | log_timeline_events_z | timeline events, log1p per SD | 1.52 | 4.59 | 3.59 | 5.89 | 0.00 | 23798 | 11.55 | 8783.20 |
| human_account_linked | has_human_discussion | log_timeline_force_pushes_z | timeline force pushes, log1p per SD | -0.06 | 0.94 | 0.88 | 1.02 | 0.13 | 23798 | 11.55 | 8783.20 |
| human_account_linked_closed_only | merged | C(agent, Treatment(reference='OpenAI_Codex'))[T.Claude_Code] | agent=Claude_Code vs OpenAI_Codex | 0.35 | 1.42 | 0.69 | 2.96 | 0.34 | 22719 | 84.86 | 14455.87 |
| human_account_linked_closed_only | merged | C(agent, Treatment(reference='OpenAI_Codex'))[T.Cursor] | agent=Cursor vs OpenAI_Codex | 0.17 | 1.18 | 0.70 | 2.00 | 0.53 | 22719 | 84.86 | 14455.87 |
| human_account_linked_closed_only | merged | account_age_z | account age, per SD | -0.23 | 0.79 | 0.63 | 1.00 | 0.05 | 22719 | 84.86 | 14455.87 |
| human_account_linked_closed_only | merged | log_followers_z | followers, log1p per SD | 0.28 | 1.32 | 1.08 | 1.62 | 0.01 | 22719 | 84.86 | 14455.87 |
| human_account_linked_closed_only | merged | log_prior_repo_prs_z | prior observed author-repo PRs, log1p per SD | 0.22 | 1.24 | 0.86 | 1.78 | 0.24 | 22719 | 84.86 | 14455.87 |
| human_account_linked_closed_only | merged | prior_repo_merge_rate_z | prior observed author-repo merge rate, per SD | 0.49 | 1.63 | 1.36 | 1.96 | 0.00 | 22719 | 84.86 | 14455.87 |
| human_account_linked_closed_only | merged | log_timeline_commits_z | timeline commits, log1p per SD | -1.14 | 0.32 | 0.07 | 1.53 | 0.15 | 22719 | 84.86 | 14455.87 |
| human_account_linked_closed_only | merged | log_timeline_events_z | timeline events, log1p per SD | 2.05 | 7.80 | 0.56 | 108.07 | 0.13 | 22719 | 84.86 | 14455.87 |
| human_account_linked_closed_only | merged | log_timeline_force_pushes_z | timeline force pushes, log1p per SD | -0.17 | 0.84 | 0.60 | 1.18 | 0.32 | 22719 | 84.86 | 14455.87 |
| human_account_linked_no_extreme_pairs | has_human_review | C(agent, Treatment(reference='OpenAI_Codex'))[T.Claude_Code] | agent=Claude_Code vs OpenAI_Codex | -0.22 | 0.80 | 0.52 | 1.24 | 0.32 | 8664 | 16.49 | 5159.89 |
| human_account_linked_no_extreme_pairs | has_human_review | C(agent, Treatment(reference='OpenAI_Codex'))[T.Cursor] | agent=Cursor vs OpenAI_Codex | 0.61 | 1.84 | 1.21 | 2.81 | 0.00 | 8664 | 16.49 | 5159.89 |
| human_account_linked_no_extreme_pairs | has_human_review | account_age_z | account age, per SD | 0.14 | 1.15 | 0.95 | 1.39 | 0.14 | 8664 | 16.49 | 5159.89 |
| human_account_linked_no_extreme_pairs | has_human_review | log_followers_z | followers, log1p per SD | -0.34 | 0.71 | 0.60 | 0.84 | 0.00 | 8664 | 16.49 | 5159.89 |
| human_account_linked_no_extreme_pairs | has_human_review | log_prior_repo_prs_z | prior observed author-repo PRs, log1p per SD | -0.46 | 0.63 | 0.50 | 0.79 | 0.00 | 8664 | 16.49 | 5159.89 |
| human_account_linked_no_extreme_pairs | has_human_review | prior_repo_merge_rate_z | prior observed author-repo merge rate, per SD | 0.00 | 1.00 | 0.86 | 1.18 | 0.97 | 8664 | 16.49 | 5159.89 |
| human_account_linked_no_extreme_pairs | has_human_review | log_timeline_commits_z | timeline commits, log1p per SD | -0.70 | 0.50 | 0.42 | 0.59 | 0.00 | 8664 | 16.49 | 5159.89 |
| human_account_linked_no_extreme_pairs | has_human_review | log_timeline_events_z | timeline events, log1p per SD | 1.96 | 7.09 | 5.23 | 9.63 | 0.00 | 8664 | 16.49 | 5159.89 |
| human_account_linked_no_extreme_pairs | has_human_review | log_timeline_force_pushes_z | timeline force pushes, log1p per SD | -0.01 | 0.99 | 0.89 | 1.10 | 0.82 | 8664 | 16.49 | 5159.89 |
| human_account_linked_no_extreme_pairs | has_approval | C(agent, Treatment(reference='OpenAI_Codex'))[T.Claude_Code] | agent=Claude_Code vs OpenAI_Codex | -0.40 | 0.67 | 0.39 | 1.14 | 0.14 | 8664 | 12.94 | 4461.74 |
| human_account_linked_no_extreme_pairs | has_approval | C(agent, Treatment(reference='OpenAI_Codex'))[T.Cursor] | agent=Cursor vs OpenAI_Codex | 0.69 | 1.99 | 1.25 | 3.17 | 0.00 | 8664 | 12.94 | 4461.74 |
| human_account_linked_no_extreme_pairs | has_approval | account_age_z | account age, per SD | 0.09 | 1.10 | 0.88 | 1.37 | 0.41 | 8664 | 12.94 | 4461.74 |
| human_account_linked_no_extreme_pairs | has_approval | log_followers_z | followers, log1p per SD | -0.40 | 0.67 | 0.56 | 0.81 | 0.00 | 8664 | 12.94 | 4461.74 |
| human_account_linked_no_extreme_pairs | has_approval | log_prior_repo_prs_z | prior observed author-repo PRs, log1p per SD | -0.51 | 0.60 | 0.45 | 0.80 | 0.00 | 8664 | 12.94 | 4461.74 |
| human_account_linked_no_extreme_pairs | has_approval | prior_repo_merge_rate_z | prior observed author-repo merge rate, per SD | 0.07 | 1.07 | 0.91 | 1.27 | 0.42 | 8664 | 12.94 | 4461.74 |
| human_account_linked_no_extreme_pairs | has_approval | log_timeline_commits_z | timeline commits, log1p per SD | -0.80 | 0.45 | 0.38 | 0.53 | 0.00 | 8664 | 12.94 | 4461.74 |
| human_account_linked_no_extreme_pairs | has_approval | log_timeline_events_z | timeline events, log1p per SD | 2.01 | 7.46 | 5.30 | 10.51 | 0.00 | 8664 | 12.94 | 4461.74 |
| human_account_linked_no_extreme_pairs | has_approval | log_timeline_force_pushes_z | timeline force pushes, log1p per SD | -0.10 | 0.90 | 0.80 | 1.01 | 0.09 | 8664 | 12.94 | 4461.74 |
| human_account_linked_no_extreme_pairs | has_changes_requested | C(agent, Treatment(reference='OpenAI_Codex'))[T.Claude_Code] | agent=Claude_Code vs OpenAI_Codex | -0.32 | 0.72 | 0.27 | 1.93 | 0.52 | 8664 | 0.97 | 786.45 |
| human_account_linked_no_extreme_pairs | has_changes_requested | C(agent, Treatment(reference='OpenAI_Codex'))[T.Cursor] | agent=Cursor vs OpenAI_Codex | -0.14 | 0.87 | 0.37 | 2.00 | 0.74 | 8664 | 0.97 | 786.45 |
| human_account_linked_no_extreme_pairs | has_changes_requested | account_age_z | account age, per SD | -0.06 | 0.94 | 0.73 | 1.22 | 0.64 | 8664 | 0.97 | 786.45 |
| human_account_linked_no_extreme_pairs | has_changes_requested | log_followers_z | followers, log1p per SD | -0.48 | 0.62 | 0.47 | 0.81 | 0.00 | 8664 | 0.97 | 786.45 |
| human_account_linked_no_extreme_pairs | has_changes_requested | log_prior_repo_prs_z | prior observed author-repo PRs, log1p per SD | -0.17 | 0.84 | 0.59 | 1.20 | 0.34 | 8664 | 0.97 | 786.45 |
| human_account_linked_no_extreme_pairs | has_changes_requested | prior_repo_merge_rate_z | prior observed author-repo merge rate, per SD | 0.01 | 1.01 | 0.74 | 1.38 | 0.95 | 8664 | 0.97 | 786.45 |
| human_account_linked_no_extreme_pairs | has_changes_requested | log_timeline_commits_z | timeline commits, log1p per SD | -0.02 | 0.98 | 0.81 | 1.20 | 0.87 | 8664 | 0.97 | 786.45 |
| human_account_linked_no_extreme_pairs | has_changes_requested | log_timeline_events_z | timeline events, log1p per SD | 1.15 | 3.15 | 2.19 | 4.54 | 0.00 | 8664 | 0.97 | 786.45 |
| human_account_linked_no_extreme_pairs | has_changes_requested | log_timeline_force_pushes_z | timeline force pushes, log1p per SD | 0.11 | 1.11 | 0.98 | 1.26 | 0.09 | 8664 | 0.97 | 786.45 |
| human_account_linked_no_extreme_pairs | has_human_discussion | C(agent, Treatment(reference='OpenAI_Codex'))[T.Claude_Code] | agent=Claude_Code vs OpenAI_Codex | 0.59 | 1.81 | 1.24 | 2.63 | 0.00 | 8664 | 27.40 | 7061.63 |
| human_account_linked_no_extreme_pairs | has_human_discussion | C(agent, Treatment(reference='OpenAI_Codex'))[T.Cursor] | agent=Cursor vs OpenAI_Codex | 0.38 | 1.46 | 0.95 | 2.26 | 0.09 | 8664 | 27.40 | 7061.63 |
| human_account_linked_no_extreme_pairs | has_human_discussion | account_age_z | account age, per SD | 0.11 | 1.11 | 0.94 | 1.32 | 0.23 | 8664 | 27.40 | 7061.63 |
| human_account_linked_no_extreme_pairs | has_human_discussion | log_followers_z | followers, log1p per SD | -0.25 | 0.78 | 0.65 | 0.93 | 0.01 | 8664 | 27.40 | 7061.63 |
| human_account_linked_no_extreme_pairs | has_human_discussion | log_prior_repo_prs_z | prior observed author-repo PRs, log1p per SD | -0.29 | 0.75 | 0.63 | 0.90 | 0.00 | 8664 | 27.40 | 7061.63 |
| human_account_linked_no_extreme_pairs | has_human_discussion | prior_repo_merge_rate_z | prior observed author-repo merge rate, per SD | -0.24 | 0.79 | 0.69 | 0.91 | 0.00 | 8664 | 27.40 | 7061.63 |
| human_account_linked_no_extreme_pairs | has_human_discussion | log_timeline_commits_z | timeline commits, log1p per SD | -0.71 | 0.49 | 0.42 | 0.57 | 0.00 | 8664 | 27.40 | 7061.63 |
| human_account_linked_no_extreme_pairs | has_human_discussion | log_timeline_events_z | timeline events, log1p per SD | 1.83 | 6.22 | 4.77 | 8.12 | 0.00 | 8664 | 27.40 | 7061.63 |
| human_account_linked_no_extreme_pairs | has_human_discussion | log_timeline_force_pushes_z | timeline force pushes, log1p per SD | -0.05 | 0.95 | 0.85 | 1.06 | 0.32 | 8664 | 27.40 | 7061.63 |
| human_account_linked_no_extreme_pairs_closed_only | merged | C(agent, Treatment(reference='OpenAI_Codex'))[T.Claude_Code] | agent=Claude_Code vs OpenAI_Codex | -0.04 | 0.96 | 0.64 | 1.43 | 0.83 | 7823 | 76.51 | 7218.20 |
| human_account_linked_no_extreme_pairs_closed_only | merged | C(agent, Treatment(reference='OpenAI_Codex'))[T.Cursor] | agent=Cursor vs OpenAI_Codex | -0.06 | 0.94 | 0.72 | 1.23 | 0.68 | 7823 | 76.51 | 7218.20 |
| human_account_linked_no_extreme_pairs_closed_only | merged | account_age_z | account age, per SD | -0.03 | 0.97 | 0.86 | 1.08 | 0.57 | 7823 | 76.51 | 7218.20 |
| human_account_linked_no_extreme_pairs_closed_only | merged | log_followers_z | followers, log1p per SD | 0.34 | 1.41 | 1.27 | 1.56 | 0.00 | 7823 | 76.51 | 7218.20 |
| human_account_linked_no_extreme_pairs_closed_only | merged | log_prior_repo_prs_z | prior observed author-repo PRs, log1p per SD | -0.23 | 0.80 | 0.69 | 0.92 | 0.00 | 7823 | 76.51 | 7218.20 |
| human_account_linked_no_extreme_pairs_closed_only | merged | prior_repo_merge_rate_z | prior observed author-repo merge rate, per SD | 0.60 | 1.83 | 1.64 | 2.03 | 0.00 | 7823 | 76.51 | 7218.20 |
| human_account_linked_no_extreme_pairs_closed_only | merged | log_timeline_commits_z | timeline commits, log1p per SD | -0.51 | 0.60 | 0.49 | 0.74 | 0.00 | 7823 | 76.51 | 7218.20 |
| human_account_linked_no_extreme_pairs_closed_only | merged | log_timeline_events_z | timeline events, log1p per SD | 1.01 | 2.74 | 2.09 | 3.57 | 0.00 | 7823 | 76.51 | 7218.20 |
| human_account_linked_no_extreme_pairs_closed_only | merged | log_timeline_force_pushes_z | timeline force pushes, log1p per SD | -0.03 | 0.97 | 0.87 | 1.09 | 0.65 | 7823 | 76.51 | 7218.20 |

Model run metadata:

| sample | outcome | n | event_rate_pct | aic | status |
| --- | --- | --- | --- | --- | --- |
| all_valid_accounts | has_human_review | 28625 | 12.09 | 11315.16 | ok |
| all_valid_accounts | has_approval | 28625 | 9.10 | 9561.88 | ok |
| all_valid_accounts | has_changes_requested | 28625 | 1.10 | 2466.39 | ok |
| all_valid_accounts | has_human_discussion | 28625 | 18.19 | 14246.90 | ok |
| all_valid_accounts_closed_only | merged | 27392 | 79.86 | 20229.73 | ok |
| all_valid_accounts_no_extreme_pairs | has_human_review | 11468 | 21.15 | 8183.15 | ok |
| all_valid_accounts_no_extreme_pairs | has_approval | 11468 | 16.19 | 7270.45 | ok |
| all_valid_accounts_no_extreme_pairs | has_changes_requested | 11468 | 2.31 | 1992.56 | ok |
| all_valid_accounts_no_extreme_pairs | has_human_discussion | 11468 | 32.05 | 10179.02 | ok |
| all_valid_accounts_no_extreme_pairs_closed_only | merged | 10528 | 70.53 | 10494.63 | ok |
| human_account_linked | has_human_review | 23798 | 7.07 | 6579.54 | ok |
| human_account_linked | has_approval | 23798 | 5.20 | 5148.79 | ok |
| human_account_linked | has_changes_requested | 23798 | 0.38 | 864.08 | ok |
| human_account_linked | has_human_discussion | 23798 | 11.55 | 8783.20 | ok |
| human_account_linked_closed_only | merged | 22719 | 84.86 | 14455.87 | ok |
| human_account_linked_no_extreme_pairs | has_human_review | 8664 | 16.49 | 5159.89 | ok |
| human_account_linked_no_extreme_pairs | has_approval | 8664 | 12.94 | 4461.74 | ok |
| human_account_linked_no_extreme_pairs | has_changes_requested | 8664 | 0.97 | 786.45 | ok |
| human_account_linked_no_extreme_pairs | has_human_discussion | 8664 | 27.40 | 7061.63 | ok |
| human_account_linked_no_extreme_pairs_closed_only | merged | 7823 | 76.51 | 7218.20 | ok |

## GitHub-Enriched Churn and Author Association Models

These models use only PRs successfully enriched from the GitHub API, adding true additions/deletions, changed files, commit count, and GitHub author association.

| sample | outcome | term | effect | coef_log_odds | odds_ratio | ci_low | ci_high | p_value | n | event_rate_pct | aic |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| github_enriched_human_account_linked_no_extreme_pairs | has_human_review | C(agent, Treatment(reference='OpenAI_Codex'))[T.Claude_Code] | agent=Claude_Code vs OpenAI_Codex | 0.12 | 1.13 | 0.46 | 2.79 | 0.79 | 2003 | 16.53 | 1489.87 |
| github_enriched_human_account_linked_no_extreme_pairs | has_human_review | C(agent, Treatment(reference='OpenAI_Codex'))[T.Cursor] | agent=Cursor vs OpenAI_Codex | 0.59 | 1.81 | 1.00 | 3.27 | 0.05 | 2003 | 16.53 | 1489.87 |
| github_enriched_human_account_linked_no_extreme_pairs | has_human_review | C(author_association, Treatment(reference='CONTRIBUTOR'))[T.COLLABORATOR] | author_association=COLLABORATOR vs CONTRIBUTOR | -0.76 | 0.47 | 0.26 | 0.85 | 0.01 | 2003 | 16.53 | 1489.87 |
| github_enriched_human_account_linked_no_extreme_pairs | has_human_review | C(author_association, Treatment(reference='CONTRIBUTOR'))[T.MEMBER] | author_association=MEMBER vs CONTRIBUTOR | -0.25 | 0.78 | 0.47 | 1.28 | 0.32 | 2003 | 16.53 | 1489.87 |
| github_enriched_human_account_linked_no_extreme_pairs | has_human_review | C(author_association, Treatment(reference='CONTRIBUTOR'))[T.NONE] | author_association=NONE vs CONTRIBUTOR | -3.83 | 0.02 | 0.00 | 0.15 | 0.00 | 2003 | 16.53 | 1489.87 |
| github_enriched_human_account_linked_no_extreme_pairs | has_human_review | C(author_association, Treatment(reference='CONTRIBUTOR'))[T.OWNER] | author_association=OWNER vs CONTRIBUTOR | -2.94 | 0.05 | 0.03 | 0.11 | 0.00 | 2003 | 16.53 | 1489.87 |
| github_enriched_human_account_linked_no_extreme_pairs | has_human_review | account_age_z | account age, per SD | -0.05 | 0.95 | 0.74 | 1.22 | 0.68 | 2003 | 16.53 | 1489.87 |
| github_enriched_human_account_linked_no_extreme_pairs | has_human_review | log_followers_z | followers, log1p per SD | -0.19 | 0.83 | 0.65 | 1.06 | 0.14 | 2003 | 16.53 | 1489.87 |
| github_enriched_human_account_linked_no_extreme_pairs | has_human_review | log_github_total_churn_z | GitHub total churn, log1p per SD | -0.47 | 0.63 | 0.49 | 0.80 | 0.00 | 2003 | 16.53 | 1489.87 |
| github_enriched_human_account_linked_no_extreme_pairs | has_human_review | log_github_changed_files_z | GitHub changed files, log1p per SD | 0.14 | 1.15 | 0.91 | 1.44 | 0.24 | 2003 | 16.53 | 1489.87 |
| github_enriched_human_account_linked_no_extreme_pairs | has_human_review | log_github_commits_z | GitHub commits, log1p per SD | 0.66 | 1.93 | 1.55 | 2.39 | 0.00 | 2003 | 16.53 | 1489.87 |
| github_enriched_human_account_linked_no_extreme_pairs | has_approval | C(agent, Treatment(reference='OpenAI_Codex'))[T.Claude_Code] | agent=Claude_Code vs OpenAI_Codex | 0.25 | 1.28 | 0.51 | 3.19 | 0.60 | 2003 | 13.13 | 1298.82 |
| github_enriched_human_account_linked_no_extreme_pairs | has_approval | C(agent, Treatment(reference='OpenAI_Codex'))[T.Cursor] | agent=Cursor vs OpenAI_Codex | 0.58 | 1.79 | 0.96 | 3.35 | 0.07 | 2003 | 13.13 | 1298.82 |
| github_enriched_human_account_linked_no_extreme_pairs | has_approval | C(author_association, Treatment(reference='CONTRIBUTOR'))[T.COLLABORATOR] | author_association=COLLABORATOR vs CONTRIBUTOR | -0.71 | 0.49 | 0.26 | 0.94 | 0.03 | 2003 | 13.13 | 1298.82 |
| github_enriched_human_account_linked_no_extreme_pairs | has_approval | C(author_association, Treatment(reference='CONTRIBUTOR'))[T.MEMBER] | author_association=MEMBER vs CONTRIBUTOR | -0.28 | 0.75 | 0.44 | 1.29 | 0.31 | 2003 | 13.13 | 1298.82 |
| github_enriched_human_account_linked_no_extreme_pairs | has_approval | C(author_association, Treatment(reference='CONTRIBUTOR'))[T.NONE] | author_association=NONE vs CONTRIBUTOR | -3.22 | 0.04 | 0.01 | 0.21 | 0.00 | 2003 | 13.13 | 1298.82 |
| github_enriched_human_account_linked_no_extreme_pairs | has_approval | C(author_association, Treatment(reference='CONTRIBUTOR'))[T.OWNER] | author_association=OWNER vs CONTRIBUTOR | -4.43 | 0.01 | 0.00 | 0.05 | 0.00 | 2003 | 13.13 | 1298.82 |
| github_enriched_human_account_linked_no_extreme_pairs | has_approval | account_age_z | account age, per SD | -0.08 | 0.93 | 0.70 | 1.22 | 0.58 | 2003 | 13.13 | 1298.82 |
| github_enriched_human_account_linked_no_extreme_pairs | has_approval | log_followers_z | followers, log1p per SD | -0.24 | 0.79 | 0.60 | 1.03 | 0.08 | 2003 | 13.13 | 1298.82 |
| github_enriched_human_account_linked_no_extreme_pairs | has_approval | log_github_total_churn_z | GitHub total churn, log1p per SD | -0.42 | 0.66 | 0.52 | 0.84 | 0.00 | 2003 | 13.13 | 1298.82 |
| github_enriched_human_account_linked_no_extreme_pairs | has_approval | log_github_changed_files_z | GitHub changed files, log1p per SD | 0.09 | 1.09 | 0.87 | 1.37 | 0.45 | 2003 | 13.13 | 1298.82 |
| github_enriched_human_account_linked_no_extreme_pairs | has_approval | log_github_commits_z | GitHub commits, log1p per SD | 0.43 | 1.54 | 1.26 | 1.88 | 0.00 | 2003 | 13.13 | 1298.82 |
| github_enriched_human_account_linked_no_extreme_pairs | has_changes_requested | C(agent, Treatment(reference='OpenAI_Codex'))[T.Claude_Code] | agent=Claude_Code vs OpenAI_Codex | 0.40 | 1.49 | 0.29 | 7.65 | 0.64 | 2003 | 0.70 | 159.20 |
| github_enriched_human_account_linked_no_extreme_pairs | has_changes_requested | C(agent, Treatment(reference='OpenAI_Codex'))[T.Cursor] | agent=Cursor vs OpenAI_Codex | -23.17 | 0.00 | 0.00 | inf | 1.00 | 2003 | 0.70 | 159.20 |
| github_enriched_human_account_linked_no_extreme_pairs | has_changes_requested | C(author_association, Treatment(reference='CONTRIBUTOR'))[T.COLLABORATOR] | author_association=COLLABORATOR vs CONTRIBUTOR | -0.49 | 0.61 | 0.12 | 3.19 | 0.56 | 2003 | 0.70 | 159.20 |
| github_enriched_human_account_linked_no_extreme_pairs | has_changes_requested | C(author_association, Treatment(reference='CONTRIBUTOR'))[T.MEMBER] | author_association=MEMBER vs CONTRIBUTOR | 0.71 | 2.03 | 0.54 | 7.63 | 0.29 | 2003 | 0.70 | 159.20 |
| github_enriched_human_account_linked_no_extreme_pairs | has_changes_requested | C(author_association, Treatment(reference='CONTRIBUTOR'))[T.NONE] | author_association=NONE vs CONTRIBUTOR | -23.92 | 0.00 | 0.00 | inf | 1.00 | 2003 | 0.70 | 159.20 |
| github_enriched_human_account_linked_no_extreme_pairs | has_changes_requested | C(author_association, Treatment(reference='CONTRIBUTOR'))[T.OWNER] | author_association=OWNER vs CONTRIBUTOR | -22.46 | 0.00 | 0.00 | inf | 1.00 | 2003 | 0.70 | 159.20 |
| github_enriched_human_account_linked_no_extreme_pairs | has_changes_requested | account_age_z | account age, per SD | -0.40 | 0.67 | 0.39 | 1.13 | 0.13 | 2003 | 0.70 | 159.20 |
| github_enriched_human_account_linked_no_extreme_pairs | has_changes_requested | log_followers_z | followers, log1p per SD | -0.16 | 0.86 | 0.69 | 1.07 | 0.16 | 2003 | 0.70 | 159.20 |
| github_enriched_human_account_linked_no_extreme_pairs | has_changes_requested | log_github_total_churn_z | GitHub total churn, log1p per SD | -0.63 | 0.53 | 0.35 | 0.81 | 0.00 | 2003 | 0.70 | 159.20 |
| github_enriched_human_account_linked_no_extreme_pairs | has_changes_requested | log_github_changed_files_z | GitHub changed files, log1p per SD | 0.21 | 1.23 | 0.75 | 2.04 | 0.41 | 2003 | 0.70 | 159.20 |
| github_enriched_human_account_linked_no_extreme_pairs | has_changes_requested | log_github_commits_z | GitHub commits, log1p per SD | 0.82 | 2.26 | 1.67 | 3.05 | 0.00 | 2003 | 0.70 | 159.20 |
| github_enriched_human_account_linked_no_extreme_pairs | has_human_discussion | C(agent, Treatment(reference='OpenAI_Codex'))[T.Claude_Code] | agent=Claude_Code vs OpenAI_Codex | 0.71 | 2.04 | 0.92 | 4.53 | 0.08 | 2003 | 28.16 | 2034.28 |
| github_enriched_human_account_linked_no_extreme_pairs | has_human_discussion | C(agent, Treatment(reference='OpenAI_Codex'))[T.Cursor] | agent=Cursor vs OpenAI_Codex | 0.32 | 1.37 | 0.77 | 2.46 | 0.29 | 2003 | 28.16 | 2034.28 |
| github_enriched_human_account_linked_no_extreme_pairs | has_human_discussion | C(author_association, Treatment(reference='CONTRIBUTOR'))[T.COLLABORATOR] | author_association=COLLABORATOR vs CONTRIBUTOR | -0.96 | 0.38 | 0.22 | 0.67 | 0.00 | 2003 | 28.16 | 2034.28 |
| github_enriched_human_account_linked_no_extreme_pairs | has_human_discussion | C(author_association, Treatment(reference='CONTRIBUTOR'))[T.MEMBER] | author_association=MEMBER vs CONTRIBUTOR | -0.44 | 0.64 | 0.37 | 1.12 | 0.12 | 2003 | 28.16 | 2034.28 |
| github_enriched_human_account_linked_no_extreme_pairs | has_human_discussion | C(author_association, Treatment(reference='CONTRIBUTOR'))[T.NONE] | author_association=NONE vs CONTRIBUTOR | -1.29 | 0.27 | 0.13 | 0.59 | 0.00 | 2003 | 28.16 | 2034.28 |
| github_enriched_human_account_linked_no_extreme_pairs | has_human_discussion | C(author_association, Treatment(reference='CONTRIBUTOR'))[T.OWNER] | author_association=OWNER vs CONTRIBUTOR | -2.20 | 0.11 | 0.06 | 0.20 | 0.00 | 2003 | 28.16 | 2034.28 |
| github_enriched_human_account_linked_no_extreme_pairs | has_human_discussion | account_age_z | account age, per SD | -0.03 | 0.97 | 0.78 | 1.21 | 0.77 | 2003 | 28.16 | 2034.28 |
| github_enriched_human_account_linked_no_extreme_pairs | has_human_discussion | log_followers_z | followers, log1p per SD | -0.03 | 0.97 | 0.75 | 1.24 | 0.78 | 2003 | 28.16 | 2034.28 |
| github_enriched_human_account_linked_no_extreme_pairs | has_human_discussion | log_github_total_churn_z | GitHub total churn, log1p per SD | -0.25 | 0.78 | 0.63 | 0.96 | 0.02 | 2003 | 28.16 | 2034.28 |
| github_enriched_human_account_linked_no_extreme_pairs | has_human_discussion | log_github_changed_files_z | GitHub changed files, log1p per SD | 0.11 | 1.12 | 0.91 | 1.37 | 0.28 | 2003 | 28.16 | 2034.28 |
| github_enriched_human_account_linked_no_extreme_pairs | has_human_discussion | log_github_commits_z | GitHub commits, log1p per SD | 0.55 | 1.73 | 1.45 | 2.07 | 0.00 | 2003 | 28.16 | 2034.28 |
| github_enriched_human_account_linked_no_extreme_pairs_closed_only | merged | C(agent, Treatment(reference='OpenAI_Codex'))[T.Claude_Code] | agent=Claude_Code vs OpenAI_Codex | 0.63 | 1.87 | 0.85 | 4.16 | 0.12 | 1818 | 76.29 | 1799.57 |
| github_enriched_human_account_linked_no_extreme_pairs_closed_only | merged | C(agent, Treatment(reference='OpenAI_Codex'))[T.Cursor] | agent=Cursor vs OpenAI_Codex | 0.07 | 1.07 | 0.64 | 1.78 | 0.79 | 1818 | 76.29 | 1799.57 |
| github_enriched_human_account_linked_no_extreme_pairs_closed_only | merged | C(author_association, Treatment(reference='CONTRIBUTOR'))[T.COLLABORATOR] | author_association=COLLABORATOR vs CONTRIBUTOR | 0.39 | 1.48 | 0.92 | 2.40 | 0.11 | 1818 | 76.29 | 1799.57 |
| github_enriched_human_account_linked_no_extreme_pairs_closed_only | merged | C(author_association, Treatment(reference='CONTRIBUTOR'))[T.MEMBER] | author_association=MEMBER vs CONTRIBUTOR | 0.37 | 1.45 | 0.96 | 2.20 | 0.08 | 1818 | 76.29 | 1799.57 |
| github_enriched_human_account_linked_no_extreme_pairs_closed_only | merged | C(author_association, Treatment(reference='CONTRIBUTOR'))[T.NONE] | author_association=NONE vs CONTRIBUTOR | -3.08 | 0.05 | 0.01 | 0.17 | 0.00 | 1818 | 76.29 | 1799.57 |
| github_enriched_human_account_linked_no_extreme_pairs_closed_only | merged | C(author_association, Treatment(reference='CONTRIBUTOR'))[T.OWNER] | author_association=OWNER vs CONTRIBUTOR | 0.90 | 2.45 | 1.62 | 3.71 | 0.00 | 1818 | 76.29 | 1799.57 |
| github_enriched_human_account_linked_no_extreme_pairs_closed_only | merged | account_age_z | account age, per SD | 0.12 | 1.13 | 0.92 | 1.40 | 0.25 | 1818 | 76.29 | 1799.57 |
| github_enriched_human_account_linked_no_extreme_pairs_closed_only | merged | log_followers_z | followers, log1p per SD | 0.16 | 1.17 | 0.97 | 1.42 | 0.10 | 1818 | 76.29 | 1799.57 |
| github_enriched_human_account_linked_no_extreme_pairs_closed_only | merged | log_github_total_churn_z | GitHub total churn, log1p per SD | -0.45 | 0.64 | 0.53 | 0.77 | 0.00 | 1818 | 76.29 | 1799.57 |
| github_enriched_human_account_linked_no_extreme_pairs_closed_only | merged | log_github_changed_files_z | GitHub changed files, log1p per SD | -0.02 | 0.98 | 0.83 | 1.16 | 0.80 | 1818 | 76.29 | 1799.57 |
| github_enriched_human_account_linked_no_extreme_pairs_closed_only | merged | log_github_commits_z | GitHub commits, log1p per SD | 0.26 | 1.29 | 1.08 | 1.55 | 0.01 | 1818 | 76.29 | 1799.57 |

GitHub-enriched model run metadata:

| sample | outcome | n | event_rate_pct | aic | status |
| --- | --- | --- | --- | --- | --- |
| github_enriched_human_account_linked_no_extreme_pairs | has_human_review | 2003 | 16.53 | 1489.87 | ok |
| github_enriched_human_account_linked_no_extreme_pairs | has_approval | 2003 | 13.13 | 1298.82 | ok |
| github_enriched_human_account_linked_no_extreme_pairs | has_changes_requested | 2003 | 0.70 | 159.20 | ok |
| github_enriched_human_account_linked_no_extreme_pairs | has_human_discussion | 2003 | 28.16 | 2034.28 | ok |
| github_enriched_human_account_linked_no_extreme_pairs_closed_only | merged | 1818 | 76.29 | 1799.57 | ok |

## Review Duration Models

Review duration is modeled as log1p hours to first human review among PRs that received a human review.

| sample | outcome | term | effect | coef_log_hours | duration_ratio | ci_low | ci_high | p_value | n | median_hours | aic |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| duration_human_account_linked_no_extreme_pairs | log_review_latency_hours | C(agent, Treatment(reference='OpenAI_Codex'))[T.Claude_Code] | agent=Claude_Code vs OpenAI_Codex | 0.21 | 1.23 | 0.77 | 1.97 | 0.38 | 1429 | 3.60 | 5748.50 |
| duration_human_account_linked_no_extreme_pairs | log_review_latency_hours | C(agent, Treatment(reference='OpenAI_Codex'))[T.Cursor] | agent=Cursor vs OpenAI_Codex | -0.20 | 0.81 | 0.59 | 1.12 | 0.21 | 1429 | 3.60 | 5748.50 |
| duration_human_account_linked_no_extreme_pairs | log_review_latency_hours | account_age_z | account age, per SD | 0.04 | 1.04 | 0.90 | 1.20 | 0.59 | 1429 | 3.60 | 5748.50 |
| duration_human_account_linked_no_extreme_pairs | log_review_latency_hours | log_followers_z | followers, log1p per SD | -0.17 | 0.84 | 0.73 | 0.97 | 0.02 | 1429 | 3.60 | 5748.50 |
| duration_human_account_linked_no_extreme_pairs | log_review_latency_hours | log_prior_repo_prs_z | prior observed author-repo PRs, log1p per SD | -0.09 | 0.91 | 0.73 | 1.14 | 0.43 | 1429 | 3.60 | 5748.50 |
| duration_human_account_linked_no_extreme_pairs | log_review_latency_hours | log_timeline_events_z | timeline events, log1p per SD | -0.01 | 0.99 | 0.84 | 1.15 | 0.86 | 1429 | 3.60 | 5748.50 |
| duration_github_enriched_human_account_linked_no_extreme_pairs | log_review_latency_hours | C(agent, Treatment(reference='OpenAI_Codex'))[T.Claude_Code] | agent=Claude_Code vs OpenAI_Codex | -0.29 | 0.75 | 0.34 | 1.64 | 0.47 | 331 | 3.46 | 1344.53 |
| duration_github_enriched_human_account_linked_no_extreme_pairs | log_review_latency_hours | C(agent, Treatment(reference='OpenAI_Codex'))[T.Cursor] | agent=Cursor vs OpenAI_Codex | -0.32 | 0.72 | 0.43 | 1.23 | 0.23 | 331 | 3.46 | 1344.53 |
| duration_github_enriched_human_account_linked_no_extreme_pairs | log_review_latency_hours | C(author_association, Treatment(reference='CONTRIBUTOR'))[T.COLLABORATOR] | author_association=COLLABORATOR vs CONTRIBUTOR | 0.41 | 1.51 | 0.78 | 2.93 | 0.22 | 331 | 3.46 | 1344.53 |
| duration_github_enriched_human_account_linked_no_extreme_pairs | log_review_latency_hours | C(author_association, Treatment(reference='CONTRIBUTOR'))[T.MEMBER] | author_association=MEMBER vs CONTRIBUTOR | -0.01 | 0.99 | 0.60 | 1.64 | 0.96 | 331 | 3.46 | 1344.53 |
| duration_github_enriched_human_account_linked_no_extreme_pairs | log_review_latency_hours | C(author_association, Treatment(reference='CONTRIBUTOR'))[T.NONE] | author_association=NONE vs CONTRIBUTOR | 2.06 | 7.83 | 2.55 | 24.09 | 0.00 | 331 | 3.46 | 1344.53 |
| duration_github_enriched_human_account_linked_no_extreme_pairs | log_review_latency_hours | C(author_association, Treatment(reference='CONTRIBUTOR'))[T.OWNER] | author_association=OWNER vs CONTRIBUTOR | 0.33 | 1.39 | 0.28 | 6.90 | 0.69 | 331 | 3.46 | 1344.53 |
| duration_github_enriched_human_account_linked_no_extreme_pairs | log_review_latency_hours | account_age_z | account age, per SD | -0.02 | 0.98 | 0.76 | 1.27 | 0.90 | 331 | 3.46 | 1344.53 |
| duration_github_enriched_human_account_linked_no_extreme_pairs | log_review_latency_hours | log_followers_z | followers, log1p per SD | -0.13 | 0.88 | 0.68 | 1.12 | 0.29 | 331 | 3.46 | 1344.53 |
| duration_github_enriched_human_account_linked_no_extreme_pairs | log_review_latency_hours | log_github_total_churn_z | GitHub total churn, log1p per SD | 0.29 | 1.34 | 0.96 | 1.86 | 0.08 | 331 | 3.46 | 1344.53 |
| duration_github_enriched_human_account_linked_no_extreme_pairs | log_review_latency_hours | log_github_changed_files_z | GitHub changed files, log1p per SD | -0.14 | 0.87 | 0.61 | 1.24 | 0.44 | 331 | 3.46 | 1344.53 |
| duration_github_enriched_human_account_linked_no_extreme_pairs | log_review_latency_hours | log_github_commits_z | GitHub commits, log1p per SD | 0.44 | 1.56 | 1.19 | 2.04 | 0.00 | 331 | 3.46 | 1344.53 |

Review-duration model run metadata:

| sample | outcome | n | median_hours | aic | status |
| --- | --- | --- | --- | --- | --- |
| duration_human_account_linked_no_extreme_pairs | log_review_latency_hours | 1429 | 3.60 | 5748.50 | ok |
| duration_github_enriched_human_account_linked_no_extreme_pairs | log_review_latency_hours | 331 | 3.46 | 1344.53 | ok |

```json
{
  "spearman_age_merged": {
    "rho": 0.012860566241216162,
    "p": 0.047264091086903944,
    "n": 23798
  },
  "spearman_log_followers_merged": {
    "rho": 0.07761235455568147,
    "p": 3.989383289979763e-33,
    "n": 23798
  },
  "spearman_age_has_human_review": {
    "rho": -0.03516877980998932,
    "p": 5.739238857502769e-08,
    "n": 23798
  },
  "spearman_log_followers_has_human_review": {
    "rho": -0.1387801146149771,
    "p": 1.1995511246648759e-102,
    "n": 23798
  },
  "spearman_age_has_approval": {
    "rho": -0.035248065403673666,
    "p": 5.3585692497552264e-08,
    "n": 23798
  },
  "spearman_log_followers_has_approval": {
    "rho": -0.11592880012716003,
    "p": 5.398715600502241e-72,
    "n": 23798
  },
  "spearman_age_has_changes_requested": {
    "rho": -0.026739596090242932,
    "p": 3.6987944295438545e-05,
    "n": 23798
  },
  "spearman_log_followers_has_changes_requested": {
    "rho": -0.04194021848859061,
    "p": 9.642147140528986e-11,
    "n": 23798
  },
  "spearman_age_has_human_discussion": {
    "rho": -0.040914706474178136,
    "p": 2.7180760816020315e-10,
    "n": 23798
  },
  "spearman_log_followers_has_human_discussion": {
    "rho": -0.13468424828009,
    "p": 9.771182551335736e-97,
    "n": 23798
  },
  "chi2_quartile_merged": {
    "chi2": 265.4308311851438,
    "p": 3.005869551811982e-57,
    "dof": 3,
    "table": {
      "false": {
        "Q1 least": 948,
        "Q2": 1538,
        "Q3": 923,
        "Q4 most": 1110
      },
      "true": {
        "Q1 least": 5002,
        "Q2": 4411,
        "Q3": 5026,
        "Q4 most": 4840
      }
    }
  },
  "chi2_quartile_has_human_review": {
    "chi2": 915.6982651657246,
    "p": 3.482875374274543e-198,
    "dof": 3,
    "table": {
      "false": {
        "Q1 least": 5579,
        "Q2": 5094,
        "Q3": 5936,
        "Q4 most": 5507
      },
      "true": {
        "Q1 least": 371,
        "Q2": 855,
        "Q3": 13,
        "Q4 most": 443
      }
    }
  },
  "chi2_quartile_has_approval": {
    "chi2": 552.5421777059523,
    "p": 1.9538771384394765e-119,
    "dof": 3,
    "table": {
      "false": {
        "Q1 least": 5638,
        "Q2": 5378,
        "Q3": 5943,
        "Q4 most": 5602
      },
      "true": {
        "Q1 least": 312,
        "Q2": 571,
        "Q3": 6,
        "Q4 most": 348
      }
    }
  },
  "chi2_quartile_has_changes_requested": {
    "chi2": 40.27756627990321,
    "p": 9.304997105653815e-09,
    "dof": 3,
    "table": {
      "false": {
        "Q1 least": 5921,
        "Q2": 5906,
        "Q3": 5947,
        "Q4 most": 5933
      },
      "true": {
        "Q1 least": 29,
        "Q2": 43,
        "Q3": 2,
        "Q4 most": 17
      }
    }
  },
  "chi2_quartile_has_human_discussion": {
    "chi2": 1388.9147844140684,
    "p": 7.49163929018559e-301,
    "dof": 3,
    "table": {
      "false": {
        "Q1 least": 5308,
        "Q2": 4638,
        "Q3": 5929,
        "Q4 most": 5174
      },
      "true": {
        "Q1 least": 642,
        "Q2": 1311,
        "Q3": 20,
        "Q4 most": 776
      }
    }
  }
}
```

## Statistical Association Tests

Spearman correlations treat binary outcomes as 0/1; chi-square tests compare outcome rates across account-age quartiles.

```json
{
  "spearman_age_merged": {
    "rho": 0.1667533676652544,
    "p": 1.4884763225122376e-177,
    "n": 28625
  },
  "spearman_log_followers_merged": {
    "rho": 0.208192023736793,
    "p": 8.748536293555726e-278,
    "n": 28625
  },
  "spearman_age_has_human_review": {
    "rho": -0.23542261732202663,
    "p": 0.0,
    "n": 28625
  },
  "spearman_log_followers_has_human_review": {
    "rho": -0.2981247531891201,
    "p": 0.0,
    "n": 28625
  },
  "spearman_age_has_approval": {
    "rho": -0.20909788538342594,
    "p": 3.04545525390329e-280,
    "n": 28625
  },
  "spearman_log_followers_has_approval": {
    "rho": -0.2581359730529727,
    "p": 0.0,
    "n": 28625
  },
  "spearman_age_has_changes_requested": {
    "rho": -0.11035494043690881,
    "p": 2.967272800319311e-78,
    "n": 28625
  },
  "spearman_log_followers_has_changes_requested": {
    "rho": -0.11657117181207456,
    "p": 3.6867569627422695e-87,
    "n": 28625
  },
  "spearman_age_has_human_discussion": {
    "rho": -0.267058140550935,
    "p": 0.0,
    "n": 28625
  },
  "spearman_log_followers_has_human_discussion": {
    "rho": -0.32647526102715424,
    "p": 0.0,
    "n": 28625
  },
  "chi2_quartile_merged": {
    "chi2": 1870.8048601087667,
    "p": 0.0,
    "dof": 3,
    "table": {
      "false": {
        "Q1 least": 3008,
        "Q2": 1023,
        "Q3": 1443,
        "Q4 most": 1277
      },
      "true": {
        "Q1 least": 4149,
        "Q2": 6133,
        "Q3": 5713,
        "Q4 most": 5879
      }
    }
  },
  "chi2_quartile_has_human_review": {
    "chi2": 2712.4883819081815,
    "p": 0.0,
    "dof": 3,
    "table": {
      "false": {
        "Q1 least": 5050,
        "Q2": 6640,
        "Q3": 6764,
        "Q4 most": 6710
      },
      "true": {
        "Q1 least": 2107,
        "Q2": 516,
        "Q3": 392,
        "Q4 most": 446
      }
    }
  },
  "chi2_quartile_has_approval": {
    "chi2": 2280.4157966978873,
    "p": 0.0,
    "dof": 3,
    "table": {
      "false": {
        "Q1 least": 5506,
        "Q2": 6760,
        "Q3": 6946,
        "Q4 most": 6807
      },
      "true": {
        "Q1 least": 1651,
        "Q2": 396,
        "Q3": 210,
        "Q4 most": 349
      }
    }
  },
  "chi2_quartile_has_changes_requested": {
    "chi2": 512.5066000798597,
    "p": 9.294810557846829e-111,
    "dof": 3,
    "table": {
      "false": {
        "Q1 least": 6906,
        "Q2": 7126,
        "Q3": 7140,
        "Q4 most": 7139
      },
      "true": {
        "Q1 least": 251,
        "Q2": 30,
        "Q3": 16,
        "Q4 most": 17
      }
    }
  },
  "chi2_quartile_has_human_discussion": {
    "chi2": 3697.3233716956947,
    "p": 0.0,
    "dof": 3,
    "table": {
      "false": {
        "Q1 least": 4151,
        "Q2": 6271,
        "Q3": 6620,
        "Q4 most": 6377
      },
      "true": {
        "Q1 least": 3006,
        "Q2": 885,
        "Q3": 536,
        "Q4 most": 779
      }
    }
  }
}
```
