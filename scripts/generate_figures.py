"""Generate publication-ready figures (300 DPI) and system architecture diagram."""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd

from src.config import RESULTS_DIR, FIGURES_DIR

# Set global publication styling
plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 13,
    "axes.titlesize": 13,
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
    "legend.fontsize": 11,
    "figure.titlesize": 15,
    "lines.linewidth": 2.2,
    "lines.markersize": 7,
    "figure.autolayout": True,
})


def plot_cost_curves():
    # Prefer cost_curves_v2.csv
    csv_path = RESULTS_DIR / "cost_curves_v2.csv"
    if not csv_path.exists():
        csv_path = RESULTS_DIR / "cost_curves.csv"

    if not csv_path.exists():
        print(f"[SKIP] No cost curves CSV found.")
        return

    df = pd.read_csv(csv_path)
    graphs = df["graph"].unique()
    n_graphs = len(graphs)

    fig, axes = plt.subplots(1, n_graphs, figsize=(5 * n_graphs, 5), sharey=True)
    if n_graphs == 1:
        axes = [axes]

    colors = {"HITS": "#D9534F", "PageRank": "#337AB7", "SALSA": "#5CB85C", "InDegree": "#F0AD4E"}
    markers = {"HITS": "o", "PageRank": "s", "SALSA": "^", "InDegree": "d"}

    title_map = {
        "Synthetic_BA_500": "Scale-Free (BA-500)",
        "Synthetic_ER_500": "Random (ER-500)",
        "Synthetic_SBM_500": "Planted SBM-500",
        "SNAP_web-Stanford_BaseSet": "SNAP web-Stanford BaseSet",
        "SNAP_wiki-Vote_BaseSet": "SNAP wiki-Vote BaseSet",
    }

    for idx, g_name in enumerate(graphs):
        ax = axes[idx]
        sub_df = df[df["graph"] == g_name]

        for ranker in ["HITS", "PageRank", "SALSA", "InDegree"]:
            r_df = sub_df[sub_df["ranker"] == ranker]
            agg = r_df.groupby("budget")["rank_gain"].agg(["mean", "std", "count"]).reset_index()

            # Bootstrap CI or standard error for CI band
            ci_half = 1.96 * agg["std"].fillna(0) / np.sqrt(agg["count"])

            ax.plot(
                agg["budget"],
                agg["mean"],
                label=ranker,
                color=colors.get(ranker, "black"),
                marker=markers.get(ranker, "o"),
            )
            ax.fill_between(
                agg["budget"],
                np.maximum(0, agg["mean"] - ci_half),
                agg["mean"] + ci_half,
                alpha=0.18,
                color=colors.get(ranker, "black"),
            )

        clean_title = title_map.get(g_name, g_name)
        ax.set_title(clean_title, fontweight="bold")
        ax.set_xlabel("Attacker Edge Budget B")
        if idx == 0:
            ax.set_ylabel("Target Rank Gain [with 95% CI]")
        ax.grid(True, linestyle="--", alpha=0.5)
        if idx == 0:
            ax.legend(frameon=True, facecolor="white", framealpha=0.9, loc="upper left")

    plt.suptitle("Target Rank Gain vs Attacker Budget Across Graph Topologies (Preliminary - Mid-Project)", y=1.02, fontweight="bold")
    out_png = FIGURES_DIR / "cost_curves_rank_gain.png"
    plt.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[SAVED] {out_png}")


