"""RQ3 full analysis pipeline (Part A + Part B), run co-primary at k=5 and k=10.
This package used Q4 labels during drafting; the final report maps it to RQ3.
Mirrors SENG404_Q4_starter.ipynb logic. Saves figures to RQ3/results/figures/.
"""
import warnings
import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
FIG = BASE_DIR / "results" / "figures"; FIG.mkdir(exist_ok=True)
AGENTS = ["Claude Code", "Cursor", "Devin", "GitHub Copilot", "OpenAI Codex"]
K_GRID = [5, 10]
MIN_AGENTS_PER_REPO = 2
AGENT_ORDER = ["OpenAI Codex", "Cursor", "Devin", "GitHub Copilot", "Claude Code"]

# ---------- load + build frame (Sections 0-2) ----------
pr       = pd.read_parquet(DATA_DIR / "pull_request.parquet")
commits  = pd.read_parquet(DATA_DIR / "pr_commits.parquet")
cdetails = pd.read_parquet(DATA_DIR / "pr_commit_details.parquet")
tasktype = pd.read_parquet(DATA_DIR / "pr_task_type.parquet")
repos    = pd.read_parquet(DATA_DIR / "repository.parquet")
for c in ["created_at", "closed_at", "merged_at"]:
    pr[c] = pd.to_datetime(pr[c], errors="coerce", utc=True)

RAW_TO_AGENT = {"openai_codex": "OpenAI Codex", "copilot": "GitHub Copilot",
                "devin": "Devin", "cursor": "Cursor", "claude_code": "Claude Code"}
def norm_agent(x):
    if pd.isna(x): return np.nan
    key = str(x).strip().lower().replace("-", "_").replace(" ", "_")
    if key in RAW_TO_AGENT: return RAW_TO_AGENT[key]
    k2 = key.replace("_", "")
    for raw, canon in RAW_TO_AGENT.items():
        r = raw.replace("_", "")
        if r in k2 or k2 in r: return canon
    return str(x)
pr["agent"] = pr["agent"].map(norm_agent)

pr["is_merged"]   = pr["merged_at"].notna()
pr["is_rejected"] = pr["closed_at"].notna() & pr["merged_at"].isna()
pr["is_open"]     = ~pr["is_merged"] & ~pr["is_rejected"]
pr["decided"]     = pr["is_merged"] | pr["is_rejected"]
pr["merge_time_h"] = (pr["merged_at"] - pr["created_at"]).dt.total_seconds() / 3600

sz = (cdetails.assign(loc=lambda d: d["additions"].fillna(0) + d["deletions"].fillna(0))
              .groupby("pr_id").agg(loc=("loc", "sum"),
                                    files_touched=("filename", "nunique")).reset_index())
ncommits = commits.groupby("pr_id")["sha"].nunique().rename("n_commits").reset_index()
tt = tasktype[["id", "type"]].rename(columns={"id": "pr_join_id", "type": "task_type"})
rf = repos[["id", "stars", "forks", "language"]].rename(columns={"id": "repo_id"})
df = (pr.merge(sz, left_on="id", right_on="pr_id", how="left")
        .merge(ncommits, left_on="id", right_on="pr_id", how="left", suffixes=("", "_c"))
        .merge(tt, left_on="id", right_on="pr_join_id", how="left")
        .merge(rf, on="repo_id", how="left"))
df["log_loc"] = np.log1p(df["loc"].fillna(0))

cell_counts = (df.dropna(subset=["agent"]).groupby(["repo_id", "agent"]).size()
                 .rename("n_prs").reset_index())

def make_panel(K):
    ok = cell_counts[cell_counts["n_prs"] >= K]
    per = ok.groupby("repo_id")["agent"].nunique()
    qual = set(per[per >= MIN_AGENTS_PER_REPO].index)
    # restrict to (repo, agent) cells that themselves clear k, within qualifying repos
    keep_cells = ok[ok["repo_id"].isin(qual)][["repo_id", "agent"]]
    panel = df.merge(keep_cells, on=["repo_id", "agent"], how="inner").copy()
    return panel, qual

import statsmodels.formula.api as smf
from scipy.stats import wilcoxon, kruskal
from scipy.spatial.distance import jensenshannon
from lifelines import CoxPHFitter

def agent_cat(s):
    # put a well-populated agent as reference: OpenAI Codex (hub)
    cats = [a for a in AGENT_ORDER if a in set(s.dropna())]
    return pd.Categorical(s, categories=cats)

