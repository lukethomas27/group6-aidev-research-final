"""
Review Engagement Framework — Analysis Pipeline
SENG404 Interim Report

Research question:
    How do reviewers engage with AI-authored pull requests, and does that
    engagement differ by agent, task type, and repository context?

Two-stage framework
-------------------
Stage 1  (all PRs)
    Coverage       — Was the PR reviewed by a human?
                     DV: has_human_review  (binary)

Stage 2  (PRs with at least one human review)
    Responsiveness — How quickly did review arrive?
                     DV: ttfr_h / repo_median_ttfr_h  (survival, all PRs right-censored)
    Scrutiny       — Did reviewers request changes?
                     DV: changes_requested  (binary)
    Intensity      — How much review activity occurred?
                     DV: n_inline_human     (count — inline code comments, human only)
                     DV: n_discussion_human (count — issue-thread comments, human only)
    Low-Friction   — Was the PR approved with little or no iteration?
    Approval         DV: low_friction_approval  (binary)

Models
------
    M1   Logistic           Coverage
    M2   Weibull AFT        Responsiveness     (right-censors unreviewed PRs)
    M3   Logistic           Scrutiny           (reviewed PRs only)
    M4a  Negative binomial  Intensity — inline (all PRs, zero-inflated by design)
    M4b  Negative binomial  Intensity — discussion
    M5   Logistic           Low-Friction Approval (reviewed PRs only)

All logistic models use cluster-robust SEs by repo_id.
Reference agent: OpenAI Codex (matches teammate Luke's section).
"""

# ---------------------------------------------------------------------------
# 0. Imports
# ---------------------------------------------------------------------------
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
from pathlib import Path
from scipy.stats import chi2 as chi2_dist

import statsmodels.formula.api as smf
from statsmodels.stats.proportion import proportion_confint
from lifelines import WeibullAFTFitter, KaplanMeierFitter

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR   = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "results"
OUTPUT_DIR.mkdir(exist_ok=True)

SNAPSHOT  = pd.Timestamp("2025-08-01", tz="UTC")
REF_AGENT = "OpenAI_Codex"
MIN_CELL_N = 30   # mask heatmap cells with fewer PRs

# ---------------------------------------------------------------------------
# 1. Load tables
# ---------------------------------------------------------------------------
print("Loading parquet files...")

pr       = pd.read_parquet(DATA_DIR / "pull_request.parquet")
reviews  = pd.read_parquet(DATA_DIR / "pr_reviews.parquet")
comments = pd.read_parquet(DATA_DIR / "pr_comments.parquet")
inline   = pd.read_parquet(DATA_DIR / "pr_review_comments_v2.parquet")
tasks    = pd.read_parquet(DATA_DIR / "pr_task_type.parquet")
repos    = pd.read_parquet(DATA_DIR / "repository.parquet")
commits  = pd.read_parquet(DATA_DIR / "pr_commits.parquet")

try:
    details = pd.read_parquet(
        DATA_DIR / "pr_commit_details.parquet",
        columns=["pr_id", "additions", "deletions", "filename"]
    )
    HAS_DETAILS = True
    print("  pr_commit_details loaded.")
except FileNotFoundError:
    HAS_DETAILS = False
    print("  pr_commit_details not found — using commit count only for complexity.")

# ---------------------------------------------------------------------------
# 2. Parse timestamps
# ---------------------------------------------------------------------------
for col in ["created_at", "closed_at", "merged_at"]:
    pr[col] = pd.to_datetime(pr[col], utc=True, errors="coerce")
reviews["submitted_at"] = pd.to_datetime(reviews["submitted_at"], utc=True, errors="coerce")
comments["created_at"]  = pd.to_datetime(comments["created_at"],  utc=True, errors="coerce")

# ---------------------------------------------------------------------------
# 3. Normalise agent labels to snake_case (formula-safe)
# ---------------------------------------------------------------------------
# Raw agent label values present in the dataset
AGENT_ORDER  = ["OpenAI_Codex", "Copilot", "Devin", "Cursor", "Claude_Code"]
AGENT_LABELS = {
    "OpenAI_Codex":  "OpenAI Codex",
    "Copilot":       "GitHub Copilot",
    "Devin":         "Devin",
    "Cursor":        "Cursor",
    "Claude_Code":   "Claude Code",
}

