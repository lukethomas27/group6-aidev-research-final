from __future__ import annotations

import json
import re
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf


DATASET = "hf://datasets/hao-li/AIDev"
BASE_DIR = Path(__file__).resolve().parents[1]
LOCAL_DATA_DIR = BASE_DIR / "data"
OUT_DIR = BASE_DIR / "results"


def read_table(name: str, columns: list[str] | None = None) -> pd.DataFrame:
    local_path = LOCAL_DATA_DIR / f"{name}.parquet"
    if local_path.exists():
        return pd.read_parquet(local_path, columns=columns)
    return pd.read_parquet(f"{DATASET}/{name}.parquet", columns=columns)


def parse_utc(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, utc=True, errors="coerce")


def add_author_experience(pr: pd.DataFrame, users: pd.DataFrame) -> pd.DataFrame:
    users = users.rename(
        columns={
            "id": "user_id",
            "created_at": "user_created_at",
        }
    )
    users["user_id"] = pd.to_numeric(users["user_id"], errors="coerce").astype("Int64")
    users["user_created_at"] = parse_utc(users["user_created_at"])
    users["followers"] = pd.to_numeric(users["followers"], errors="coerce")
    users["following"] = pd.to_numeric(users["following"], errors="coerce")

    pr = pr.copy()
    pr["user_id"] = pd.to_numeric(pr["user_id"], errors="coerce").astype("Int64")
    pr["created_at"] = parse_utc(pr["created_at"])
    pr["closed_at"] = parse_utc(pr["closed_at"])
    pr["merged_at"] = parse_utc(pr["merged_at"])
    pr["merged"] = pr["merged_at"].notna()

    merged = pr.merge(
        users[["user_id", "login", "followers", "following", "user_created_at"]],
        on="user_id",
        how="left",
    )
    merged["account_age_years_at_pr"] = (
        (merged["created_at"] - merged["user_created_at"]).dt.total_seconds()
        / (365.25 * 24 * 60 * 60)
    )
    merged.loc[merged["account_age_years_at_pr"] < 0, "account_age_years_at_pr"] = np.nan
    merged["log_followers"] = np.log1p(merged["followers"].clip(lower=0))
    return merged


def add_repository_controls(df: pd.DataFrame, repos: pd.DataFrame) -> pd.DataFrame:
    repos = repos.rename(
        columns={
            "id": "repo_id",
            "language": "repo_language",
            "forks": "repo_forks",
            "stars": "repo_stars",
        }
    )
    repos["repo_id"] = pd.to_numeric(repos["repo_id"], errors="coerce").astype("Int64")
    repos["repo_stars"] = pd.to_numeric(repos["repo_stars"], errors="coerce")
    repos["repo_forks"] = pd.to_numeric(repos["repo_forks"], errors="coerce")

    out = df.copy()
    out["repo_id"] = pd.to_numeric(out["repo_id"], errors="coerce").astype("Int64")
    out = out.merge(
        repos[["repo_id", "repo_language", "repo_forks", "repo_stars"]],
        on="repo_id",
        how="left",
    )
    out["repo_language"] = out["repo_language"].fillna("Unknown")
    top_languages = out["repo_language"].value_counts().head(12).index
    out["language_group"] = np.where(out["repo_language"].isin(top_languages), out["repo_language"], "Other")
    out["log_repo_stars"] = np.log1p(out["repo_stars"].fillna(0).clip(lower=0))
    out["log_repo_forks"] = np.log1p(out["repo_forks"].fillna(0).clip(lower=0))
    out["created_month"] = out["created_at"].dt.strftime("%Y-%m").fillna("Unknown")
    out["is_closed"] = out["closed_at"].notna() | out["state"].eq("closed")
    return out


def add_observed_author_history(df: pd.DataFrame, all_pr: pd.DataFrame) -> pd.DataFrame:
    source = all_pr[["id", "user_id", "repo_id", "created_at", "merged_at"]].copy()
    source["user_id"] = pd.to_numeric(source["user_id"], errors="coerce").astype("Int64")
    source["repo_id"] = pd.to_numeric(source["repo_id"], errors="coerce").astype("Int64")
    source["created_at"] = parse_utc(source["created_at"])
    source["merged"] = parse_utc(source["merged_at"]).notna().astype(int)
    source = source.dropna(subset=["user_id", "repo_id", "created_at"])
    source = source.sort_values(["user_id", "repo_id", "created_at", "id"])

    source["prior_observed_user_repo_prs"] = source.groupby(["user_id", "repo_id"]).cumcount()
    source["prior_observed_user_repo_merged_prs"] = (
        source.groupby(["user_id", "repo_id"])["merged"].cumsum() - source["merged"]
    )
    source["prior_observed_user_prs"] = source.groupby("user_id").cumcount()
    source["prior_observed_user_merged_prs"] = source.groupby("user_id")["merged"].cumsum() - source["merged"]
    pair_totals = (
        source.groupby(["user_id", "repo_id"])
        .size()
        .rename("observed_user_repo_pair_prs")
        .reset_index()
    )

    out = df.merge(
        source[
            [
                "id",
                "prior_observed_user_repo_prs",
                "prior_observed_user_repo_merged_prs",
                "prior_observed_user_prs",
                "prior_observed_user_merged_prs",
            ]
        ],
        on="id",
        how="left",
    )
    out = out.merge(pair_totals, on=["user_id", "repo_id"], how="left")
    history_cols = [
        "prior_observed_user_repo_prs",
        "prior_observed_user_repo_merged_prs",
        "prior_observed_user_prs",
        "prior_observed_user_merged_prs",
    ]
    for col in history_cols:
        out[col] = out[col].fillna(0).clip(lower=0)
        out[f"log_{col}"] = np.log1p(out[col])
    out["observed_user_repo_pair_prs"] = out["observed_user_repo_pair_prs"].fillna(1).clip(lower=1)
    out["prior_observed_user_repo_merge_rate"] = np.where(
        out["prior_observed_user_repo_prs"] > 0,
        out["prior_observed_user_repo_merged_prs"] / out["prior_observed_user_repo_prs"],
        0,
    )
    return out


def summarise_author_repo_pair_volume(pop: pd.DataFrame, threshold: int = 100) -> pd.DataFrame:
    return (
        pop.groupby(["agent", "user", "user_id", "repo_id"], dropna=False)
        .agg(
            pair_prs=("id", "count"),
            observed_pair_prs_all_aidev=("observed_user_repo_pair_prs", "max"),
            merged_rate=("merged", pct),
            median_account_age_years=("account_age_years_at_pr", "median"),
            human_review_rate=("has_human_review", pct),
            human_discussion_rate=("has_human_discussion", pct),
        )
        .reset_index()
        .assign(is_extreme_pair=lambda df: df["observed_pair_prs_all_aidev"] > threshold)
        .sort_values("observed_pair_prs_all_aidev", ascending=False)
    )


