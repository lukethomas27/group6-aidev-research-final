from __future__ import annotations

import html
import re
from itertools import combinations
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy import stats
from statsmodels.stats.multitest import multipletests
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC


BASE_URL = "https://huggingface.co/datasets/hao-li/AIDev/resolve/main/"
BASE_DIR = Path(__file__).resolve().parents[1]
OUT = BASE_DIR / "results"
FIG = BASE_DIR / "figures"


def clean_text(value: object) -> str:
    text = "" if pd.isna(value) else html.unescape(str(value))
    text = re.sub(r"<!--.*?-->|<details.*?</details>|<[^>]+>", " ", text, flags=re.S)
    text = re.sub(r"```.*?```|`[^`]*`", " ", text, flags=re.S)
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"[@#]\S+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def load_discussion_items() -> tuple[pd.DataFrame, pd.DataFrame]:
    pr = pd.read_parquet(BASE_URL + "pull_request.parquet")
    pr["pr_api_url"] = pr["repo_url"] + "/pulls/" + pr["number"].astype(str)
    prmeta = pr[["id", "agent", "user", "pr_api_url"]].rename(
        columns={"id": "pr_id", "user": "pr_author"}
    )

    comments = pd.read_parquet(BASE_URL + "pr_comments.parquet")
    comments = comments.merge(prmeta[["pr_id", "agent", "pr_author"]], on="pr_id", how="left")
    comments["kind"] = "issue_comment"
    comments["text"] = comments["body"]
    comments["time"] = pd.to_datetime(comments["created_at"], utc=True, errors="coerce")

    reviews = pd.read_parquet(BASE_URL + "pr_reviews.parquet")
    reviews = reviews.merge(prmeta[["pr_id", "agent", "pr_author"]], on="pr_id", how="left")
    reviews["kind"] = "review_body"
    reviews["text"] = reviews["body"]
    reviews["time"] = pd.to_datetime(reviews["submitted_at"], utc=True, errors="coerce")

    inline = pd.read_parquet(BASE_URL + "pr_review_comments_v2.parquet")
    inline = inline.merge(
        prmeta[["pr_api_url", "agent", "pr_author", "pr_id"]],
        left_on="pull_request_url",
        right_on="pr_api_url",
        how="left",
    )
    inline["kind"] = "inline_review_comment"
    inline["text"] = inline["body"]
    inline["time"] = pd.to_datetime(inline["created_at"], utc=True, errors="coerce")

    cols = ["pr_id", "agent", "pr_author", "user", "user_type", "kind", "text", "time"]
    df = pd.concat([comments[cols], reviews[cols], inline[cols]], ignore_index=True, sort=False)
    df = df[df["agent"].notna()].copy()
    df = df[df["user_type"].fillna("").str.lower().ne("bot")]
    df = df[df["user"].fillna("").str.lower() != df["pr_author"].fillna("").str.lower()]
    df["clean"] = df["text"].map(clean_text)
    df["n_words"] = df["clean"].str.split().map(len)
    df = df[df["n_words"] >= 3].copy()
    df["month"] = df["time"].dt.to_period("M").astype(str)

    review_state = reviews[reviews["agent"].notna()].copy()
    review_state = review_state[review_state["user_type"].fillna("").str.lower().ne("bot")]
    review_state = review_state[
        review_state["user"].fillna("").str.lower()
        != review_state["pr_author"].fillna("").str.lower()
    ]
    review_state = review_state[review_state["state"].isin(["APPROVED", "CHANGES_REQUESTED", "COMMENTED"])].copy()
    review_state["state_score"] = review_state["state"].map(
        {"APPROVED": 1, "CHANGES_REQUESTED": -1, "COMMENTED": 0}
    )
    return df, review_state


def add_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    analyzer = SentimentIntensityAnalyzer()
    df["vader"] = df["clean"].map(lambda s: analyzer.polarity_scores(s)["compound"])
    df["textblob"] = df["clean"].map(lambda s: TextBlob(s).sentiment.polarity)

    oracle = pd.read_excel("external/SentiCR/SentiCR/oracle.xlsx", header=None, names=["text", "label"])
    oracle["clean"] = oracle["text"].map(clean_text)
    X_train, X_test, y_train, y_test = train_test_split(
        oracle["clean"], oracle["label"], test_size=0.2, random_state=404, stratify=oracle["label"]
    )
    senticr_model = Pipeline(
        [
            ("tfidf", TfidfVectorizer(min_df=2, ngram_range=(1, 2), stop_words="english")),
            ("clf", LinearSVC(class_weight="balanced", random_state=404)),
        ]
    )
    senticr_model.fit(X_train, y_train)
    df["senticr_oracle"] = senticr_model.predict(df["clean"])

    report = classification_report(y_test, senticr_model.predict(X_test), digits=3)
    OUT.mkdir(exist_ok=True)
    (OUT / "senticr_oracle_holdout_report.txt").write_text(report)
    return df