# ---------------------------------------------------------------------------
# 4. Split reviews: human vs bot
# ---------------------------------------------------------------------------
human_rev = reviews[reviews["user_type"] == "User"].copy()
bot_rev   = reviews[reviews["user_type"] == "Bot"].copy()

# ---------------------------------------------------------------------------
# 5. Aggregate human review signals per PR
# ---------------------------------------------------------------------------
hr_agg = (
    human_rev
    .sort_values("submitted_at")
    .groupby("pr_id")
    .agg(
        n_human_reviews     = ("id",           "count"),
        first_review_at     = ("submitted_at", "first"),
        n_changes_requested = ("state", lambda x: (x == "CHANGES_REQUESTED").sum()),
        n_approvals         = ("state", lambda x: (x == "APPROVED").sum()),
    )
    .reset_index()
)

bot_agg = (
    bot_rev.groupby("pr_id")
           .agg(n_bot_reviews=("id", "count"))
           .reset_index()
)

# ---------------------------------------------------------------------------
# 6. Aggregate comment volume — human authors only, inline vs discussion
# ---------------------------------------------------------------------------
# Inline review comments (pr_review_comments_v2):
#   These link to pr_id via pull_request_review_id -> reviews.id -> reviews.pr_id
#   We include only reviews authored by humans.
human_review_ids = set(human_rev["id"])
inline_human = inline[inline["pull_request_review_id"].isin(human_review_ids)].copy()

inline_per_review = (
    inline_human.groupby("pull_request_review_id")
                .size().rename("n_inline").reset_index()
)
inline_per_pr = (
    reviews[["id", "pr_id"]]
    .merge(inline_per_review, left_on="id", right_on="pull_request_review_id", how="left")
    .groupby("pr_id")["n_inline"].sum()
    .reset_index()
    .rename(columns={"n_inline": "n_inline_human"})
)

# Issue-thread discussion comments (pr_comments):
#   Filter to human authors only
discussion_human = comments[comments["user_type"] == "User"]
discussion_per_pr = (
    discussion_human.groupby("pr_id")
                    .size().rename("n_discussion_human")
                    .reset_index()
)

# ---------------------------------------------------------------------------
# 7. Complexity controls
# ---------------------------------------------------------------------------
commit_count = (
    commits.groupby("pr_id")["sha"]
           .nunique().rename("commit_count")
           .reset_index()
)

if HAS_DETAILS:
    complexity = (
        details.groupby("pr_id")
               .agg(
                   total_additions = ("additions", "sum"),
                   total_deletions = ("deletions", "sum"),
                   files_changed   = ("filename",  "nunique"),
               )
               .reset_index()
    )

# ---------------------------------------------------------------------------
# 8. Build master dataframe — one row per PR
# ---------------------------------------------------------------------------
print("Joining tables...")

# Rename the join key in every aggregated table to "id" so the merge chain
# does not accumulate duplicate pr_id columns.
def rekey(frame):
    return frame.rename(columns={"pr_id": "id"})

df = (
    pr
    .merge(tasks[["id", "type"]], on="id", how="left")
    .merge(
        repos[["id", "stars", "language"]],
        left_on="repo_id", right_on="id",
        how="left", suffixes=("", "_repo")
    )
    .merge(rekey(hr_agg),            on="id", how="left")
    .merge(rekey(bot_agg),           on="id", how="left")
    .merge(rekey(inline_per_pr),     on="id", how="left")
    .merge(rekey(discussion_per_pr), on="id", how="left")
    .merge(rekey(commit_count),      on="id", how="left")
)

if HAS_DETAILS:
    df = df.merge(rekey(complexity), on="id", how="left")

# Fill missing counts with zero
zero_cols = [
    "n_human_reviews", "n_changes_requested", "n_approvals",
    "n_bot_reviews", "n_inline_human", "n_discussion_human", "commit_count",
]
if HAS_DETAILS:
    zero_cols += ["total_additions", "total_deletions", "files_changed"]

for col in zero_cols:
    if col in df.columns:
        df[col] = df[col].fillna(0).astype(int)

# ---------------------------------------------------------------------------
# 9. Derive dependent variables
# ---------------------------------------------------------------------------

# Stage 1 ——————————————————————————————————————————————————————————————————

# DV: Coverage
df["has_human_review"] = (df["n_human_reviews"] > 0).astype(int)

# Stage 2 ——————————————————————————————————————————————————————————————————

