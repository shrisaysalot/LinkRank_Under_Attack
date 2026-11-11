"""Publication Figures Generator (v3) - 300 DPI, Large Fonts, High-Contrast Style."""
import sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.eval.stats import bootstrap_ci

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 14
})


def plot_h2_takeover():
    print("Generating H2 spectral takeover figure...")
    df = pd.read_csv("results/h2_robustness_v3.csv")
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), dpi=300)

    # Panel A: Ratio p*(10) / sigma1^2 across graphs
    ax1 = axes[0]
    graphs = sorted(df["graph"].unique())
    clean_names = [g.replace("Synthetic_", "").replace("SNAP_", "").replace("_BaseSet", "") for g in graphs]

    means, lowers, uppers = [], [], []
    for g in graphs:
        sub = df[df["graph"] == g]["ratio_p_star_10_to_sigma1_sq"].dropna().values
        m, l, u = bootstrap_ci(sub)
        means.append(m)
        lowers.append(m - l)
        uppers.append(u - m)

    x_pos = np.arange(len(graphs))
    ax1.bar(x_pos, means, yerr=[lowers, uppers], capsize=5, color="#4c72b0", edgecolor="black", alpha=0.85, width=0.55)
    ax1.axhline(1.0, color="red", linestyle="--", linewidth=1.8, label=r"Theoretical Barrier: $p = \sigma_1^2$")
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(clean_names, rotation=15, ha="right", fontweight="bold")
    ax1.set_ylabel(r"Takeover Ratio $p^*(10) / \sigma_1^2$", fontweight="bold")
    ax1.set_title(r"(a) Normalized Critical Budget $p^*(10) / \sigma_1^2$", fontweight="bold")
    ax1.legend(loc="upper left", frameon=True)
    ax1.grid(True, linestyle="--", alpha=0.5)

    # Panel B: Step jump (Abruptness: HITS vs PageRank)
    ax2 = axes[1]
    h_jumps = df["max_hits_step_jump"].values
    pr_jumps = df["max_pagerank_step_jump"].values

    box_data = [h_jumps, pr_jumps]
    bp = ax2.boxplot(box_data, patch_artist=True, labels=["HITS\n(Spectral Snap)", "PageRank\n(Damped Random Walk)"], widths=0.45)
    colors = ["#c44e52", "#55a868"]
    for patch, c in zip(bp["boxes"], colors):
        patch.set_facecolor(c)
        patch.set_alpha(0.8)

    ax2.set_ylabel("Maximum Single-Step Rank Gain", fontweight="bold")
    ax2.set_title(r"(b) Takeover Abruptness: HITS vs PageRank", fontweight="bold")
    ax2.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    out_path = Path("figures/h2_takeover_v3.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    print(f"Saved {out_path}")


def plot_defense_tradeoff():
    print("Generating Defense Trade-Off figure...")
    df = pd.read_csv("results/defenses_eval_v3.csv")
    df_pos = df[df["base_gain"] > 0]

    fig, ax = plt.subplots(figsize=(9, 6), dpi=300)

    # Shade goal region: Reduction >= 50% and Clean NDCG Loss <= 5%
    ax.axvspan(0, 0.05 * 100, ymin=0.5, ymax=1.0, color="#2ca02c", alpha=0.15, label="Target Quadrant (Red >= 50%, Loss <= 5%)")

    def_names = sorted(df["defense"].unique())
    markers = ["o", "s", "^", "D", "v", "P", "*", "X", "<", ">", "d"]
    colors = plt.cm.tab10(np.linspace(0, 1, len(def_names)))

    for i, d in enumerate(def_names):
        sub = df_pos[df_pos["defense"] == d]
        all_sub = df[df["defense"] == d]
        red_pct = sub["attack_reduction"].median() * 100.0
        loss_pct = all_sub["clean_ndcg_loss"].mean() * 100.0

        short_d = d.replace("D4_WuDavison_Mutual_0.5", "D4 (Mutual)") \
                   .replace("D4b_WuDavison_OutJaccard_0.5", "D4b (Out-Jaccard)") \
                   .replace("D1_RandomizedHITS_0.15", "D1 (Randomized)") \
                   .replace("D3_HubCapping_0.01", "D3 (Hub Cap 1%)") \
                   .replace("D5_TrustHITS_PageRankSeeds", "D5 (PageRank Seeds)") \
                   .replace("D5_TrustHITS_InDegreeSeeds", "D5 (In-Degree Seeds)") \
                   .replace("Undefended_HITS", "Undefended HITS") \
                   .replace("D1_SubspaceHITS", "D1 (Subspace)") \
                   .replace("D2_BharatHenzinger", "D2 (Bharat-Henzinger)") \
                   .replace("Combined_D4_plus_D1", "Combined (D4+D1)") \
                   .replace("Combined_D4_plus_D5", "Combined (D4+D5)")

        ax.scatter(loss_pct, red_pct, label=short_d, color=colors[i], marker=markers[i % len(markers)], s=80, edgecolors="black", linewidth=1.2, zorder=5)

    ax.set_xlabel("Clean NDCG@20 Loss (%) [Lower is Better]", fontweight="bold")
    ax.set_ylabel("Median Attack Reduction (%) [Higher is Better]", fontweight="bold")
    ax.set_title("Defense Security vs Clean Utility Trade-Off Matrix", fontweight="bold")
    ax.axhline(50, color="gray", linestyle=":", alpha=0.7)
    ax.axvline(5, color="gray", linestyle=":", alpha=0.7)
    ax.set_xlim(-1, 65)
    ax.set_ylim(-30, 105)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", frameon=True, fontsize=9)
    ax.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    out_path = Path("figures/defense_tradeoff_v3.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    print(f"Saved {out_path}")


def plot_cost_curves_per_attack():
    print("Generating Cost Curves per Attack figure...")
    df = pd.read_csv("results/cost_curves_v3.csv")
    attacks = sorted(df["attack"].unique())
    budgets = sorted(df["budget"].unique())

    # Create 2 x 4 grid for 7 attacks
    fig, axes = plt.subplots(2, 4, figsize=(16, 8), dpi=300, sharex=True, sharey=True)
    axes = axes.flatten()

    ranker_colors = {
        "HITS": "#d62728",
        "PageRank": "#2ca02c",
        "SALSA": "#1f77b4",
        "InDegree": "#9467bd"
    }

    for idx, att in enumerate(attacks):
        ax = axes[idx]
        att_df = df[df["attack"] == att]

        for r_name in ["HITS", "PageRank", "SALSA", "InDegree"]:
            rdf = att_df[att_df["ranker"] == r_name]
            means, lowers, uppers = [], [], []

            for b in budgets:
                sub_b = rdf[rdf["budget"] == b]["normalized_rank_gain"].values
                if len(sub_b) > 0:
                    m, l, u = bootstrap_ci(sub_b)
                else:
                    m, l, u = 0.0, 0.0, 0.0
                means.append(m)
                lowers.append(l)
                uppers.append(u)

            ax.plot(budgets, means, label=r_name, color=ranker_colors[r_name], linewidth=2.0)
            ax.fill_between(budgets, lowers, uppers, color=ranker_colors[r_name], alpha=0.18)

        short_att = att.replace("_ProposalInflation", " (Proposal)") \
                       .replace("_ProposalCrossScore", " (Cross-Score)") \
                       .replace("_CrossScoreLinks", " (Cross-Links)") \
                       .replace("_GreedyGradient", " (Greedy)")
        ax.set_title(f"{short_att}", fontweight="bold", fontsize=11)
        ax.set_xscale("log")
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, linestyle="--", alpha=0.5)

        if idx in [0, 4]:
            ax.set_ylabel("Norm. Rank Gain", fontweight="bold")
        if idx >= 3:
            ax.set_xlabel("Edge Budget B (Log Scale)", fontweight="bold")

    # Hide 8th subplot
    axes[7].axis("off")
    # Put common legend in 8th slot
    handles, labels = axes[0].get_legend_handles_labels()
    axes[7].legend(handles, labels, loc="center", frameon=True, fontsize=12, title="Algorithm", title_fontsize=12)

    plt.suptitle("Adversarial Cost Curves Across All 7 Attack Families (with 95% Bootstrap CIs)", fontsize=14, fontweight="bold")
    plt.tight_layout()
    out_path = Path("figures/cost_curves_v3.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    print(f"Saved {out_path}")


if __name__ == "__main__":
    plot_h2_takeover()
    plot_defense_tradeoff()
    plot_cost_curves_per_attack()