def aggregate_outputs(df: pd.DataFrame, review_state: pd.DataFrame) -> None:
    OUT.mkdir(exist_ok=True)
    FIG.mkdir(exist_ok=True)

    def label_vader(x: float) -> str:
        return "positive" if x >= 0.05 else ("negative" if x <= -0.05 else "neutral")

    def label_textblob(x: float) -> str:
        return "positive" if x >= 0.10 else ("negative" if x <= -0.10 else "neutral")

    df["vader_label"] = df["vader"].map(label_vader)
    df["textblob_label"] = df["textblob"].map(label_textblob)

    monthly = (
        df.groupby("month")
        .agg(
            n=("clean", "size"),
            vader_mean=("vader", "mean"),
            textblob_mean=("textblob", "mean"),
            senticr_negative_share=("senticr_oracle", lambda x: (x == -1).mean()),
        )
        .reset_index()
    )
    monthly.to_csv(OUT / "monthly_sentiment.csv", index=False)

    agent = (
        df.groupby("agent")
        .agg(
            n=("clean", "size"),
            vader_mean=("vader", "mean"),
            textblob_mean=("textblob", "mean"),
            senticr_negative_share=("senticr_oracle", lambda x: (x == -1).mean()),
            vader_positive=("vader_label", lambda x: (x == "positive").mean()),
            vader_negative=("vader_label", lambda x: (x == "negative").mean()),
        )
        .reset_index()
    )
    agent.to_csv(OUT / "agent_sentiment.csv", index=False)

    state = (
        review_state.groupby("agent")
        .agg(
            n=("state", "size"),
            state_mean=("state_score", "mean"),
            approved=("state", lambda x: (x == "APPROVED").mean()),
            changes_requested=("state", lambda x: (x == "CHANGES_REQUESTED").mean()),
            commented=("state", lambda x: (x == "COMMENTED").mean()),
        )
        .reset_index()
    )
    state.to_csv(OUT / "review_state_sentiment.csv", index=False)

    sns.set_theme(style="whitegrid", font_scale=1.05)
    plt.figure(figsize=(9, 5))
    plot_monthly = monthly[monthly["n"] >= 30].copy()
    plt.plot(plot_monthly["month"], plot_monthly["vader_mean"], marker="o", label="VADER mean")
    plt.plot(plot_monthly["month"], plot_monthly["textblob_mean"], marker="o", label="TextBlob mean")
    plt.xticks(rotation=35, ha="right")
    plt.ylabel("Mean sentiment score")
    plt.xlabel("Comment month")
    plt.title("Monthly Review Sentiment Toward AI Coding Agent PRs")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG / "monthly_sentiment_trend.png", dpi=220)
    plt.close()

    order = agent.sort_values("vader_mean", ascending=False)["agent"]
    plt.figure(figsize=(9, 5))
    sns.barplot(data=agent, x="agent", y="vader_mean", order=order, color="#4C78A8")
    plt.xticks(rotation=25, ha="right")
    plt.ylabel("Mean VADER sentiment")
    plt.xlabel("Agent")
    plt.title("Agent Ranking by VADER Review Sentiment")
    plt.tight_layout()
    plt.savefig(FIG / "agent_vader_ranking.png", dpi=220)
    plt.close()

    rank_rows = []
    rank_rows += [
        {"method": "VADER", "agent": row.agent, "score": row.vader_mean}
        for row in agent.itertuples()
    ]
    rank_rows += [
        {"method": "TextBlob", "agent": row.agent, "score": row.textblob_mean}
        for row in agent.itertuples()
    ]
    rank_rows += [
        {"method": "SentiCR-trained", "agent": row.agent, "score": -row.senticr_negative_share}
        for row in agent.itertuples()
    ]
    rank_rows += [
        {"method": "Review state", "agent": row.agent, "score": row.state_mean}
        for row in state.itertuples()
    ]
    ranks = pd.DataFrame(rank_rows)
    ranks["rank"] = ranks.groupby("method")["score"].rank(ascending=False, method="min").astype(int)
    ranks.to_csv(OUT / "method_rankings.csv", index=False)

    pivot = ranks.pivot(index="method", columns="agent", values="rank")
    plt.figure(figsize=(9, 4.5))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlGnBu_r", cbar_kws={"label": "Rank (1 = most positive)"})
    plt.title("Agent Rankings Change Across Sentiment Methods")
    plt.xlabel("Agent")
    plt.ylabel("Method")
    plt.tight_layout()
    plt.savefig(FIG / "method_ranking_comparison.png", dpi=220)
    plt.close()


def statistical_tests(df: pd.DataFrame) -> None:
    lines = []
    for score in ["vader", "textblob"]:
        groups = [g[score].values for _, g in df.groupby("agent")]
        h, p = stats.kruskal(*groups)
        lines.append(f"{score}: Kruskal-Wallis H={h:.3f}, p={p:.3e}")

        rows = []
        for a, b in combinations(sorted(df["agent"].unique()), 2):
            av = df.loc[df["agent"] == a, score]
            bv = df.loc[df["agent"] == b, score]
            u, raw_p = stats.mannwhitneyu(av, bv, alternative="two-sided")
            rows.append({"score": score, "agent_a": a, "agent_b": b, "u": u, "raw_p": raw_p})
        pairwise = pd.DataFrame(rows)
        pairwise["holm_p"] = multipletests(pairwise["raw_p"], method="holm")[1]
        pairwise.to_csv(OUT / f"pairwise_{score}_holm.csv", index=False)

    corr = df[["vader", "textblob", "senticr_oracle"]].corr(method="spearman")
    corr.to_csv(OUT / "sentiment_method_spearman.csv")
    lines.append("\nSpearman correlation between sentiment methods:")
    lines.append(corr.round(3).to_string())
    (OUT / "statistical_tests.txt").write_text("\n".join(lines))


def main() -> None:
    df, review_state = load_discussion_items()
    df = add_sentiment(df)
    df.to_parquet(OUT / "filtered_sentiment_items.parquet")
    aggregate_outputs(df, review_state)
    statistical_tests(df)
    print(f"Saved outputs to {OUT.resolve()} and figures to {FIG.resolve()}")


if __name__ == "__main__":
    main()