def add_timeline_complexity(df: pd.DataFrame) -> pd.DataFrame:
    timeline = read_table("pr_timeline", columns=["pr_id", "event", "commit_id", "actor"])
    event_counts = timeline.pivot_table(
        index="pr_id",
        columns="event",
        values="actor",
        aggfunc="count",
        fill_value=0,
    )
    event_counts.columns = [f"timeline_event_{col}" for col in event_counts.columns]
    agg = (
        timeline.groupby("pr_id")
        .agg(
            timeline_events=("event", "count"),
            timeline_commits=("event", lambda s: int((s == "committed").sum())),
            timeline_distinct_commit_ids=("commit_id", "nunique"),
            timeline_distinct_actors=("actor", "nunique"),
        )
        .join(event_counts, how="left")
        .reset_index()
    )
    agg = agg.rename(
        columns={
            "timeline_event_head_ref_force_pushed": "timeline_force_pushes",
            "timeline_event_review_requested": "timeline_review_requests",
            "timeline_event_labeled": "timeline_labels",
            "timeline_event_ready_for_review": "timeline_ready_for_review_events",
            "timeline_event_convert_to_draft": "timeline_convert_to_draft_events",
        }
    )
    keep = [
        "pr_id",
        "timeline_events",
        "timeline_commits",
        "timeline_distinct_commit_ids",
        "timeline_distinct_actors",
        "timeline_force_pushes",
        "timeline_review_requests",
        "timeline_labels",
        "timeline_ready_for_review_events",
        "timeline_convert_to_draft_events",
    ]
    for col in keep:
        if col not in agg.columns:
            agg[col] = 0

    out = df.merge(agg[keep], left_on="id", right_on="pr_id", how="left")
    for col in [col for col in keep if col != "pr_id"]:
        out[col] = out[col].fillna(0).clip(lower=0)
        out[f"log_{col}"] = np.log1p(out[col])
    return out


def add_github_pr_metrics(df: pd.DataFrame) -> pd.DataFrame:
    metrics_path = LOCAL_DATA_DIR / "github_pr_metrics.csv"
    out = df.copy()
    if not metrics_path.exists():
        out["has_github_metrics"] = False
        return out

    metrics = pd.read_csv(metrics_path)
    metrics = metrics[metrics["status"].eq("ok")].copy()
    keep = [
        "id",
        "additions",
        "deletions",
        "changed_files",
        "commits",
        "author_association",
        "draft",
        "maintainer_can_modify",
    ]
    metrics = metrics[[col for col in keep if col in metrics.columns]]
    for col in ["additions", "deletions", "changed_files", "commits"]:
        metrics[col] = pd.to_numeric(metrics[col], errors="coerce")
    metrics["github_total_churn"] = metrics["additions"].fillna(0) + metrics["deletions"].fillna(0)
    metrics["log_github_total_churn"] = np.log1p(metrics["github_total_churn"])
    metrics["log_github_changed_files"] = np.log1p(metrics["changed_files"].fillna(0).clip(lower=0))
    metrics["log_github_commits"] = np.log1p(metrics["commits"].fillna(0).clip(lower=0))
    metrics["author_association"] = metrics["author_association"].fillna("UNKNOWN")
    metrics["is_owner_member_collaborator"] = metrics["author_association"].isin(
        ["OWNER", "MEMBER", "COLLABORATOR"]
    )

    out = out.merge(metrics, on="id", how="left")
    out["has_github_metrics"] = out["github_total_churn"].notna()
    return out


TASK_PATTERNS = [
    ("security", r"\b(security|vulnerab|cve|auth|permission|xss|csrf|injection)\b"),
    ("dependency", r"\b(dependenc|deps?|bump|upgrade|downgrade|version|package|requirements?)\b"),
    ("ci_build", r"\b(ci|github actions?|workflow|build|docker|container|release|deploy)\b"),
    ("test", r"\b(test|tests|testing|coverage|pytest|jest|spec)\b"),
    ("docs", r"\b(doc|docs|documentation|readme|guide|tutorial|comment typo)\b"),
    ("bugfix", r"\b(fix|bug|error|crash|issue|regression|fail|broken|incorrect|resolve)\b"),
    ("feature", r"\b(feat|feature|add|implement|support|enable|introduce|new)\b"),
    ("refactor", r"\b(refactor|cleanup|clean up|restructure|rename|simplify|deduplicate)\b"),
    ("performance", r"\b(perf|performance|optimi[sz]e|speed|faster|memory|latency)\b"),
]


def classify_task_category(title: object, body: object) -> str:
    title_text = "" if pd.isna(title) else str(title).lower()
    for category, pattern in TASK_PATTERNS:
        if re.search(pattern, title_text):
            return category

    body_text = "" if pd.isna(body) else str(body).lower()[:1000]
    for category, pattern in TASK_PATTERNS:
        if category == "test":
            continue
        if re.search(pattern, body_text):
            return category
    return "other"