RESULTS = {}

def run_partA(panel, K):
    out = {}
    # ---- descriptive within-repo-centered acceptance ----
    ra = (panel.groupby(["repo_id", "agent"])
                .agg(n=("id", "size"), acc_rate=("is_merged", "mean"),
                     med_merge_h=("merge_time_h", "median")).reset_index())
    repo_mean = ra.groupby("repo_id")["acc_rate"].transform("mean")
    ra["acc_rate_centered"] = ra["acc_rate"] - repo_mean
    centered = ra.groupby("agent")["acc_rate_centered"].agg(["mean", "count"]).sort_values("mean", ascending=False)
    out["centered_acc"] = centered
    out["ra"] = ra

    # ---- paired Wilcoxon for every co-occurring pair ----
    wide = ra.pivot_table(index="repo_id", columns="agent", values="acc_rate")
    from itertools import combinations
    pairs = []
    for a, b in combinations([c for c in AGENT_ORDER if c in wide.columns], 2):
        sub = wide[[a, b]].dropna()
        if len(sub) >= 6:
            try:
                stat, p = wilcoxon(sub[a], sub[b])
            except ValueError:
                p = np.nan
            pairs.append({"a": a, "b": b, "n_repos": len(sub),
                          "median_diff_acc": (sub[a] - sub[b]).median(), "p": p})
        else:
            pairs.append({"a": a, "b": b, "n_repos": len(sub),
                          "median_diff_acc": np.nan, "p": np.nan})
    out["paired"] = pd.DataFrame(pairs)

    # ---- FE logit raw vs adjusted (MLE on a common estimable agent set) ----
    # Within-repo FE logit suffers perfect separation when an agent is in too few
    # repos (Claude Code: 4 repos @k=5, 0 @k=10). We detect separation in the RAW
    # model, drop those agents, and fit BOTH raw and adjusted with MLE on the same
    # agent set so the raw->adjusted gap is apples-to-apples. Dropped agents are
    # reported and kept in the robust descriptive / JSD / size analyses.
    m = panel[panel["decided"]].dropna(subset=["agent", "repo_id"]).copy()
    m["repo_id"] = m["repo_id"].astype(str)
    m["is_merged"] = m["is_merged"].astype(int)
    all_ag = [a for a in AGENT_ORDER if a in set(m["agent"])]
    def fit_on(agents_keep, data, adjusted):
        d = data[data["agent"].isin(agents_keep)].copy()
        d["agent"] = pd.Categorical(d["agent"], categories=[a for a in AGENT_ORDER if a in agents_keep])
        f = "is_merged ~ C(agent) + C(repo_id)"
        if adjusted:
            f += " + C(task_type) + log_loc + files_touched"
            d = d.dropna(subset=["task_type", "log_loc", "files_touched"])
        return smf.logit(f, data=d).fit(disp=0, maxiter=300), len(d)
    def ok_fit(fit):
        se = fit.bse.filter(like="C(agent)")
        return len(se) > 0 and np.isfinite(se).all() and (se < 5).all()
    # iteratively drop the least-supported agent (fewest repos) until the raw FE
    # logit converges cleanly; Codex (reference, the hub) is always retained.
    support = m.groupby("agent")["repo_id"].nunique().sort_values()  # least first
    estimable, dropped = list(all_ag), []
    while len(estimable) >= 2:
        try:
            fr, n_raw = fit_on(estimable, m, adjusted=False)
            if ok_fit(fr):
                break
            raise np.linalg.LinAlgError("non-finite/huge SE")
        except Exception:
            drop = next((a for a in support.index if a in estimable and a != "OpenAI Codex"), None)
            if drop is None:
                break
            estimable.remove(drop); dropped.append(drop)
    out["logit_excluded"] = dropped
    fit_raw, n_raw = fit_on(estimable, m, adjusted=False)
    fit_adj, n_adj = fit_on(estimable, m, adjusted=True)
    def agent_terms(fit):
        s = fit.params.filter(like="C(agent)")
        se = fit.bse.filter(like="C(agent)")
        return pd.DataFrame({"coef_logit": s, "odds_ratio": np.exp(s),
                             "se": se, "p": fit.pvalues.filter(like="C(agent)")})
    out["logit_raw"] = agent_terms(fit_raw); out["logit_raw_method"] = "MLE"
    out["logit_adj"] = agent_terms(fit_adj); out["logit_adj_method"] = "MLE"
    out["n_decided"] = n_raw; out["n_adj"] = n_adj

    # ---- Cox PH for merge speed, stratified by repo ----
    surv = panel.copy()
    end = surv["merged_at"].fillna(surv["closed_at"])
    surv["dur_h"] = (end - surv["created_at"]).dt.total_seconds() / 3600
    surv["event"] = surv["is_merged"].astype(int)
    surv = surv[surv["dur_h"] > 0].dropna(subset=["dur_h", "agent"])
    n_censored = int((surv["event"] == 0).sum())
    cox = surv[["dur_h", "event", "agent", "repo_id", "log_loc"]].dropna().copy()
    cox["agent"] = cox["agent"].astype(str)
    cox = pd.get_dummies(cox, columns=["agent"], drop_first=False)
    # drop reference agent (Codex) so HRs are vs Codex; keep others
    ref = "agent_OpenAI Codex"
    if ref in cox.columns:
        cox = cox.drop(columns=[ref])
    cph = CoxPHFitter(penalizer=0.1)
    cph.fit(cox, duration_col="dur_h", event_col="event", strata=["repo_id"])
    summ = cph.summary[["coef", "exp(coef)", "exp(coef) lower 95%", "exp(coef) upper 95%", "p"]]
    out["cox"] = summ; out["cox_n"] = len(cox); out["cox_censored"] = n_censored
    out["cox_ref"] = "OpenAI Codex"
    return out

