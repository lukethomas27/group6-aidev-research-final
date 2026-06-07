"""Checkpoint script: replicates notebook Sections 0-3 (config, load, build frame,
feasibility gate) to report RQ3 viability at k=5 and k=10. Does NOT run Part A/B.
Logic is kept identical to SENG404_Q4_starter.ipynb."""
import numpy as np
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
AGENTS = ["Claude Code", "Cursor", "Devin", "GitHub Copilot", "OpenAI Codex"]
K_GRID = [5, 10]
MIN_AGENTS_PER_REPO = 2

def load(name):
    df = pd.read_parquet(DATA_DIR / f"{name}.parquet")
    return df

pr       = load("pull_request")
commits  = load("pr_commits")
cdetails = load("pr_commit_details")
tasktype = load("pr_task_type")
repos    = load("repository")

for c in ["created_at", "closed_at", "merged_at"]:
    if c in pr.columns:
        pr[c] = pd.to_datetime(pr[c], errors="coerce", utc=True)

RAW_TO_AGENT = {
    "openai_codex": "OpenAI Codex", "copilot": "GitHub Copilot",
    "devin": "Devin", "cursor": "Cursor", "claude_code": "Claude Code",
}
def norm_agent(x):
    if pd.isna(x):
        return np.nan
    key = str(x).strip().lower().replace("-", "_").replace(" ", "_")
    if key in RAW_TO_AGENT:
        return RAW_TO_AGENT[key]
    k2 = key.replace("_", "")
    for raw, canon in RAW_TO_AGENT.items():
        r = raw.replace("_", "")
        if r in k2 or k2 in r:
            return canon
    return str(x)
pr["agent"] = pr["agent"].map(norm_agent)
assert set(pr["agent"].dropna().unique()) <= set(AGENTS)

pr["is_merged"]   = pr["merged_at"].notna()
pr["is_rejected"] = pr["closed_at"].notna() & pr["merged_at"].isna()
pr["is_open"]     = ~pr["is_merged"] & ~pr["is_rejected"]
pr["decided"]     = pr["is_merged"] | pr["is_rejected"]
pr["merge_time_h"] = (pr["merged_at"] - pr["created_at"]).dt.total_seconds() / 3600

sz = (cdetails.assign(loc=lambda d: d["additions"].fillna(0) + d["deletions"].fillna(0))
              .groupby("pr_id")
              .agg(loc=("loc", "sum"), files_touched=("filename", "nunique"))
              .reset_index())
ncommits = (commits.groupby("pr_id")["sha"].nunique().rename("n_commits").reset_index())
tt = tasktype[["id", "type"]].rename(columns={"id": "pr_join_id", "type": "task_type"})
rf = repos[["id", "stars", "forks", "language"]].rename(columns={"id": "repo_id"})

df = (pr.merge(sz, left_on="id", right_on="pr_id", how="left")
        .merge(ncommits, left_on="id", right_on="pr_id", how="left", suffixes=("", "_c"))
        .merge(tt, left_on="id", right_on="pr_join_id", how="left")
        .merge(rf, on="repo_id", how="left"))
df["log_loc"] = np.log1p(df["loc"].fillna(0))

print("=" * 70)
print("PR-level frame:", df.shape)
print("\nAgent totals (all repos):")
print(df["agent"].value_counts(dropna=False).to_string())
print("\nOutcome totals: merged=%d  rejected=%d  open=%d"
      % (df["is_merged"].sum(), df["is_rejected"].sum(), df["is_open"].sum()))
print("task_type coverage: %d / %d PRs labelled" % (df["task_type"].notna().sum(), len(df)))

# ---------------- Section 3: feasibility gate ----------------
cell_counts = (df.dropna(subset=["agent"])
                 .groupby(["repo_id", "agent"]).size()
                 .rename("n_prs").reset_index())

for k in K_GRID:
    ok = cell_counts[cell_counts["n_prs"] >= k]
    per_repo = ok.groupby("repo_id")["agent"].nunique()
    qual = per_repo[per_repo >= MIN_AGENTS_PER_REPO].index
    covered = ok[ok["repo_id"].isin(qual)]
    panel = df[df["repo_id"].isin(set(qual)) & df["agent"].notna()]
    print("\n" + "=" * 70)
    print(f"=== k = {k} PRs/agent, >= {MIN_AGENTS_PER_REPO} agents/repo ===")
    print(f"qualifying repos              : {len(qual)}")
    print(f"PRs in qualifying cells (>=k) : {int(covered['n_prs'].sum())}")
    print(f"ALL PRs in qualifying repos   : {len(panel)}  (full panel incl. <k cells)")
    print(f"distinct agent-pairs possible : repos with each agent count below")
    print("\nagent presence (in how many qualifying repos each agent has >=k PRs):")
    print(covered.groupby("agent")["repo_id"].nunique().sort_values(ascending=False).to_string())
    # how many repos have N qualifying agents
    print("\nrepos by #qualifying-agents:")
    print(per_repo[per_repo >= MIN_AGENTS_PER_REPO].value_counts().sort_index().to_string())
    # which agent pairs co-occur, and how often
    from itertools import combinations
    pair_counts = {}
    for rid, g in ok[ok["repo_id"].isin(qual)].groupby("repo_id"):
        ags = sorted(g["agent"].unique())
        for a, b in combinations(ags, 2):
            pair_counts[(a, b)] = pair_counts.get((a, b), 0) + 1
    print("\nco-occurring agent pairs (shared qualifying repos):")
    for (a, b), n in sorted(pair_counts.items(), key=lambda kv: -kv[1]):
        print(f"  {a:15s} & {b:15s}: {n} repos")
    # per-(repo,agent) N within qualifying repos
    print("\ntop qualifying repos (repo_id, full panel N, agents w/ >=k):")
    top = (covered.groupby("repo_id")
                  .agg(n_qual_agents=("agent", "nunique"), prs_in_qual_cells=("n_prs", "sum"))
                  .sort_values("prs_in_qual_cells", ascending=False).head(12))
    for rid, row in top.iterrows():
        name = repos.loc[repos["id"] == rid, "full_name"]
        name = name.iloc[0] if len(name) else str(rid)
        print(f"  {name[:45]:45s} agents={int(row['n_qual_agents'])} prs(>=k)={int(row['prs_in_qual_cells'])}")