# DV: Responsiveness — normalized time to first human review
df["first_review_at"] = pd.to_datetime(df["first_review_at"], utc=True, errors="coerce")
df["ttfr_h"] = (
    (df["first_review_at"] - df["created_at"])
    .dt.total_seconds() / 3600
)

# Repo-level median TTFR: computed over reviewed PRs in the same repo
repo_baseline = (
    df.loc[df["ttfr_h"].notna(), ["repo_id", "ttfr_h"]]
    .groupby("repo_id")["ttfr_h"]
    .median()
    .rename("repo_median_ttfr_h")
)
df = df.join(repo_baseline, on="repo_id")
df["ttfr_norm"] = df["ttfr_h"] / df["repo_median_ttfr_h"]

# Survival analysis inputs (right-censor PRs that have not yet received a review)
df["ttfr_observed"] = df["first_review_at"].notna().astype(int)
censor_h = (SNAPSHOT - df["created_at"]).dt.total_seconds() / 3600
df["ttfr_duration"] = pd.to_numeric(
    df["ttfr_h"].fillna(censor_h), errors="coerce"
).astype(float)
df = df[df["ttfr_duration"].notna() & (df["ttfr_duration"] > 0)]

# DV: Scrutiny (binary; defined for reviewed PRs — set NaN for unreviewed)
df["changes_requested"] = np.where(
    df["has_human_review"] == 1,
    (df["n_changes_requested"] > 0).astype(int),
    np.nan
)

# DV: Intensity — inline review comments (human, code-level)
#     n_inline_human already computed; treat 0 as no inline feedback

# DV: Intensity — discussion comments (human, issue-thread)
#     n_discussion_human already computed

# DV: Low-Friction Approval
#   Operationalization: approved AND zero CHANGES_REQUESTED rounds
#   Defined only for reviewed PRs; NaN for unreviewed
df["low_friction_approval"] = np.where(
    df["has_human_review"] == 1,
    ((df["n_approvals"] > 0) & (df["n_changes_requested"] == 0)).astype(int),
    np.nan
)

# ---------------------------------------------------------------------------
# 10. Log-transform controls; collapse rare language levels
# ---------------------------------------------------------------------------
df["log_stars"]   = np.log1p(df["stars"])
df["log_commits"] = np.log1p(df["commit_count"])

if HAS_DETAILS:
    df["log_additions"] = np.log1p(df["total_additions"])
    df["log_deletions"] = np.log1p(df["total_deletions"])
    df["log_files"]     = np.log1p(df["files_changed"])
    COMPLEXITY = "+ log_commits + log_additions + log_deletions + log_files"
else:
    COMPLEXITY = "+ log_commits"

df_model = df.dropna(subset=["agent", "type", "log_stars"]).copy()

top_langs = df_model["language"].value_counts().head(10).index
df_model["lang_group"] = df_model["language"].where(
    df_model["language"].isin(top_langs), other="other"
)

# Subsets for stage-2 models
reviewed = df_model[df_model["has_human_review"] == 1].copy()

print(f"\nFull analytical dataset:   {len(df_model):,} PRs, {df_model['repo_id'].nunique():,} repos")
print(f"Reviewed subset (Stage 2): {len(reviewed):,} PRs")
print("\nPR counts by agent:")
print(df_model["agent"].value_counts())

# ---------------------------------------------------------------------------
# 11. Inter-construct correlation check (Table 2)
# ---------------------------------------------------------------------------
corr_vars = {
    "Coverage":          "has_human_review",
    "Scrutiny":          "changes_requested",
    "Inline intensity":  "n_inline_human",
    "Discussion":        "n_discussion_human",
    "Low-friction appr.":"low_friction_approval",
}
corr_df = df_model[[v for v in corr_vars.values()]].copy()
corr_df.columns = list(corr_vars.keys())
table2 = corr_df.corr(method="spearman").round(3)
print("\nTable 2 — Spearman inter-construct correlations:")
print(table2.to_string())
table2.to_csv(OUTPUT_DIR / "table2_correlations.csv")

# ---------------------------------------------------------------------------
# 12. Descriptive statistics — Table 1
# ---------------------------------------------------------------------------
print("\nBuilding Table 1...")

def pct(x):
    return x.mean() * 100

t1_all = df_model.groupby("agent").agg(
    n_prs             = ("id",                  "count"),
    pct_covered       = ("has_human_review",    pct),
    median_ttfr_h     = ("ttfr_h",              "median"),
    median_inline     = ("n_inline_human",      "median"),
    median_discussion = ("n_discussion_human",  "median"),
).round(1)

