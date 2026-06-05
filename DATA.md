# Data Notes

The analyses use the AIDev dataset by Hao Li and collaborators, plus a small GitHub REST API enrichment cache for RQ4.

## Raw AIDev Tables

Raw parquet files are not committed because some exceed normal GitHub file-size limits. In particular, `all_pull_request.parquet` is over 300 MB.

To rerun scripts that expect local parquet files, place the relevant tables under each RQ's `data/` folder:

- `pull_request.parquet`
- `all_pull_request.parquet`
- `user.parquet`
- `all_user.parquet`
- `repository.parquet`
- `pr_reviews.parquet`
- `pr_comments.parquet`
- `pr_review_comments_v2.parquet`
- `pr_timeline.parquet`
- `pr_commits.parquet`
- `pr_commit_details.parquet`
- `pr_task_type.parquet`

RQ1 and RQ4 can also read some tables directly from Hugging Face when local caches are missing. RQ2 and RQ3 expect local parquet files in their `data/` folders.

## Included Cache

`RQ4/data/github_pr_metrics.csv` is included because it is small enough for Git and records the GitHub REST API enrichment used by the final RQ4 analysis.

## Generated Outputs

Curated CSV, JSON, Markdown, PDF, SVG, and PNG outputs are committed under each RQ's `results/` folder where available.
