from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf


BASE_URL = "https://huggingface.co/datasets/hao-li/AIDev/resolve/main/"
BASE_DIR = Path(__file__).resolve().parents[1]
OUT = BASE_DIR / "results"


def ranking_string(series: pd.Series, higher_is_better: bool = True) -> str:
    ordered = series.sort_values(ascending=not higher_is_better)
    return " > ".join(ordered.index.tolist())


def main() -> None:
    OUT.mkdir(exist_ok=True)
    df = pd.read_parquet(OUT / "filtered_sentiment_items.parquet")
    pr = pd.read_parquet(BASE_URL + "pull_request.parquet")
    prmeta = pr[["id", "repo_id", "repo_url", "agent"]].rename(columns={"id": "pr_id"})
    df = df.merge(prmeta[["pr_id", "repo_id", "repo_url"]], on="pr_id", how="left")
    df["senticr_negative"] = (df["senticr_oracle"] == -1).astype(int)
    df["senticr_positive_signal"] = -df["senticr_negative"]

    raw = (
        df.groupby("agent")
        .agg(
            n=("clean", "size"),
            repos=("repo_id", "nunique"),
            vader_mean=("vader", "mean"),
            textblob_mean=("textblob", "mean"),
            senticr_negative_share=("senticr_negative", "mean"),
        )
        .sort_values("vader_mean", ascending=False)
    )
    raw.to_csv(OUT / "imbalance_raw_agent_summary.csv")

    # Equal-agent downsampling: each agent is repeatedly sampled to the smallest agent N.
    rng = np.random.default_rng(404)
    min_n = int(df.groupby("agent").size().min())
    rows = []
    for rep in range(500):
        sample_parts = []
        for agent, group in df.groupby("agent"):
            take = group.iloc[rng.choice(len(group), size=min_n, replace=False)]
            sample_parts.append(take)
        sample = pd.concat(sample_parts)
        for agent, group in sample.groupby("agent"):
            rows.append(
                {
                    "rep": rep,
                    "agent": agent,
                    "vader_mean": group["vader"].mean(),
                    "textblob_mean": group["textblob"].mean(),
                    "senticr_negative_share": group["senticr_negative"].mean(),
                }
            )
    ds = pd.DataFrame(rows)
    downsample_summary = (
        ds.groupby("agent")
        .agg(
            vader_mean=("vader_mean", "mean"),
            vader_sd=("vader_mean", "std"),
            textblob_mean=("textblob_mean", "mean"),
            textblob_sd=("textblob_mean", "std"),
            senticr_negative_share=("senticr_negative_share", "mean"),
            senticr_negative_sd=("senticr_negative_share", "std"),
        )
        .sort_values("vader_mean", ascending=False)
    )
    downsample_summary.to_csv(OUT / "imbalance_downsample_agent_summary.csv")

    rank_rows = []
    for rep, group in ds.groupby("rep"):
        vader_order = group.sort_values("vader_mean", ascending=False)["agent"].tolist()
        senticr_order = group.sort_values("senticr_negative_share", ascending=True)["agent"].tolist()
        for i, agent in enumerate(vader_order, start=1):
            rank_rows.append({"rep": rep, "method": "VADER downsample", "agent": agent, "rank": i})
        for i, agent in enumerate(senticr_order, start=1):
            rank_rows.append({"rep": rep, "method": "SentiCR downsample", "agent": agent, "rank": i})
    rank_df = pd.DataFrame(rank_rows)
    rank_stability = (
        rank_df.groupby(["method", "agent"])
        .agg(
            mean_rank=("rank", "mean"),
            top1_share=("rank", lambda x: (x == 1).mean()),
            bottom_share=("rank", lambda x: (x == 5).mean()),
        )
        .reset_index()
    )
    rank_stability.to_csv(OUT / "imbalance_downsample_rank_stability.csv", index=False)

    # Repo-normalized averages: each repo-agent cell has equal weight.
    repo_agent = (
        df.groupby(["repo_id", "agent"])
        .agg(
            n=("clean", "size"),
            vader_mean=("vader", "mean"),
            textblob_mean=("textblob", "mean"),
            senticr_negative_share=("senticr_negative", "mean"),
        )
        .reset_index()
    )
    repo_norm = (
        repo_agent.groupby("agent")
        .agg(
            repo_agent_cells=("repo_id", "size"),
            comments=("n", "sum"),
            vader_repo_avg=("vader_mean", "mean"),
            textblob_repo_avg=("textblob_mean", "mean"),
            senticr_negative_repo_avg=("senticr_negative_share", "mean"),
        )
        .sort_values("vader_repo_avg", ascending=False)
    )
    repo_norm.to_csv(OUT / "imbalance_repo_normalized_summary.csv")

    # Within-repo restriction: repositories with at least two agents and at least 5 comments
    # for each included repo-agent cell.
    eligible_cells = repo_agent[repo_agent["n"] >= 5].copy()
    multi_repo_ids = eligible_cells.groupby("repo_id")["agent"].nunique()
    multi_repo_ids = multi_repo_ids[multi_repo_ids >= 2].index
    within = df[df["repo_id"].isin(multi_repo_ids)].copy()
    within = within.merge(
        eligible_cells[["repo_id", "agent"]].assign(eligible_cell=True),
        on=["repo_id", "agent"],
        how="left",
    )
    within = within[within["eligible_cell"].eq(True)].copy()

    within_summary = (
        within.groupby("agent")
        .agg(
            n=("clean", "size"),
            repos=("repo_id", "nunique"),
            vader_mean=("vader", "mean"),
            textblob_mean=("textblob", "mean"),
            senticr_negative_share=("senticr_negative", "mean"),
        )
        .sort_values("vader_mean", ascending=False)
    )
    within_summary.to_csv(OUT / "imbalance_within_repo_summary.csv")

    for score in ["vader", "textblob", "senticr_positive_signal"]:
        within[f"{score}_repo_centered"] = within[score] - within.groupby("repo_id")[score].transform("mean")

    within_centered = (
        within.groupby("agent")
        .agg(
            n=("clean", "size"),
            repos=("repo_id", "nunique"),
            vader_centered=("vader_repo_centered", "mean"),
            textblob_centered=("textblob_repo_centered", "mean"),
            senticr_centered=("senticr_positive_signal_repo_centered", "mean"),
        )
        .sort_values("vader_centered", ascending=False)
    )
    within_centered.to_csv(OUT / "imbalance_within_repo_centered_summary.csv")

    # Repository fixed-effect models. Coefficients are relative to Copilot baseline.
    model_lines = []
    model_df = within[["vader", "textblob", "senticr_positive_signal", "agent", "repo_id"]].copy()
    model_df["agent"] = pd.Categorical(
        model_df["agent"],
        categories=["Copilot", "OpenAI_Codex", "Devin", "Cursor", "Claude_Code"],
    )
    for score in ["vader", "textblob", "senticr_positive_signal"]:
        model = smf.ols(f"{score} ~ C(agent) + C(repo_id)", data=model_df).fit()
        model_lines.append(f"\n{score} repository fixed effects; baseline agent = Copilot")
        for term, coef, pval in zip(model.params.index, model.params.values, model.pvalues.values):
            if term.startswith("C(agent)"):
                model_lines.append(f"{term}: coef={coef:.4f}, p={pval:.3e}")

    summary_lines = [
        "Dataset imbalance robustness summary",
        f"Filtered sentiment items: {len(df):,}",
        f"Equal-agent downsampling N per agent: {min_n:,}; repetitions: 500",
        f"Within-repo restricted comments: {len(within):,}",
        f"Within-repo restricted repositories: {within['repo_id'].nunique():,}",
        "",
        "Raw VADER ranking: " + ranking_string(raw["vader_mean"]),
        "Downsampled VADER ranking: " + ranking_string(downsample_summary["vader_mean"]),
        "Repo-normalized VADER ranking: " + ranking_string(repo_norm["vader_repo_avg"]),
        "Within-repo VADER ranking: " + ranking_string(within_summary["vader_mean"]),
        "Within-repo centered VADER ranking: " + ranking_string(within_centered["vader_centered"]),
        "",
        "Raw SentiCR ranking, lower negative share is better: "
        + ranking_string(raw["senticr_negative_share"], higher_is_better=False),
        "Downsampled SentiCR ranking, lower negative share is better: "
        + ranking_string(downsample_summary["senticr_negative_share"], higher_is_better=False),
        "Repo-normalized SentiCR ranking, lower negative share is better: "
        + ranking_string(repo_norm["senticr_negative_repo_avg"], higher_is_better=False),
        "Within-repo SentiCR ranking, lower negative share is better: "
        + ranking_string(within_summary["senticr_negative_share"], higher_is_better=False),
        "Within-repo centered SentiCR ranking, higher centered signal is better: "
        + ranking_string(within_centered["senticr_centered"]),
        "",
        *model_lines,
    ]
    (OUT / "imbalance_robustness_summary.txt").write_text("\n".join(summary_lines))
    print("\n".join(summary_lines))


if __name__ == "__main__":
    main()