t1_rev = reviewed.groupby("agent").agg(
    pct_scrutinized   = ("changes_requested",     pct),
    pct_low_friction  = ("low_friction_approval", pct),
).round(1)

table1 = t1_all.join(t1_rev)
print(table1.to_string())
table1.to_csv(OUTPUT_DIR / "table1_descriptives.csv")

# ---------------------------------------------------------------------------
# 13. Visualisations
# ---------------------------------------------------------------------------
print("\nGenerating figures...")

# ── Figure 1: Coverage rate per agent ──────────────────────────────────────
cov = (df_model.groupby("agent")["has_human_review"]
               .agg(["sum", "count"])
               .reindex(AGENT_ORDER))
cov["pct"] = cov["sum"] / cov["count"] * 100
lo, hi = proportion_confint(cov["sum"], cov["count"], method="wilson")

fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(range(len(cov)), cov["pct"], color="steelblue")
ax.errorbar(range(len(cov)), cov["pct"],
            yerr=[cov["pct"] - lo * 100, hi * 100 - cov["pct"]],
            fmt="none", color="black", capsize=4)
ax.set_xticks(range(len(cov)))
ax.set_xticklabels([AGENT_LABELS[a] for a in AGENT_ORDER])
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.set_ylabel("PRs receiving ≥1 human review (%)")
ax.set_title("Figure 1: Human review coverage by agent (with 95% Wilson CI)")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "fig1_coverage_by_agent.png", dpi=150)
plt.close()

# ── Figure 2: Coverage heatmap — agent × task type ─────────────────────────
def heatmap_rate(data, dv, title, filename, cmap="Blues", vmax=100):
    cells = (data.groupby(["agent", "type"])[dv]
                 .agg(rate=lambda x: x.dropna().mean(), n="count")
                 .reset_index())
    pivot_r = cells.pivot(index="agent", columns="type", values="rate").reindex(AGENT_ORDER)
    pivot_n = cells.pivot(index="agent", columns="type", values="n").reindex(AGENT_ORDER)
    mask    = pivot_n < MIN_CELL_N

    fig, ax = plt.subplots(figsize=(13, 4))
    sns.heatmap(pivot_r * 100, annot=True, fmt=".0f", mask=mask,
                cmap=cmap, vmin=0, vmax=vmax, ax=ax,
                cbar_kws={"label": "Rate (%)"})
    ax.set_yticklabels([AGENT_LABELS.get(a, a) for a in pivot_r.index], rotation=0)
    ax.set_title(title + f"\n(cells with N < {MIN_CELL_N} masked)")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, dpi=150)
    plt.close()

heatmap_rate(df_model, "has_human_review",
             "Figure 2: Review coverage rate by agent × task type",
             "fig2_coverage_heatmap.png", cmap="Blues")

# ── Figure 3: Scrutiny rate heatmap — agent × task type ────────────────────
heatmap_rate(reviewed, "changes_requested",
             "Figure 3: Scrutiny (CHANGES_REQUESTED) rate by agent × task type\n(reviewed PRs only)",
             "fig3_scrutiny_heatmap.png", cmap="RdYlGn_r")

# ── Figure 4: Engagement profile — stacked bar ─────────────────────────────
# For each agent, show share of PRs in four reviewer engagement states:
#   no review | low-friction approval | approved after iteration | changes requested (open/not merged)
def engagement_state(row):
    if row["has_human_review"] == 0:
        return "No review"
    if row["n_changes_requested"] > 0:
        return "Changes requested"
    if row["n_approvals"] > 0:
        return "Low-friction approval"
    return "Reviewed, no decision"

df_model["engagement_state"] = df_model.apply(engagement_state, axis=1)

state_order  = ["No review", "Low-friction approval", "Reviewed, no decision", "Changes requested"]
state_colors = ["#d9d9d9", "#a1c9f4", "#6baed6", "#d62728"]

state_pct = (
    df_model.groupby("agent")["engagement_state"]
            .value_counts(normalize=True)
            .mul(100)
            .unstack(fill_value=0)
            .reindex(AGENT_ORDER)[state_order]
)

fig, ax = plt.subplots(figsize=(8, 4))
state_pct.plot(kind="bar", stacked=True, color=state_colors, ax=ax, width=0.6)
ax.set_xticklabels([AGENT_LABELS[a] for a in AGENT_ORDER], rotation=0)
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.set_ylabel("Share of PRs (%)")
ax.set_title("Figure 4: Reviewer engagement profile per agent")
ax.legend(loc="lower right", fontsize=8)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "fig4_engagement_profile.png", dpi=150)
plt.close()