def run_partB(panel, K):
    out = {}
    # ---- task-type specialization (JSD vs repo baseline) ----
    TASKS = sorted(panel["task_type"].dropna().unique())
    def dist(sub):
        v = sub["task_type"].value_counts().reindex(TASKS).fillna(0).values.astype(float)
        s = v.sum()
        return v / s if s else v
    rows = []
    for rid, repo_df in panel.dropna(subset=["task_type"]).groupby("repo_id"):
        rd = dist(repo_df)
        for ag, ag_df in repo_df.groupby("agent"):
            jsd = jensenshannon(dist(ag_df), rd, base=2)
            rows.append({"repo_id": rid, "agent": ag, "n": len(ag_df), "jsd": jsd})
    spec = pd.DataFrame(rows)
    out["jsd"] = spec.groupby("agent")["jsd"].agg(["mean", "count"]).sort_values("mean", ascending=False)
    out["agent_task_share"] = pd.crosstab(panel["agent"], panel["task_type"], normalize="index").round(3)

    # ---- size specialization ----
    size_m = panel.dropna(subset=["log_loc", "agent"]).copy()
    size_m["repo_id"] = size_m["repo_id"].astype(str)
    size_m["agent"] = agent_cat(size_m["agent"])
    fit_size = smf.ols("log_loc ~ C(agent) + C(repo_id)", data=size_m).fit()
    s = fit_size.params.filter(like="C(agent)")
    out["size_effect"] = pd.DataFrame({"coef_log_loc": s, "p": fit_size.pvalues.filter(like="C(agent)")})
    out["size_median_loc"] = panel.groupby("agent")["loc"].median().sort_values()
    sig = 0; tested = 0
    for rid, g in panel.dropna(subset=["loc"]).groupby("repo_id"):
        groups = [v["loc"].values for _, v in g.groupby("agent") if len(v) >= K]
        if len(groups) >= 2:
            tested += 1
            if kruskal(*groups).pvalue < 0.05:
                sig += 1
    out["kruskal_sig"] = sig; out["kruskal_tested"] = tested
    return out

# ---------- figures ----------
def fig_centered_acc(ra, K):
    g = ra.groupby("agent")["acc_rate_centered"].mean().reindex(
        [a for a in AGENT_ORDER if a in ra["agent"].unique()])
    fig, ax = plt.subplots(figsize=(7, 4))
    colors = ["#c44" if v < 0 else "#4a4" for v in g.values]
    ax.barh(g.index[::-1], g.values[::-1], color=colors[::-1])
    ax.axvline(0, color="k", lw=0.8)
    ax.set_xlabel("Within-repo-centered acceptance (>0 = above repo baseline)")
    ax.set_title(f"Within-repo-centered acceptance by agent (k={K})")
    fig.tight_layout(); fig.savefig(FIG / f"acceptance_centered_k{K}.png", dpi=150); plt.close(fig)

