# RQ1: Review Sentiment

Owner: Amrinder Singh

RQ1 analyzes the sentiment of human review and discussion text around AI-authored pull requests. The scripts triangulate general-purpose sentiment tools with a lightweight code-review-specific classifier and review-state proxy.

## Scripts

- `scripts/analyze_aidev_sentiment.py`: builds the filtered discussion dataset and primary sentiment outputs.
- `scripts/sentiment_triangulation_analysis.py`: compares comment-level and PR-level sentiment signals.
- `scripts/sentiment_imbalance_robustness.py`: checks whether agent imbalance changes sentiment rankings.

## Outputs

Run `analyze_aidev_sentiment.py` first. It writes CSV, TXT, and parquet outputs to `results/` and figures to `figures/`.