# ── Figure 5: Kaplan-Meier — time to first human review ────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
for agent in AGENT_ORDER:
    grp = df_model[df_model["agent"] == agent]
    KaplanMeierFitter(label=AGENT_LABELS[agent]).fit(
        grp["ttfr_duration"], grp["ttfr_observed"]
    ).plot_survival_function(ax=ax, ci_show=False)
ax.set_xlim(0, 336)
ax.set_xlabel("Hours since PR opened")
ax.set_ylabel("Proportion not yet reviewed")
ax.set_title("Figure 5: Time to first human review (Kaplan-Meier)")
ax.legend(fontsize=8)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "fig5_km_ttfr.png", dpi=150)
plt.close()

# ── Figure 6: Intensity comparison — inline vs discussion, per agent ────────
int_agg = df_model.groupby("agent")[["n_inline_human", "n_discussion_human"]].median().reindex(AGENT_ORDER)
int_agg.index = [AGENT_LABELS[a] for a in AGENT_ORDER]

fig, ax = plt.subplots(figsize=(7, 4))
x = np.arange(len(int_agg))
w = 0.35
ax.bar(x - w/2, int_agg["n_inline_human"],    w, label="Inline review comments", color="steelblue")
ax.bar(x + w/2, int_agg["n_discussion_human"], w, label="Discussion comments",    color="coral")
ax.set_xticks(x)
ax.set_xticklabels(int_agg.index)
ax.set_ylabel("Median count per PR")
ax.set_title("Figure 6: Review intensity (median comment counts) by agent")
ax.legend()
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "fig6_intensity_by_agent.png", dpi=150)
plt.close()

print("Figures saved.")

# ---------------------------------------------------------------------------
# 14. Models
# ---------------------------------------------------------------------------
print("\nFitting models...")

AGENT_TERM = f"C(agent, Treatment('{REF_AGENT}'))"
CONTROLS   = f"+ C(type, Treatment('feat')) + log_stars + C(lang_group) {COMPLEXITY}"
CLUSTER    = {"cov_type": "cluster", "cov_kwds": {"groups": df_model["repo_id"]}}
CLUSTER_R  = {"cov_type": "cluster", "cov_kwds": {"groups": reviewed["repo_id"]}}


def fit_logit(formula, data, cluster_groups, label):
    print(f"\n[{label}]")
    # Try Newton-Raphson first; fall back to BFGS if Hessian is singular
    # (can happen in small reviewed subsets with sparse agent×task cells)
    for method in ("newton", "bfgs"):
        try:
            m = smf.logit(formula, data=data).fit(
                method=method,
                cov_type="cluster",
                cov_kwds={"groups": cluster_groups},
                disp=False,
            )
            print(m.summary2())
            return m
        except (np.linalg.LinAlgError, Exception) as e:
            if method == "bfgs":
                raise
            print(f"  Newton failed ({e}), retrying with BFGS...")
    return None


# M1: Coverage (all PRs)
m1 = fit_logit(
    f"has_human_review ~ {AGENT_TERM} {CONTROLS}",
    df_model, df_model["repo_id"], "M1: Coverage"
)

# M3: Scrutiny (reviewed PRs)
m3 = fit_logit(
    f"changes_requested ~ {AGENT_TERM} {CONTROLS}",
    reviewed, reviewed["repo_id"], "M3: Scrutiny"
)

# M4a: Intensity — inline comments (all PRs, negative binomial)
print("\n[M4a: Intensity — inline review comments]")
m4a = smf.negativebinomial(
    f"n_inline_human ~ {AGENT_TERM} {CONTROLS}",
    data=df_model
).fit(disp=False)
print(m4a.summary())

# M4b: Intensity — discussion comments (all PRs, negative binomial)
print("\n[M4b: Intensity — discussion comments]")
m4b = smf.negativebinomial(
    f"n_discussion_human ~ {AGENT_TERM} {CONTROLS}",
    data=df_model
).fit(disp=False)
print(m4b.summary())

# M5: Low-Friction Approval (reviewed PRs)
m5 = fit_logit(
    f"low_friction_approval ~ {AGENT_TERM} {CONTROLS}",
    reviewed, reviewed["repo_id"], "M5: Low-Friction Approval"
)