def plot_h2_experiment():
    # Prefer h2_robustness.csv or h2_experiment.csv
    csv_h2 = RESULTS_DIR / "h2_experiment.csv"
    if not csv_h2.exists():
        print(f"[SKIP] {csv_h2} does not exist.")
        return

    df = pd.read_csv(csv_h2)
    sigma1_sq = df["sigma1_sq"].iloc[0]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

    # Left: Target Authority Score vs Hub Farm Size p
    ax1.plot(df["p_farm_size"], df["hits_score"], label="HITS Authority", color="#D9534F", marker="o", linewidth=2.5)
    ax1.plot(df["p_farm_size"], df["pagerank_score"] * 10.0, label="PageRank Score (x10)", color="#337AB7", marker="s", linestyle="--", linewidth=2.0)
    ax1.plot(df["p_farm_size"], df["salsa_score"], label="SALSA Authority", color="#5CB85C", marker="^", linestyle=":", linewidth=2.0)

    ax1.axvline(x=sigma1_sq, color="#292b2c", linestyle="--", linewidth=2.0, label=rf"Theoretical $\sigma_1^2 \approx {sigma1_sq:.1f}$")
    ax1.annotate(
        r"Takeover Jump ($p \approx \sigma_1^2$)",
        xy=(sigma1_sq, df["hits_score"].max() * 0.5),
        xytext=(sigma1_sq + 4, df["hits_score"].max() * 0.4),
        arrowprops=dict(facecolor="black", shrink=0.08, width=1.5, headwidth=7),
        fontweight="bold",
        fontsize=11
    )

    ax1.set_title("Target Authority Score vs Farm Size p (Preliminary)", fontweight="bold")
    ax1.set_xlabel(r"Hub Farm Size $p$ (Nodes & Edges Added)")
    ax1.set_ylabel("Target Authority Score")
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.legend(loc="upper left")

    # Right: Target Rank vs p
    ax2.plot(df["p_farm_size"], df["hits_rank"], label="HITS Rank", color="#D9534F", marker="o", linewidth=2.5)
    ax2.plot(df["p_farm_size"], df["pagerank_rank"], label="PageRank Rank", color="#337AB7", marker="s", linestyle="--", linewidth=2.0)
    ax2.plot(df["p_farm_size"], df["salsa_rank"], label="SALSA Rank", color="#5CB85C", marker="^", linestyle=":", linewidth=2.0)
    ax2.axvline(x=sigma1_sq, color="#292b2c", linestyle="--", linewidth=2.0, label=rf"Threshold $\sigma_1^2$")

    ax2.set_title("Target Rank vs Farm Size p (H2 Bifurcation)", fontweight="bold")
    ax2.set_xlabel(r"Hub Farm Size $p$")
    ax2.set_ylabel("Target Rank (1 = Top Authority)")
    ax2.invert_yaxis()
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.legend(loc="lower left")

    out_png = FIGURES_DIR / "h2_spectral_takeover.png"
    plt.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[SAVED] {out_png}")


def plot_defenses():
    csv_path = RESULTS_DIR / "defenses_eval_v2.csv"
    if not csv_path.exists():
        csv_path = RESULTS_DIR / "defenses_eval.csv"

    if not csv_path.exists():
        print(f"[SKIP] No defense evaluation CSV found.")
        return

    df = pd.read_csv(csv_path)

    # Aggregate by defense
    if "clean_ndcg_loss" in df.columns:
        agg = df.groupby("defense").agg({
            "attack_success_reduction": "mean",
            "clean_ndcg_loss": "mean",
            "clean_top20_ndcg": "mean",
        }).reset_index()
        x_col = "clean_ndcg_loss"
        x_label = "Clean Graph NDCG@20 Loss (Lower = Better)"
    else:
        agg = df.groupby("defense").agg({
            "attack_success_reduction": "mean",
            "false_demotion": "mean",
            "clean_top20_ndcg": "first"
        }).reset_index()
        x_col = "false_demotion"
        x_label = "Clean Graph False Demotion (1 - Clean Jaccard@20)"

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["#D9534F", "#0275D8", "#5BC0DE", "#5CB85C", "#F0AD4E", "#6F42C1", "#20C997", "#E83E8C"]

    # Target proposal goal region: reduction >= 50%, NDCG loss <= 5%
    ax.add_patch(patches.Rectangle((0, 50), 0.05, 60, color="#28A745", alpha=0.12, label="Proposal Target Zone (>=50% red, <=5% loss)"))

    for i, row in agg.iterrows():
        name = row["defense"].replace("_", " ")
        x_val = row[x_col]
        y_val = row["attack_success_reduction"] * 100.0

        ax.scatter(
            x_val,
            y_val,
            s=180,
            color=colors[i % len(colors)],
            label=name,
            edgecolors="black",
            linewidth=1.4,
            zorder=5
        )
        ax.annotate(
            name,
            (x_val + 0.008, y_val + 1.2),
            fontsize=10.5,
            fontweight="bold"
        )

    ax.set_title("Defenses Trade-off: Attack Reduction vs Clean Distortion (Preliminary)", fontweight="bold")
    ax.set_xlabel(x_label)
    ax.set_ylabel("Attack Success Reduction (%) [Higher = Better]")
    ax.set_ylim(-30, 115)
    ax.set_xlim(-0.01, max(0.65, agg[x_col].max() + 0.08))
    ax.grid(True, linestyle="--", alpha=0.5)

    out_png = FIGURES_DIR / "defenses_tradeoff.png"
    plt.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[SAVED] {out_png}")