def fig_task_mix(panel, K, topn=8):
    top = (panel.groupby("repo_id").size().sort_values(ascending=False).head(topn).index)
    sub = panel[panel["repo_id"].isin(top)]
    full = repos.set_index("id")["full_name"]
    fig, axes = plt.subplots(2, 4, figsize=(16, 7), sharey=True)
    tasks = sorted(panel["task_type"].dropna().unique())
    cmap = plt.get_cmap("tab20")
    for ax, rid in zip(axes.ravel(), top):
        ct = pd.crosstab(sub[sub["repo_id"] == rid]["agent"],
                         sub[sub["repo_id"] == rid]["task_type"], normalize="index").reindex(columns=tasks).fillna(0)
        ct = ct.reindex([a for a in AGENT_ORDER if a in ct.index])
        bottom = np.zeros(len(ct))
        for i, t in enumerate(tasks):
            ax.bar(range(len(ct)), ct[t].values, bottom=bottom, color=cmap(i % 20), label=t)
            bottom += ct[t].values
        ax.set_xticks(range(len(ct))); ax.set_xticklabels([a.split()[0] for a in ct.index], rotation=45, ha="right", fontsize=8)
        ax.set_title(str(full.get(rid, rid))[:28], fontsize=9)
    for ax in axes.ravel()[len(top):]:
        ax.axis("off")
    handles, labels = axes.ravel()[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=len(tasks), fontsize=8)
    fig.suptitle(f"Task-type mix by agent, top {topn} qualifying repos (k={K})")
    fig.tight_layout(rect=[0, 0.06, 1, 0.97]); fig.savefig(FIG / f"task_mix_k{K}.png", dpi=150); plt.close(fig)

def fig_loc_box(panel, K):
    order = [a for a in AGENT_ORDER if a in panel["agent"].unique()]
    data = [panel[panel["agent"] == a]["log_loc"].dropna().values for a in order]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.boxplot(data, vert=True, labels=[a.split()[0] for a in order], showfliers=False)
    ax.set_ylabel("log(1 + LOC changed)")
    ax.set_title(f"PR size (log LOC) by agent, qualifying panel (k={K})")
    fig.tight_layout(); fig.savefig(FIG / f"loc_box_k{K}.png", dpi=150); plt.close(fig)

for K in K_GRID:
    panel, qual = make_panel(K)
    print("\n" + "#" * 72)
    print(f"#### k = {K}: panel = {len(panel)} PRs across {len(qual)} repos")
    print("#" * 72)
    A = run_partA(panel, K)
    B = run_partB(panel, K)
    RESULTS[K] = {"A": A, "B": B, "n_panel": len(panel), "n_repos": len(qual)}
    fig_centered_acc(A["ra"], K); fig_task_mix(panel, K); fig_loc_box(panel, K)

    print("\n[A] within-repo-centered acceptance by agent:")
    print(A["centered_acc"].round(4).to_string())
    print("\n[A] paired Wilcoxon (acceptance, shared repos):")
    print(A["paired"].round(4).to_string(index=False))
    print(f"\n[A] FE logit excluded for separation: {A['logit_excluded']}")
    print(f"[A] FE logit RAW ({A['logit_raw_method']}, n_decided={A['n_decided']}, ref=OpenAI Codex):")
    print(A["logit_raw"].round(4).to_string())
    print(f"[A] FE logit ADJUSTED for task+size ({A['logit_adj_method']}, n={A['n_adj']}):")
    print(A["logit_adj"].round(4).to_string())
    print(f"\n[A] Cox PH (strata=repo, penalizer=0.1, n={A['cox_n']}, censored={A['cox_censored']}, ref={A['cox_ref']}):")
    print(A["cox"].round(4).to_string())
    print("\n[B] task specialization JSD by agent:")
    print(B["jsd"].round(4).to_string())
    print("\n[B] agent x task share:")
    print(B["agent_task_share"].to_string())
    print("\n[B] within-repo size effect (log LOC, ref=OpenAI Codex):")
    print(B["size_effect"].round(4).to_string())
    print("\n[B] median raw LOC by agent:")
    print(B["size_median_loc"].round(1).to_string())
    print(f"[B] repos w/ significant within-repo size diff (Kruskal p<.05): {B['kruskal_sig']}/{B['kruskal_tested']}")

print("\n\nFIGURES:", sorted(p.name for p in FIG.glob("*.png")))
print("DONE")