# ---------------------------------------------------------------------------
# 15. Responsiveness — Weibull AFT (M2)
# ---------------------------------------------------------------------------
print("\n[M2: Responsiveness — Weibull AFT]")

aft_cat_cols = ["agent", "type", "lang_group"]
aft_data = (
    df_model[["ttfr_duration", "ttfr_observed", "log_stars", "log_commits"]
             + aft_cat_cols
             + (["log_additions", "log_deletions", "log_files"] if HAS_DETAILS else [])]
    .dropna().copy()
)
aft_data = pd.get_dummies(aft_data, columns=aft_cat_cols, drop_first=False)

# Drop reference levels
for ref_col in [f"agent_{REF_AGENT}", "type_feat", "lang_group_other"]:
    if ref_col in aft_data.columns:
        aft_data.drop(columns=[ref_col], inplace=True)

aft = WeibullAFTFitter(penalizer=0.01)
aft.fit(aft_data, duration_col="ttfr_duration", event_col="ttfr_observed")
aft.print_summary(decimals=3)
aft.params_.to_csv(OUTPUT_DIR / "m2_aft_params.csv")

# ---------------------------------------------------------------------------
# 16. Repo-context moderation test (M3b: Scrutiny × log_stars)
# ---------------------------------------------------------------------------
print("\n[M3b: Scrutiny — agent × log_stars interaction]")
m3b = smf.logit(
    f"changes_requested ~ C(agent, Treatment('{REF_AGENT}')) * log_stars "
    f"+ C(type) + C(lang_group) {COMPLEXITY}",
    data=reviewed
).fit(cov_type="cluster", cov_kwds={"groups": reviewed["repo_id"]}, disp=False)

lr_stat   = 2 * (m3b.llf - m3.llf)
n_extra   = m3b.df_model - m3.df_model
p_val     = chi2_dist.sf(lr_stat, df=n_extra)
print(f"LR test (interaction vs. main effects): chi2={lr_stat:.2f}, df={n_extra}, p={p_val:.4f}")
if p_val < 0.05:
    print("  -> Significant: repo reputation moderates scrutiny toward different agents.")
else:
    print("  -> Not significant: scrutiny differences are consistent across repo sizes.")

# ---------------------------------------------------------------------------
# 17. Forest plot — agent odds ratios across M1, M3, M5 (Figure 7)
# ---------------------------------------------------------------------------
agent_terms = [t for t in m1.params.index if "agent" in t and REF_AGENT not in t]
extracted = pd.Series(agent_terms).str.extract(r"\[T\.(.*?)\]")[0]
clean_labels = extracted.map(AGENT_LABELS).fillna(extracted).tolist()

fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharey=True)
for ax, (model, title) in zip(axes, [
    (m1,  "M1: Coverage"),
    (m3,  "M3: Scrutiny"),
    (m5,  "M5: Low-Friction Approval"),
]):
    vals  = np.exp(model.params[agent_terms])
    lo_ci = np.exp(model.conf_int().loc[agent_terms, 0])
    hi_ci = np.exp(model.conf_int().loc[agent_terms, 1])
    y     = range(len(vals))

    ax.errorbar(vals, y, xerr=[vals - lo_ci, hi_ci - vals],
                fmt="o", color="steelblue", capsize=4)
    ax.axvline(1, color="black", linewidth=0.8, linestyle="--")
    ax.set_yticks(list(y))
    ax.set_yticklabels(clean_labels)
    ax.set_xlabel("Odds ratio vs. Codex")
    ax.set_title(title)

plt.suptitle("Figure 7: Agent odds ratios (vs. OpenAI Codex) — coverage, scrutiny, low-friction approval",
             y=1.02, fontsize=10)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "fig7_forest_plot.png", dpi=150, bbox_inches="tight")
plt.close()

# ---------------------------------------------------------------------------
# 18. Export odds-ratio tables
# ---------------------------------------------------------------------------
for label, model in [("m1_coverage", m1), ("m3_scrutiny", m3), ("m5_lowfriction", m5)]:
    pd.DataFrame({
        "OR":    np.exp(model.params),
        "CI_lo": np.exp(model.conf_int()[0]),
        "CI_hi": np.exp(model.conf_int()[1]),
        "p":     model.pvalues,
    }).to_csv(OUTPUT_DIR / f"{label}_OR.csv")

print(f"\nAll outputs saved to {OUTPUT_DIR}")
print("Done.")
