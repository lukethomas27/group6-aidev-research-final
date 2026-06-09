from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf


BASE_URL = "https://huggingface.co/datasets/hao-li/AIDev/resolve/main/"
BASE_DIR = Path(__file__).resolve().parents[1]
OUT = BASE_DIR / "results"


def rank_order(values: pd.Series, higher_is_better: bool = True) -> list[str]:
    return values.sort_values(ascending=not higher_is_better).index.tolist()


def main() -> None:
    OUT.mkdir(exist_ok=True)
    df = pd.read_parquet(OUT / "filtered_sentiment_items.parquet")
    pr = pd.read_parquet(BASE_URL + "pull_request.parquet")
    pr = pr[["id", "agent", "merged_at", "state", "created_at", "closed_at", "repo_id"]].rename(
        columns={"id": "pr_id", "state": "pr_state"}
    )
    pr["merged"] = pr["merged_at"].notna().astype(int)
    df = df.merge(pr[["pr_id", "repo_id", "merged"]], on="pr_id", how="left")
    df["senticr_negative"] = (df["senticr_oracle"] == -1).astype(int)

    # Bootstrap confidence intervals and rank stability by comment-level sentiment.
    rng = np.random.default_rng(404)
    boot_rows = []
    agents = sorted(df["agent"].unique())
    groups = {agent: df[df["agent"] == agent] for agent in agents}
    for rep in range(1000):
        rep_scores = []
        for agent, group in groups.items():
            idx = rng.integers(0, len(group), len(group))
            sample = group.iloc[idx]
            rep_scores.append(
                {
                    "rep": rep,
                    "agent": agent,
                    "vader_mean": sample["vader"].mean(),
                    "textblob_mean": sample["textblob"].mean(),
                    "senticr_negative_share": sample["senticr_negative"].mean(),
                }
            )
        rep_df = pd.DataFrame(rep_scores)
        for method, col, ascending in [
            ("VADER", "vader_mean", False),
            ("TextBlob", "textblob_mean", False),
            ("SentiCR", "senticr_negative_share", True),
        ]:
            ordered = rep_df.sort_values(col, ascending=ascending)["agent"].tolist()
            for rank, agent in enumerate(ordered, start=1):
                boot_rows.append(
                    {
                        "rep": rep,
                        "method": method,
                        "agent": agent,
                        "rank": rank,
                        "score": rep_df.loc[rep_df["agent"] == agent, col].iloc[0],
                    }
                )
    boot = pd.DataFrame(boot_rows)
    boot_summary = (
        boot.groupby(["method", "agent"])
        .agg(
            mean_score=("score", "mean"),
            ci_low=("score", lambda x: x.quantile(0.025)),
            ci_high=("score", lambda x: x.quantile(0.975)),
            mean_rank=("rank", "mean"),
            top1_share=("rank", lambda x: (x == 1).mean()),
            top2_share=("rank", lambda x: (x <= 2).mean()),
            bottom_share=("rank", lambda x: (x == 5).mean()),
        )
        .reset_index()
    )
    boot_summary.to_csv(OUT / "triangulation_bootstrap_rank_stability.csv", index=False)

    # PR-level sentiment: avoid one heavily discussed PR dominating comment-level results.
    pr_sent = (
        df.groupby(["pr_id", "agent"])
        .agg(
            n_discussion_items=("clean", "size"),
            vader_mean=("vader", "mean"),
            textblob_mean=("textblob", "mean"),
            senticr_negative_share=("senticr_negative", "mean"),
            merged=("merged", "max"),
            repo_id=("repo_id", "first"),
        )
        .reset_index()
    )
    pr_sent["log_discussion_items"] = np.log1p(pr_sent["n_discussion_items"])
    pr_sent.to_csv(OUT / "triangulation_pr_level_sentiment.csv", index=False)

    pr_agent_summary = (
        pr_sent.groupby("agent")
        .agg(
            prs_with_discussion=("pr_id", "size"),
            merge_rate=("merged", "mean"),
            vader_pr_mean=("vader_mean", "mean"),
            textblob_pr_mean=("textblob_mean", "mean"),
            senticr_negative_pr_mean=("senticr_negative_share", "mean"),
        )
        .sort_values("vader_pr_mean", ascending=False)
    )
    pr_agent_summary.to_csv(OUT / "triangulation_pr_level_agent_summary.csv")

    merged_compare = (
        pr_sent.groupby("merged")
        .agg(
            prs=("pr_id", "size"),
            vader_mean=("vader_mean", "mean"),
            textblob_mean=("textblob_mean", "mean"),
            senticr_negative_share=("senticr_negative_share", "mean"),
            discussion_items=("n_discussion_items", "mean"),
        )
        .rename(index={0: "not_merged", 1: "merged"})
    )
    merged_compare.to_csv(OUT / "triangulation_merged_vs_unmerged.csv")

    # Logistic model: PR merge outcome predicted by sentiment and agent.
    # This is not causal; it checks whether sentiment aligns with actual outcome.
    model_df = pr_sent.dropna(subset=["merged", "vader_mean", "senticr_negative_share"]).copy()
    model_df["agent"] = pd.Categorical(
        model_df["agent"],
        categories=["Copilot", "OpenAI_Codex", "Devin", "Cursor", "Claude_Code"],
    )
    logit = smf.logit(
        "merged ~ vader_mean + senticr_negative_share + log_discussion_items + C(agent)",
        data=model_df,
    ).fit(disp=False)
    (OUT / "triangulation_merge_logit_summary.txt").write_text(str(logit.summary()))

    # Method consensus: how often each agent appears in top/bottom positions across major signals.
    method_scores = {
        "VADER comment": df.groupby("agent")["vader"].mean(),
        "TextBlob comment": df.groupby("agent")["textblob"].mean(),
        "SentiCR comment": -df.groupby("agent")["senticr_negative"].mean(),
        "VADER PR-level": pr_agent_summary["vader_pr_mean"],
        "SentiCR PR-level": -pr_agent_summary["senticr_negative_pr_mean"],
    }
    consensus_rows = []
    for method, scores in method_scores.items():
        ordered = scores.sort_values(ascending=False).index.tolist()
        for rank, agent in enumerate(ordered, start=1):
            consensus_rows.append({"method": method, "agent": agent, "rank": rank})
    consensus = pd.DataFrame(consensus_rows)
    consensus_summary = (
        consensus.groupby("agent")
        .agg(
            mean_rank=("rank", "mean"),
            top2_count=("rank", lambda x: int((x <= 2).sum())),
            bottom_count=("rank", lambda x: int((x == 5).sum())),
        )
        .sort_values("mean_rank")
    )
    consensus_summary.to_csv(OUT / "triangulation_method_consensus.csv")

    lines = [
        "Triangulation analysis summary",
        "",
        "Bootstrap rank stability files:",
        str(OUT / "triangulation_bootstrap_rank_stability.csv"),
        "",
        "PR-level sentiment by agent:",
        pr_agent_summary.round(3).to_string(),
        "",
        "Merged vs unmerged PR-level sentiment:",
        merged_compare.round(3).to_string(),
        "",
        "Method consensus across comment-level and PR-level sentiment signals:",
        consensus_summary.round(3).to_string(),
        "",
        "Merge-logit key coefficients:",
    ]
    for term in ["vader_mean", "senticr_negative_share", "log_discussion_items"]:
        lines.append(f"{term}: coef={logit.params[term]:.4f}, p={logit.pvalues[term]:.3e}")
    (OUT / "triangulation_summary.txt").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