def generate_architecture_diagram():
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis("off")

    c_built = "#D4EDDA"
    c_border_built = "#28A745"
    c_pending = "#FFF3CD"
    c_border_pending = "#FFC107"

    def draw_box(x, y, w, h, title, items, status="BUILT"):
        fill = c_built if status == "BUILT" else c_pending
        border = c_border_built if status == "BUILT" else c_border_pending
        box = patches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.2,rounding_size=0.3",
            facecolor=fill,
            edgecolor=border,
            linewidth=2.0
        )
        ax.add_patch(box)
        badge_color = "#155724" if status == "BUILT" else "#856404"
        ax.text(x + 0.2, y + h - 0.4, title, fontsize=12, fontweight="bold", color="#1F2D3D")
        ax.text(x + w - 0.2, y + h - 0.4, f"[{status}]", fontsize=10, fontweight="bold", color=badge_color, ha="right")

        for idx, item in enumerate(items):
            ax.text(x + 0.25, y + h - 0.8 - idx * 0.35, f"• {item}", fontsize=10, color="#333333")

    draw_box(0.5, 4.3, 3.8, 3.2, "1. Data Ingestion", [
        "SNAP wiki-Vote (7,115 n)",
        "SNAP web-Stanford (281k n)",
        "SNAP web-NotreDame (325k n)",
        "Synthetic BA, ER, SBM",
        "WEBSPAM labels (8,415 hosts)",
        "WEBSPAM Host Graph (Pending Java)",
    ], status="BUILT")

    draw_box(4.9, 4.3, 3.8, 3.2, "2. Attacks Engine", [
        "A1: Single Fake Hub",
        "A2: Hub Farm (p hubs)",
        "A3: Bipartite Block (Kp,q)",
        "A4: Proposal Target Inflation",
        "A4b: Multi-Hub Inflation",
        "A5: Proposal Cross-Score Farm",
        "A5b: Cross-Links Farm; A6: Greedy",
    ], status="BUILT")

    draw_box(9.3, 4.3, 4.2, 3.2, "3. Rankers & Solvers", [
        "Sparse Power-Iteration HITS",
        "PageRank (alpha=0.85)",
        "SALSA with Ergodic Jump",
        "In-Degree Centrality",
        "Sparse ARPACK SVD Eigengap",
    ], status="BUILT")

    draw_box(0.5, 0.5, 4.0, 3.4, "4. Defenses (D1-D5)", [
        "D1: Randomized HITS (eps=0.15)",
        "D1: Subspace HITS (k=5)",
        "D2: Bharat-Henzinger (1/k weighting)",
        "D3: Hub-Contribution Capping",
        "D4: Wu-Davison Mutual Overlap",
        "D4b: Wu-Davison Out-Link Jaccard",
        "D5: Trust-Based HITS Prior",
    ], status="BUILT")

    draw_box(5.1, 0.5, 3.8, 3.4, "5. Evaluation Suite", [
        "Rank Gain & Normalized Gain",
        "B*(10) and B*(20) Thresholds",
        "Top-k Jaccard & NDCG Fidelity",
        "Kendall Tau & Spearman Rho",
        "Bootstrap 95% CIs (1,000 resamples)",
        "Paired Wilcoxon & Holm-Bonferroni",
    ], status="BUILT")

    draw_box(9.5, 0.5, 4.0, 3.4, "6. Stretch Objectives", [
        "Game-Theoretic Attacker Loop",
        "Closed-Form Bound Proof B*(k)",
        "WEBSPAM-UK2007 Classifier",
        "(Scheduled for 8 Nov freeze)",
    ], status="PENDING")

    # Connectors
    arrow_props = dict(facecolor="#495057", edgecolor="#495057", width=1.5, headwidth=6, shrink=0.05)
    ax.annotate("", xy=(4.9, 5.9), xytext=(4.3, 5.9), arrowprops=arrow_props)
    ax.annotate("", xy=(9.3, 5.9), xytext=(8.7, 5.9), arrowprops=arrow_props)
    ax.annotate("", xy=(2.5, 4.3), xytext=(2.5, 3.9), arrowprops=arrow_props)
    ax.annotate("", xy=(7.0, 4.3), xytext=(7.0, 3.9), arrowprops=arrow_props)

    plt.suptitle("System Architecture: LinkRank Under Attack Pipeline", y=0.98, fontsize=16, fontweight="bold")
    out_png = FIGURES_DIR / "architecture.png"
    out_svg = FIGURES_DIR / "architecture.svg"
    plt.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.savefig(out_svg, format="svg", bbox_inches="tight")
    plt.close()
    print(f"[SAVED] {out_png} and {out_svg}")


def main():
    print("=== Generating All Figures ===")
    plot_cost_curves()
    plot_h2_experiment()
    plot_defenses()
    generate_architecture_diagram()
    print("[ALL FIGURES GENERATED]")


if __name__ == "__main__":
    main()
