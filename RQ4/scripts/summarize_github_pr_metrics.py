from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
IN_PATH = BASE_DIR / "data" / "github_pr_metrics.csv"
OUT_DIR = BASE_DIR / "results"


def pct(series: pd.Series) -> float:
    return float(series.mean() * 100) if len(series) else np.nan


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    if not IN_PATH.exists():
        raise SystemExit(f"No GitHub PR metrics cache found at {IN_PATH}")

    data = pd.read_csv(IN_PATH)
    ok = data[data["status"].eq("ok")].copy()
    if ok.empty:
        raise SystemExit("No successful GitHub PR metric rows found.")

    for col in ["additions", "deletions", "changed_files", "commits"]:
        ok[col] = pd.to_numeric(ok[col], errors="coerce")
    ok["total_churn"] = ok["additions"].fillna(0) + ok["deletions"].fillna(0)
    ok["log_total_churn"] = np.log1p(ok["total_churn"])
    ok["is_owner_member_collaborator"] = ok["author_association"].isin(["OWNER", "MEMBER", "COLLABORATOR"])

    by_agent = (
        ok.groupby("agent")
        .agg(
            enriched_prs=("id", "count"),
            median_additions=("additions", "median"),
            median_deletions=("deletions", "median"),
            median_total_churn=("total_churn", "median"),
            median_changed_files=("changed_files", "median"),
            median_commits=("commits", "median"),
            owner_member_collaborator_rate=("is_owner_member_collaborator", pct),
        )
        .reset_index()
    )

    association = (
        ok.groupby(["agent", "author_association"])
        .size()
        .rename("prs")
        .reset_index()
        .sort_values(["agent", "prs"], ascending=[True, False])
    )

    overall = pd.DataFrame(
        [
            {
                "rows": len(data),
                "ok_rows": len(ok),
                "success_rate_pct": len(ok) / len(data) * 100,
                "median_total_churn": ok["total_churn"].median(),
                "median_changed_files": ok["changed_files"].median(),
                "median_commits": ok["commits"].median(),
                "owner_member_collaborator_rate": pct(ok["is_owner_member_collaborator"]),
            }
        ]
    )

    by_agent.to_csv(OUT_DIR / "github_pr_metrics_by_agent.csv", index=False)
    association.to_csv(OUT_DIR / "github_pr_author_association.csv", index=False)
    overall.to_csv(OUT_DIR / "github_pr_metrics_overall.csv", index=False)

    print("Overall")
    print(overall.to_string(index=False))
    print("\nBy agent")
    print(by_agent.to_string(index=False))
    print("\nAuthor association")
    print(association.to_string(index=False))


if __name__ == "__main__":
    main()