def add_task_categories(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "title" not in out.columns:
        out["title"] = ""
    if "body" not in out.columns:
        out["body"] = ""
    out["task_category"] = [
        classify_task_category(title, body) for title, body in zip(out["title"], out["body"])
    ]
    return out


def zscore(series: pd.Series) -> pd.Series:
    std = series.std(skipna=True)
    if pd.isna(std) or std == 0:
        return series * 0
    return (series - series.mean(skipna=True)) / std


def add_quartiles(df: pd.DataFrame, col: str, new_col: str) -> pd.DataFrame:
    out = df.copy()
    valid = out[col].notna()
    labels = ["Q1 least", "Q2", "Q3", "Q4 most"]
    out.loc[valid, new_col] = pd.qcut(out.loc[valid, col], 4, labels=labels, duplicates="drop")
    return out


def pct(series: pd.Series) -> float:
    return float(series.mean() * 100) if len(series) else np.nan


def summarise_preference(all_pr: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    pr_weighted = (
        all_pr.groupby("agent")
        .agg(
            prs=("id", "count"),
            unique_authors=("user_id", "nunique"),
            median_account_age_years=("account_age_years_at_pr", "median"),
            mean_account_age_years=("account_age_years_at_pr", "mean"),
            median_followers=("followers", "median"),
            mean_followers=("followers", "mean"),
            merged_rate=("merged", pct),
        )
        .sort_values("median_account_age_years", ascending=False)
        .reset_index()
    )

    user_agent = (
        all_pr.groupby(["user_id", "user", "agent"], dropna=False)
        .agg(
            prs=("id", "count"),
            median_account_age_years=("account_age_years_at_pr", "median"),
            median_followers=("followers", "median"),
        )
        .reset_index()
    )
    idx = user_agent.sort_values(["user_id", "prs"], ascending=[True, False]).groupby("user_id").head(1).index
    dominant = user_agent.loc[idx].copy()
    dominant = add_quartiles(dominant, "median_account_age_years", "experience_quartile")

    dominant_share = (
        dominant.groupby(["experience_quartile", "agent"], observed=True)
        .size()
        .rename("developers")
        .reset_index()
    )
    dominant_share["share_within_quartile_pct"] = dominant_share.groupby("experience_quartile", observed=True)[
        "developers"
    ].transform(lambda s: s / s.sum() * 100)
    dominant_share = dominant_share.sort_values(["experience_quartile", "share_within_quartile_pct"], ascending=[True, False])

    concentration = (
        all_pr.groupby("agent")
        .agg(
            prs=("id", "count"),
            authors=("user_id", "nunique"),
        )
        .reset_index()
    )
    top_author_counts = (
        all_pr.groupby(["agent", "user"], dropna=False).size().rename("top_author_prs").reset_index()
        .sort_values(["agent", "top_author_prs"], ascending=[True, False])
        .groupby("agent")
        .head(1)
    )
    concentration = concentration.merge(top_author_counts, on="agent", how="left")
    concentration["top_author_pr_share_pct"] = concentration["top_author_prs"] / concentration["prs"] * 100
    concentration = concentration.sort_values("top_author_pr_share_pct", ascending=False)

    return pr_weighted, dominant_share, concentration


def summarise_experience_coverage(pr: pd.DataFrame, users: pd.DataFrame) -> pd.DataFrame:
    users = users.rename(columns={"id": "user_id", "created_at": "user_created_at"})
    users["user_id"] = pd.to_numeric(users["user_id"], errors="coerce").astype("Int64")
    users["user_created_at"] = parse_utc(users["user_created_at"])
    pr = pr.copy()
    pr["user_id"] = pd.to_numeric(pr["user_id"], errors="coerce").astype("Int64")
    pr["created_at"] = parse_utc(pr["created_at"])
    joined = pr.merge(users[["user_id", "user_created_at"]], on="user_id", how="left")
    joined["account_age_years_at_pr"] = (
        (joined["created_at"] - joined["user_created_at"]).dt.total_seconds()
        / (365.25 * 24 * 60 * 60)
    )
    joined["has_valid_experience"] = joined["account_age_years_at_pr"].notna() & (
        joined["account_age_years_at_pr"] >= 0
    )
    coverage = (
        joined.groupby("agent")
        .agg(
            raw_prs=("id", "count"),
            prs_with_experience=("has_valid_experience", "sum"),
            raw_authors=("user_id", "nunique"),
            authors_with_experience=("user_id", lambda s: s[joined.loc[s.index, "has_valid_experience"]].nunique()),
        )
        .reset_index()
    )
    coverage["experience_coverage_pct"] = coverage["prs_with_experience"] / coverage["raw_prs"] * 100
    return coverage.sort_values("experience_coverage_pct")


def build_review_outcomes(pop_pr: pd.DataFrame) -> pd.DataFrame:
    reviews = read_table("pr_reviews", columns=["pr_id", "user_type", "state", "submitted_at"])
    comments = read_table("pr_comments", columns=["pr_id", "user_type", "created_at"])
    inline = read_table("pr_review_comments_v2", columns=["pull_request_url", "user_type", "created_at"])

    reviews["submitted_at"] = parse_utc(reviews["submitted_at"])
    comments["created_at"] = parse_utc(comments["created_at"])
    inline["created_at"] = parse_utc(inline["created_at"])

    human_reviews = reviews[reviews["user_type"].eq("User")]
    review_agg = (
        human_reviews.groupby("pr_id")
        .agg(
            human_reviews=("state", "count"),
            approvals=("state", lambda s: int((s == "APPROVED").sum())),
            changes_requested=("state", lambda s: int((s == "CHANGES_REQUESTED").sum())),
            first_human_review_at=("submitted_at", "min"),
        )
        .reset_index()
    )

    comment_agg = (
        comments[comments["user_type"].eq("User")]
        .groupby("pr_id")
        .size()
        .rename("human_issue_comments")
        .reset_index()
    )

    pop_pr = pop_pr.copy()
    pop_pr["api_pull_url"] = pop_pr["repo_url"].astype(str) + "/pulls/" + pop_pr["number"].astype(str)
    inline_agg = (
        inline[inline["user_type"].eq("User")]
        .groupby("pull_request_url")
        .size()
        .rename("human_inline_comments")
        .reset_index()
        .rename(columns={"pull_request_url": "api_pull_url"})
    )

    out = pop_pr.merge(review_agg, left_on="id", right_on="pr_id", how="left")
    out = out.merge(comment_agg, left_on="id", right_on="pr_id", how="left", suffixes=("", "_comment"))
    out = out.merge(inline_agg, on="api_pull_url", how="left")

    for col in ["human_reviews", "approvals", "changes_requested", "human_issue_comments", "human_inline_comments"]:
        out[col] = out[col].fillna(0).astype(int)
    out["has_human_review"] = out["human_reviews"] > 0
    out["has_approval"] = out["approvals"] > 0
    out["has_changes_requested"] = out["changes_requested"] > 0
    out["has_human_discussion"] = (
        out["human_reviews"] + out["human_issue_comments"] + out["human_inline_comments"]
    ) > 0
    out["time_to_first_human_review_hours"] = (
        (out["first_human_review_at"] - out["created_at"]).dt.total_seconds() / 3600
    )
    out.loc[out["time_to_first_human_review_hours"] < 0, "time_to_first_human_review_hours"] = np.nan
    return out


def summarise_review_effects(pop: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    pop = add_quartiles(pop, "account_age_years_at_pr", "experience_quartile")
    by_q = (
        pop.groupby("experience_quartile", observed=True)
        .agg(
            prs=("id", "count"),
            merged_rate=("merged", pct),
            human_review_rate=("has_human_review", pct),
            approval_rate=("has_approval", pct),
            changes_requested_rate=("has_changes_requested", pct),
            human_discussion_rate=("has_human_discussion", pct),
            median_human_reviews=("human_reviews", "median"),
            median_human_comments=("human_issue_comments", "median"),
            median_inline_comments=("human_inline_comments", "median"),
            median_time_to_first_human_review_hours=("time_to_first_human_review_hours", "median"),
            median_followers=("followers", "median"),
        )
        .reset_index()
    )

    by_agent_q = (
        pop.groupby(["agent", "experience_quartile"], observed=True)
        .agg(
            prs=("id", "count"),
            merged_rate=("merged", pct),
            human_review_rate=("has_human_review", pct),
            approval_rate=("has_approval", pct),
            changes_requested_rate=("has_changes_requested", pct),
            human_discussion_rate=("has_human_discussion", pct),
        )
        .reset_index()
    )

    tests = {}
    for outcome in ["merged", "has_human_review", "has_approval", "has_changes_requested", "has_human_discussion"]:
        valid = pop[["account_age_years_at_pr", outcome]].dropna()
        tests[f"spearman_age_{outcome}"] = {
            "rho": float(stats.spearmanr(valid["account_age_years_at_pr"], valid[outcome].astype(int)).statistic),
            "p": float(stats.spearmanr(valid["account_age_years_at_pr"], valid[outcome].astype(int)).pvalue),
            "n": int(len(valid)),
        }
        valid_followers = pop[["log_followers", outcome]].dropna()
        tests[f"spearman_log_followers_{outcome}"] = {
            "rho": float(stats.spearmanr(valid_followers["log_followers"], valid_followers[outcome].astype(int)).statistic),
            "p": float(stats.spearmanr(valid_followers["log_followers"], valid_followers[outcome].astype(int)).pvalue),
            "n": int(len(valid_followers)),
        }

    q_valid = pop.dropna(subset=["experience_quartile"])
    for outcome in ["merged", "has_human_review", "has_approval", "has_changes_requested", "has_human_discussion"]:
        table = pd.crosstab(q_valid["experience_quartile"], q_valid[outcome])
        chi2, p_value, dof, expected = stats.chi2_contingency(table)
        tests[f"chi2_quartile_{outcome}"] = {
            "chi2": float(chi2),
            "p": float(p_value),
            "dof": int(dof),
            "table": table.to_dict(),
        }

    return by_q, by_agent_q, tests


def summarise_history_and_complexity(pop: pd.DataFrame) -> pd.DataFrame:
    pop = add_quartiles(pop, "account_age_years_at_pr", "experience_quartile")
    return (
        pop.groupby("experience_quartile", observed=True)
        .agg(
            prs=("id", "count"),
            median_prior_repo_prs=("prior_observed_user_repo_prs", "median"),
            mean_prior_repo_prs=("prior_observed_user_repo_prs", "mean"),
            median_prior_repo_merged_prs=("prior_observed_user_repo_merged_prs", "median"),
            median_prior_repo_merge_rate=("prior_observed_user_repo_merge_rate", "median"),
            median_prior_user_prs=("prior_observed_user_prs", "median"),
            median_timeline_commits=("timeline_commits", "median"),
            mean_timeline_commits=("timeline_commits", "mean"),
            median_timeline_events=("timeline_events", "median"),
            median_force_pushes=("timeline_force_pushes", "median"),
            median_distinct_actors=("timeline_distinct_actors", "median"),
        )
        .reset_index()
    )


def summarise_task_categories(pop: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    by_task = (
        pop.groupby("task_category")
        .agg(
            prs=("id", "count"),
            merged_rate=("merged", pct),
            human_review_rate=("has_human_review", pct),
            approval_rate=("has_approval", pct),
            changes_requested_rate=("has_changes_requested", pct),
            human_discussion_rate=("has_human_discussion", pct),
            median_account_age_years=("account_age_years_at_pr", "median"),
            median_timeline_events=("timeline_events", "median"),
        )
        .reset_index()
        .sort_values("prs", ascending=False)
    )
    by_agent_task = (
        pop.groupby(["agent", "task_category"])
        .agg(
            prs=("id", "count"),
            merged_rate=("merged", pct),
            human_review_rate=("has_human_review", pct),
            approval_rate=("has_approval", pct),
            human_discussion_rate=("has_human_discussion", pct),
        )
        .reset_index()
        .sort_values(["agent", "prs"], ascending=[True, False])
    )
    by_agent_task["share_within_agent_pct"] = by_agent_task.groupby("agent")["prs"].transform(
        lambda s: s / s.sum() * 100
    )
    return by_task, by_agent_task


def tests_for(pop: pd.DataFrame) -> dict:
    _, _, tests = summarise_review_effects(pop)
    return tests


def clean_term(term: str) -> str:
    if term == "account_age_z":
        return "account age, per SD"
    if term == "log_followers_z":
        return "followers, log1p per SD"
    if term == "log_repo_stars_z":
        return "repo stars, log1p per SD"
    if term == "log_repo_forks_z":
        return "repo forks, log1p per SD"
    if term == "log_prior_repo_prs_z":
        return "prior observed author-repo PRs, log1p per SD"
    if term == "prior_repo_merge_rate_z":
        return "prior observed author-repo merge rate, per SD"
    if term == "log_timeline_commits_z":
        return "timeline commits, log1p per SD"
    if term == "log_timeline_events_z":
        return "timeline events, log1p per SD"
    if term == "log_timeline_force_pushes_z":
        return "timeline force pushes, log1p per SD"
    if term == "log_github_total_churn_z":
        return "GitHub total churn, log1p per SD"
    if term == "log_github_changed_files_z":
        return "GitHub changed files, log1p per SD"
    if term == "log_github_commits_z":
        return "GitHub commits, log1p per SD"
    match = re.match(r"C\(author_association.*\)\[T\.(.*)\]", term)
    if match:
        return f"author_association={match.group(1)} vs CONTRIBUTOR"
    match = re.match(r"C\(agent.*\)\[T\.(.*)\]", term)
    if match:
        return f"agent={match.group(1)} vs OpenAI_Codex"
    return term


def exp_or_inf(value: float) -> float:
    try:
        if value > 700:
            return np.inf
        if value < -700:
            return 0.0
        return float(np.exp(value))
    except FloatingPointError:
        return np.inf


def fit_controlled_logit(df: pd.DataFrame, outcome: str, sample_name: str) -> tuple[pd.DataFrame, dict]:
    required = [
        outcome,
        "repo_id",
        "account_age_years_at_pr",
        "log_followers",
        "log_repo_stars",
        "log_repo_forks",
        "log_prior_observed_user_repo_prs",
        "prior_observed_user_repo_merge_rate",
        "log_timeline_commits",
        "log_timeline_events",
        "log_timeline_force_pushes",
        "agent",
        "task_category",
        "language_group",
        "created_month",
    ]
    working = df.dropna(subset=required).copy()
    working[outcome] = working[outcome].astype(int)
    working["account_age_z"] = zscore(working["account_age_years_at_pr"])
    working["log_followers_z"] = zscore(working["log_followers"])
    working["log_repo_stars_z"] = zscore(working["log_repo_stars"])
    working["log_repo_forks_z"] = zscore(working["log_repo_forks"])
    working["log_prior_repo_prs_z"] = zscore(working["log_prior_observed_user_repo_prs"])
    working["prior_repo_merge_rate_z"] = zscore(working["prior_observed_user_repo_merge_rate"])
    working["log_timeline_commits_z"] = zscore(working["log_timeline_commits"])
    working["log_timeline_events_z"] = zscore(working["log_timeline_events"])
    working["log_timeline_force_pushes_z"] = zscore(working["log_timeline_force_pushes"])
    working["cluster_repo_id"] = working["repo_id"].astype(str)

    meta = {
        "sample": sample_name,
        "outcome": outcome,
        "n": int(len(working)),
        "event_rate_pct": float(working[outcome].mean() * 100) if len(working) else np.nan,
        "aic": np.nan,
        "status": "ok",
    }
    if len(working) < 50 or working[outcome].nunique() < 2:
        meta["status"] = "insufficient outcome variation"
        return pd.DataFrame(), meta

    formula = (
        f"{outcome} ~ account_age_z + log_followers_z + "
        "C(agent, Treatment(reference='OpenAI_Codex')) + "
        "log_repo_stars_z + log_repo_forks_z + "
        "log_prior_repo_prs_z + prior_repo_merge_rate_z + "
        "log_timeline_commits_z + log_timeline_events_z + log_timeline_force_pushes_z + "
        "C(task_category) + C(language_group) + C(created_month)"
    )
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = smf.glm(formula=formula, data=working, family=sm.families.Binomial()).fit(
                maxiter=200,
                cov_type="cluster",
                cov_kwds={"groups": working["cluster_repo_id"]},
            )
    except Exception as exc:
        meta["status"] = f"failed: {exc}"
        return pd.DataFrame(), meta

    meta["aic"] = float(result.aic)
    conf = result.conf_int()
    rows = []
    for term in result.params.index:
        if term == "Intercept":
            continue
        beta = float(result.params[term])
        rows.append(
            {
                "sample": sample_name,
                "outcome": outcome,
                "term": term,
                "effect": clean_term(term),
                "coef_log_odds": beta,
                "odds_ratio": exp_or_inf(beta),
                "ci_low": exp_or_inf(float(conf.loc[term, 0])),
                "ci_high": exp_or_inf(float(conf.loc[term, 1])),
                "p_value": float(result.pvalues[term]),
                "n": meta["n"],
                "event_rate_pct": meta["event_rate_pct"],
                "aic": meta["aic"],
            }
        )
    return pd.DataFrame(rows), meta


def fit_github_enriched_logit(df: pd.DataFrame, outcome: str, sample_name: str) -> tuple[pd.DataFrame, dict]:
    required = [
        outcome,
        "repo_id",
        "account_age_years_at_pr",
        "log_followers",
        "agent",
        "task_category",
        "author_association",
        "log_github_total_churn",
        "log_github_changed_files",
        "log_github_commits",
        "created_month",
    ]
    working = df[df["has_github_metrics"]].dropna(subset=required).copy()
    working[outcome] = working[outcome].astype(int)
    working["account_age_z"] = zscore(working["account_age_years_at_pr"])
    working["log_followers_z"] = zscore(working["log_followers"])
    working["log_github_total_churn_z"] = zscore(working["log_github_total_churn"])
    working["log_github_changed_files_z"] = zscore(working["log_github_changed_files"])
    working["log_github_commits_z"] = zscore(working["log_github_commits"])
    working["cluster_repo_id"] = working["repo_id"].astype(str)

    meta = {
        "sample": sample_name,
        "outcome": outcome,
        "n": int(len(working)),
        "event_rate_pct": float(working[outcome].mean() * 100) if len(working) else np.nan,
        "aic": np.nan,
        "status": "ok",
    }
    if len(working) < 50 or working[outcome].nunique() < 2:
        meta["status"] = "insufficient outcome variation"
        return pd.DataFrame(), meta

    formula = (
        f"{outcome} ~ account_age_z + log_followers_z + "
        "C(agent, Treatment(reference='OpenAI_Codex')) + "
        "C(author_association, Treatment(reference='CONTRIBUTOR')) + "
        "log_github_total_churn_z + log_github_changed_files_z + log_github_commits_z + "
        "C(task_category) + C(created_month)"
    )
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = smf.glm(formula=formula, data=working, family=sm.families.Binomial()).fit(
                maxiter=200,
                cov_type="cluster",
                cov_kwds={"groups": working["cluster_repo_id"]},
            )
    except Exception as exc:
        meta["status"] = f"failed: {exc}"
        return pd.DataFrame(), meta

    meta["aic"] = float(result.aic)
    conf = result.conf_int()
    rows = []
    for term in result.params.index:
        if term == "Intercept":
            continue
        beta = float(result.params[term])
        rows.append(
            {
                "sample": sample_name,
                "outcome": outcome,
                "term": term,
                "effect": clean_term(term),
                "coef_log_odds": beta,
                "odds_ratio": exp_or_inf(beta),
                "ci_low": exp_or_inf(float(conf.loc[term, 0])),
                "ci_high": exp_or_inf(float(conf.loc[term, 1])),
                "p_value": float(result.pvalues[term]),
                "n": meta["n"],
                "event_rate_pct": meta["event_rate_pct"],
                "aic": meta["aic"],
            }
        )
    return pd.DataFrame(rows), meta


def run_controlled_models(pop: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    no_extreme = pop[pop["observed_user_repo_pair_prs"] <= 100].copy()
    human_linked = pop[~pop["agent"].isin(["Devin", "Copilot"])].copy()
    human_linked_no_extreme = human_linked[human_linked["observed_user_repo_pair_prs"] <= 100].copy()
    samples = {
        "all_valid_accounts": pop,
        "all_valid_accounts_no_extreme_pairs": no_extreme,
        "human_account_linked": human_linked,
        "human_account_linked_no_extreme_pairs": human_linked_no_extreme,
    }
    rows = []
    metas = []
    for sample_name, sample_df in samples.items():
        for outcome in ["has_human_review", "has_approval", "has_changes_requested", "has_human_discussion"]:
            result, meta = fit_controlled_logit(sample_df, outcome, sample_name)
            metas.append(meta)
            if not result.empty:
                rows.append(result)

        closed = sample_df[sample_df["is_closed"]].copy()
        result, meta = fit_controlled_logit(closed, "merged", f"{sample_name}_closed_only")
        metas.append(meta)
        if not result.empty:
            rows.append(result)

    if rows:
        return pd.concat(rows, ignore_index=True), pd.DataFrame(metas)
    return pd.DataFrame(), pd.DataFrame(metas)


def run_github_enriched_models(pop: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    samples = {
        "github_enriched_human_account_linked_no_extreme_pairs": pop[
            (~pop["agent"].isin(["Devin", "Copilot"]))
            & (pop["observed_user_repo_pair_prs"] <= 100)
            & (pop["has_github_metrics"])
        ].copy(),
    }
    rows = []
    metas = []
    for sample_name, sample_df in samples.items():
        for outcome in ["has_human_review", "has_approval", "has_changes_requested", "has_human_discussion"]:
            result, meta = fit_github_enriched_logit(sample_df, outcome, sample_name)
            metas.append(meta)
            if not result.empty:
                rows.append(result)

        closed = sample_df[sample_df["is_closed"]].copy()
        result, meta = fit_github_enriched_logit(closed, "merged", f"{sample_name}_closed_only")
        metas.append(meta)
        if not result.empty:
            rows.append(result)

    if rows:
        return pd.concat(rows, ignore_index=True), pd.DataFrame(metas)
    return pd.DataFrame(), pd.DataFrame(metas)


def fit_review_duration_model(
    df: pd.DataFrame,
    sample_name: str,
    use_github_metrics: bool = False,
) -> tuple[pd.DataFrame, dict]:
    required = [
        "repo_id",
        "time_to_first_human_review_hours",
        "account_age_years_at_pr",
        "log_followers",
        "agent",
        "task_category",
        "created_month",
    ]
    if use_github_metrics:
        required += [
            "author_association",
            "log_github_total_churn",
            "log_github_changed_files",
            "log_github_commits",
        ]
    else:
        required += [
            "log_repo_stars",
            "log_repo_forks",
            "log_prior_observed_user_repo_prs",
            "prior_observed_user_repo_merge_rate",
            "log_timeline_commits",
            "log_timeline_events",
        ]

    working = df[
        df["time_to_first_human_review_hours"].notna()
        & (df["time_to_first_human_review_hours"] >= 0)
    ].dropna(subset=required).copy()
    if use_github_metrics:
        working = working[working["has_github_metrics"]].copy()
    working["log_review_latency_hours"] = np.log1p(working["time_to_first_human_review_hours"])
    working["account_age_z"] = zscore(working["account_age_years_at_pr"])
    working["log_followers_z"] = zscore(working["log_followers"])
    working["cluster_repo_id"] = working["repo_id"].astype(str)

    if use_github_metrics:
        working["log_github_total_churn_z"] = zscore(working["log_github_total_churn"])
        working["log_github_changed_files_z"] = zscore(working["log_github_changed_files"])
        working["log_github_commits_z"] = zscore(working["log_github_commits"])
        formula = (
            "log_review_latency_hours ~ account_age_z + log_followers_z + "
            "C(agent, Treatment(reference='OpenAI_Codex')) + "
            "C(author_association, Treatment(reference='CONTRIBUTOR')) + "
            "log_github_total_churn_z + log_github_changed_files_z + log_github_commits_z + "
            "C(task_category) + C(created_month)"
        )
    else:
        working["log_repo_stars_z"] = zscore(working["log_repo_stars"])
        working["log_repo_forks_z"] = zscore(working["log_repo_forks"])
        working["log_prior_repo_prs_z"] = zscore(working["log_prior_observed_user_repo_prs"])
        working["prior_repo_merge_rate_z"] = zscore(working["prior_observed_user_repo_merge_rate"])
        working["log_timeline_commits_z"] = zscore(working["log_timeline_commits"])
        working["log_timeline_events_z"] = zscore(working["log_timeline_events"])
        formula = (
            "log_review_latency_hours ~ account_age_z + log_followers_z + "
            "C(agent, Treatment(reference='OpenAI_Codex')) + "
            "log_repo_stars_z + log_repo_forks_z + log_prior_repo_prs_z + "
            "prior_repo_merge_rate_z + log_timeline_commits_z + log_timeline_events_z + "
            "C(task_category) + C(created_month)"
        )

    meta = {
        "sample": sample_name,
        "outcome": "log_review_latency_hours",
        "n": int(len(working)),
        "median_hours": float(working["time_to_first_human_review_hours"].median()) if len(working) else np.nan,
        "aic": np.nan,
        "status": "ok",
    }
    if len(working) < 50:
        meta["status"] = "insufficient reviewed PRs"
        return pd.DataFrame(), meta

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = smf.ols(formula=formula, data=working).fit(
                cov_type="cluster",
                cov_kwds={"groups": working["cluster_repo_id"]},
            )
    except Exception as exc:
        meta["status"] = f"failed: {exc}"
        return pd.DataFrame(), meta

    meta["aic"] = float(result.aic)
    conf = result.conf_int()
    rows = []
    for term in result.params.index:
        if term == "Intercept":
            continue
        beta = float(result.params[term])
        rows.append(
            {
                "sample": sample_name,
                "outcome": "log_review_latency_hours",
                "term": term,
                "effect": clean_term(term),
                "coef_log_hours": beta,
                "duration_ratio": exp_or_inf(beta),
                "ci_low": exp_or_inf(float(conf.loc[term, 0])),
                "ci_high": exp_or_inf(float(conf.loc[term, 1])),
                "p_value": float(result.pvalues[term]),
                "n": meta["n"],
                "median_hours": meta["median_hours"],
                "aic": meta["aic"],
            }
        )
    return pd.DataFrame(rows), meta


def run_review_duration_models(pop: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    samples = [
        (
            "duration_human_account_linked_no_extreme_pairs",
            pop[(~pop["agent"].isin(["Devin", "Copilot"])) & (pop["observed_user_repo_pair_prs"] <= 100)].copy(),
            False,
        ),
        (
            "duration_github_enriched_human_account_linked_no_extreme_pairs",
            pop[
                (~pop["agent"].isin(["Devin", "Copilot"]))
                & (pop["observed_user_repo_pair_prs"] <= 100)
                & (pop["has_github_metrics"])
            ].copy(),
            True,
        ),
    ]
    rows = []
    metas = []
    for sample_name, sample_df, use_github_metrics in samples:
        result, meta = fit_review_duration_model(sample_df, sample_name, use_github_metrics)
        metas.append(meta)
        if not result.empty:
            rows.append(result)
    if rows:
        return pd.concat(rows, ignore_index=True), pd.DataFrame(metas)
    return pd.DataFrame(), pd.DataFrame(metas)


def write_markdown_summary(
    all_coverage: pd.DataFrame,
    pop_coverage: pd.DataFrame,
    pr_weighted: pd.DataFrame,
    dominant_share: pd.DataFrame,
    concentration: pd.DataFrame,
    review_by_q: pd.DataFrame,
    review_by_agent_q: pd.DataFrame,
    review_by_q_human_linked: pd.DataFrame,
    history_complexity_by_q: pd.DataFrame,
    pair_volume_top: pd.DataFrame,
    pair_volume_summary: pd.DataFrame,
    task_by_category: pd.DataFrame,
    task_by_agent_category: pd.DataFrame,
    tests_human_linked: dict,
    controlled_key: pd.DataFrame,
    model_meta: pd.DataFrame,
    github_enriched_key: pd.DataFrame,
    github_enriched_meta: pd.DataFrame,
    duration_key: pd.DataFrame,
    duration_meta: pd.DataFrame,
    tests: dict,
) -> None:
    OUT_DIR.mkdir(exist_ok=True)

    def md_cell(value: object) -> str:
        if pd.isna(value):
            return ""
        if isinstance(value, float):
            return f"{value:.2f}"
        text = str(value)
        return text.replace("|", "\\|").replace("\n", " ")

    def md_table(df: pd.DataFrame, n: int | None = None) -> str:
        view = df if n is None else df.head(n)
        columns = list(view.columns)
        rows = [
            "| " + " | ".join(columns) + " |",
            "| " + " | ".join(["---"] * len(columns)) + " |",
        ]
        for _, row in view.iterrows():
            rows.append("| " + " | ".join(md_cell(row[col]) for col in columns) + " |")
        return "\n".join(rows)

    pref_top = pr_weighted[
        [
            "agent",
            "prs",
            "unique_authors",
            "median_account_age_years",
            "median_followers",
            "merged_rate",
        ]
    ]
    review_top = review_by_q.copy()
    agent_review = review_by_agent_q.sort_values(["agent", "experience_quartile"])

    lines = [
        "# AIDev Developer Experience Analysis",
        "",
        "Research question: Which agents do more experienced developers prefer? Does developer experience influence how AI-generated contributions are reviewed and accepted?",
        "",
        "Experience is operationalized as GitHub account age at PR creation. Follower count is included as a secondary robustness proxy. Preference is approximated from the agent label on each PR and, for user-weighted results, the agent with the most PRs for each author account.",
        "",
        "Important caveat: this dataset records the GitHub account that opened the PR. Some agents are heavily concentrated in one bot/service account, so their rows do not always reveal the underlying human developer's preference.",
        "",
        "## Experience Coverage",
        "",
        "Rows without a valid author-account creation date are excluded from experience-based summaries.",
        "",
        "All PR table:",
        "",
        md_table(all_coverage),
        "",
        "AIDev-pop PR table:",
        "",
        md_table(pop_coverage),
        "",
        "## Agent Preference by Experience",
        "",
        md_table(pref_top),
        "",
        "## Account Concentration Check",
        "",
        md_table(concentration[["agent", "prs", "authors", "user", "top_author_pr_share_pct"]]),
        "",
        "## Dominant Agent Within Developer Experience Quartiles",
        "",
        md_table(dominant_share),
        "",
        "## Review and Acceptance by Experience Quartile, AIDev-pop",
        "",
        md_table(review_top),
        "",
        "## Review and Acceptance by Agent and Experience Quartile, AIDev-pop",
        "",
        md_table(agent_review),
        "",
        "## Human-Account-Linked Sensitivity",
        "",
        "This excludes Devin and Copilot rows because Devin is represented by one centralized bot account and Copilot lacks author-account creation dates in AIDev-pop.",
        "",
        md_table(review_by_q_human_linked),
        "",
        "## Prior History and Timeline Complexity",
        "",
        "Prior history is counted within the observed AIDev PR universe before each PR's creation time. Timeline fields are proxies for PR activity/complexity, not true code churn.",
        "",
        md_table(history_complexity_by_q),
        "",
        "## Centralized and High-Volume Account Check",
        "",
        "Extreme author-repo pairs are defined as more than 100 observed PRs in the AIDev universe, roughly the top 1% of author-repo pairs in AIDev-pop.",
        "",
        "Summary by agent:",
        "",
        md_table(pair_volume_summary),
        "",
        "Largest author-repo pairs:",
        "",
        md_table(pair_volume_top),
        "",
        "## Task Categories",
        "",
        "Task categories are lightweight keyword classifications from PR title/body, intended as controls and descriptive strata rather than gold labels.",
        "",
        md_table(task_by_category),
        "",
        "Task categories by agent:",
        "",
        md_table(task_by_agent_category),
        "",
        "## Controlled Logistic Models",
        "",
        "Models include account age, followers, agent, repo stars, repo forks, observed prior author-repo history, timeline activity/complexity proxies, repository language, and PR creation month. Merge models are fit only on closed PRs, and standard errors are clustered by repository.",
        "",
        md_table(controlled_key),
        "",
        "Model run metadata:",
        "",
        md_table(model_meta),
        "",
        "## GitHub-Enriched Churn and Author Association Models",
        "",
        "These models use only PRs successfully enriched from the GitHub API, adding true additions/deletions, changed files, commit count, and GitHub author association.",
        "",
        md_table(github_enriched_key),
        "",
        "GitHub-enriched model run metadata:",
        "",
        md_table(github_enriched_meta),
        "",
        "## Review Duration Models",
        "",
        "Review duration is modeled as log1p hours to first human review among PRs that received a human review.",
        "",
        md_table(duration_key),
        "",
        "Review-duration model run metadata:",
        "",
        md_table(duration_meta),
        "",
        "```json",
        json.dumps(tests_human_linked, indent=2),
        "```",
        "",
        "## Statistical Association Tests",
        "",
        "Spearman correlations treat binary outcomes as 0/1; chi-square tests compare outcome rates across account-age quartiles.",
        "",
        "```json",
        json.dumps(tests, indent=2),
        "```",
        "",
    ]
    (OUT_DIR / "aidev_experience_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)

    all_users = read_table("all_user", columns=["id", "login", "followers", "following", "created_at"])
    all_pr = read_table(
        "all_pull_request",
        columns=[
            "id",
            "number",
            "agent",
            "user_id",
            "user",
            "state",
            "created_at",
            "closed_at",
            "merged_at",
            "repo_id",
            "repo_url",
        ],
    )
    all_coverage = summarise_experience_coverage(all_pr, all_users)
    all_pr_raw = all_pr.copy()
    all_pr = add_author_experience(all_pr, all_users)
    all_pr = all_pr.dropna(subset=["account_age_years_at_pr"])

    pr_weighted, dominant_share, concentration = summarise_preference(all_pr)

    pop_users = read_table("user", columns=["id", "login", "followers", "following", "created_at"])
    pop_pr = read_table(
        "pull_request",
        columns=[
            "id",
            "number",
            "agent",
            "title",
            "body",
            "user_id",
            "user",
            "state",
            "created_at",
            "closed_at",
            "merged_at",
            "repo_id",
            "repo_url",
        ],
    )
    pop_coverage = summarise_experience_coverage(pop_pr, pop_users)
    pop_pr = add_author_experience(pop_pr, pop_users)
    pop_pr = pop_pr.dropna(subset=["account_age_years_at_pr"])
    pop_pr = add_task_categories(pop_pr)
    pop = build_review_outcomes(pop_pr)
    pop_repos = read_table("repository", columns=["id", "language", "forks", "stars"])
    pop = add_repository_controls(pop, pop_repos)
    pop = add_observed_author_history(pop, all_pr_raw)
    pop = add_timeline_complexity(pop)
    pop = add_github_pr_metrics(pop)
    review_by_q, review_by_agent_q, tests = summarise_review_effects(pop)
    human_linked_pop = pop[~pop["agent"].isin(["Devin", "Copilot"])].copy()
    review_by_q_human_linked, _, tests_human_linked = summarise_review_effects(human_linked_pop)
    history_complexity_by_q = summarise_history_and_complexity(pop)
    pair_volume = summarise_author_repo_pair_volume(pop)
    pair_volume_top = pair_volume.head(20)
    pair_volume_summary = (
        pair_volume.groupby("agent")
        .agg(
            author_repo_pairs=("repo_id", "count"),
            extreme_pairs=("is_extreme_pair", "sum"),
            prs_in_extreme_pairs=("pair_prs", lambda s: int(s[pair_volume.loc[s.index, "is_extreme_pair"]].sum())),
            total_prs=("pair_prs", "sum"),
        )
        .reset_index()
    )
    pair_volume_summary["extreme_pair_pr_share_pct"] = (
        pair_volume_summary["prs_in_extreme_pairs"] / pair_volume_summary["total_prs"] * 100
    )
    task_by_category, task_by_agent_category = summarise_task_categories(pop)
    controlled_results, model_meta = run_controlled_models(pop)
    github_enriched_results, github_enriched_meta = run_github_enriched_models(pop)
    duration_results, duration_meta = run_review_duration_models(pop)
    key_effects = [
        "account age, per SD",
        "followers, log1p per SD",
        "agent=Claude_Code vs OpenAI_Codex",
        "agent=Cursor vs OpenAI_Codex",
        "agent=Devin vs OpenAI_Codex",
        "prior observed author-repo PRs, log1p per SD",
        "prior observed author-repo merge rate, per SD",
        "timeline commits, log1p per SD",
        "timeline events, log1p per SD",
        "timeline force pushes, log1p per SD",
    ]
    controlled_key = controlled_results[controlled_results["effect"].isin(key_effects)].copy()
    github_key_effects = [
        "account age, per SD",
        "followers, log1p per SD",
        "agent=Claude_Code vs OpenAI_Codex",
        "agent=Cursor vs OpenAI_Codex",
        "GitHub total churn, log1p per SD",
        "GitHub changed files, log1p per SD",
        "GitHub commits, log1p per SD",
        "author_association=COLLABORATOR vs CONTRIBUTOR",
        "author_association=MEMBER vs CONTRIBUTOR",
        "author_association=OWNER vs CONTRIBUTOR",
        "author_association=NONE vs CONTRIBUTOR",
    ]
    github_enriched_key = github_enriched_results[
        github_enriched_results["effect"].isin(github_key_effects)
    ].copy()
    duration_key_effects = [
        "account age, per SD",
        "followers, log1p per SD",
        "agent=Claude_Code vs OpenAI_Codex",
        "agent=Cursor vs OpenAI_Codex",
        "GitHub total churn, log1p per SD",
        "GitHub changed files, log1p per SD",
        "GitHub commits, log1p per SD",
        "author_association=COLLABORATOR vs CONTRIBUTOR",
        "author_association=MEMBER vs CONTRIBUTOR",
        "author_association=OWNER vs CONTRIBUTOR",
        "author_association=NONE vs CONTRIBUTOR",
        "timeline events, log1p per SD",
        "prior observed author-repo PRs, log1p per SD",
    ]
    duration_key = duration_results[duration_results["effect"].isin(duration_key_effects)].copy()

    all_coverage.to_csv(OUT_DIR / "experience_coverage_all_pull_request.csv", index=False)
    pop_coverage.to_csv(OUT_DIR / "experience_coverage_aidev_pop.csv", index=False)
    pr_weighted.to_csv(OUT_DIR / "agent_preference_pr_weighted.csv", index=False)
    dominant_share.to_csv(OUT_DIR / "dominant_agent_by_experience_quartile.csv", index=False)
    concentration.to_csv(OUT_DIR / "agent_account_concentration.csv", index=False)
    review_by_q.to_csv(OUT_DIR / "review_acceptance_by_experience_quartile.csv", index=False)
    review_by_agent_q.to_csv(OUT_DIR / "review_acceptance_by_agent_experience_quartile.csv", index=False)
    review_by_q_human_linked.to_csv(
        OUT_DIR / "review_acceptance_by_experience_quartile_human_linked.csv", index=False
    )
    history_complexity_by_q.to_csv(OUT_DIR / "history_complexity_by_experience_quartile.csv", index=False)
    pair_volume.to_csv(OUT_DIR / "author_repo_pair_volume.csv", index=False)
    pair_volume_summary.to_csv(OUT_DIR / "author_repo_pair_volume_summary.csv", index=False)
    task_by_category.to_csv(OUT_DIR / "task_category_summary.csv", index=False)
    task_by_agent_category.to_csv(OUT_DIR / "task_category_by_agent.csv", index=False)
    controlled_results.to_csv(OUT_DIR / "controlled_logistic_coefficients.csv", index=False)
    controlled_key.to_csv(OUT_DIR / "controlled_logistic_key_effects.csv", index=False)
    model_meta.to_csv(OUT_DIR / "controlled_logistic_model_metadata.csv", index=False)
    github_enriched_results.to_csv(OUT_DIR / "github_enriched_logistic_coefficients.csv", index=False)
    github_enriched_key.to_csv(OUT_DIR / "github_enriched_logistic_key_effects.csv", index=False)
    github_enriched_meta.to_csv(OUT_DIR / "github_enriched_logistic_model_metadata.csv", index=False)
    duration_results.to_csv(OUT_DIR / "review_duration_coefficients.csv", index=False)
    duration_key.to_csv(OUT_DIR / "review_duration_key_effects.csv", index=False)
    duration_meta.to_csv(OUT_DIR / "review_duration_model_metadata.csv", index=False)
    (OUT_DIR / "statistical_tests.json").write_text(json.dumps(tests, indent=2), encoding="utf-8")
    (OUT_DIR / "statistical_tests_human_linked.json").write_text(
        json.dumps(tests_human_linked, indent=2), encoding="utf-8"
    )

    write_markdown_summary(
        all_coverage,
        pop_coverage,
        pr_weighted,
        dominant_share,
        concentration,
        review_by_q,
        review_by_agent_q,
        review_by_q_human_linked,
        history_complexity_by_q,
        pair_volume_top,
        pair_volume_summary,
        task_by_category,
        task_by_agent_category,
        tests_human_linked,
        controlled_key,
        model_meta,
        github_enriched_key,
        github_enriched_meta,
        duration_key,
        duration_meta,
        tests,
    )


if __name__ == "__main__":
    main()
