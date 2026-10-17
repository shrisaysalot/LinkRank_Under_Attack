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
    "font.size": 12,
    "axes.labelsize": 14,
    "axes.titlesize": 15,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    "legend.fontsize": 12,
    "figure.titlesize": 16,
    "lines.linewidth": 2.5,
    "lines.markersize": 8,
    "figure.autolayout": True,
})


def plot_cost_curves():
    csv_path = RESULTS_DIR / "cost_curves.csv"
    if not csv_path.exists():
        print(f"[SKIP] {csv_path} does not exist.")
        return

    df = pd.read_csv(csv_path)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)

    graphs = df["graph"].unique()
    colors = {"HITS": "#D9534F", "PageRank": "#337AB7", "SALSA": "#5CB85C", "InDegree": "#F0AD4E"}
    markers = {"HITS": "o", "PageRank": "s", "SALSA": "^", "InDegree": "d"}

    for idx, g_name in enumerate(graphs[:2]):
        ax = axes[idx]
        sub_df = df[df["graph"] == g_name]

        for ranker in ["HITS", "PageRank", "SALSA", "InDegree"]:
            r_df = sub_df[sub_df["ranker"] == ranker]
            agg = r_df.groupby("budget")["rank_gain"].agg(["mean", "std"]).reset_index()

            ax.plot(
                agg["budget"],
                agg["mean"],
                label=ranker,
                color=colors.get(ranker, "black"),
                marker=markers.get(ranker, "o"),
            )
            ax.fill_between(
                agg["budget"],
                agg["mean"] - agg["std"].fillna(0),
                agg["mean"] + agg["std"].fillna(0),
                alpha=0.15,
                color=colors.get(ranker, "black"),
            )

        clean_title = "Synthetic Scale-Free (BA-500)" if "Synthetic" in g_name else "SNAP wiki-Vote (Base Set)"
        ax.set_title(clean_title, fontweight="bold")
        ax.set_xlabel("Attacker Edge Budget")
        if idx == 0:
            ax.set_ylabel("Target Rank Gain (Higher = Greater Vulnerability)")
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.legend(frameon=True, facecolor="white", framealpha=0.9)

    out_png = FIGURES_DIR / "cost_curves_rank_gain.png"
    plt.savefig(out_png, dpi=300)
    plt.close()
    print(f"[SAVED] {out_png}")


def plot_h2_experiment():
    csv_path = RESULTS_DIR / "h2_experiment.csv"
    if not csv_path.exists():
        print(f"[SKIP] {csv_path} does not exist.")
        return

    df = pd.read_csv(csv_path)
    sigma1_sq = df["sigma1_sq"].iloc[0]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Left: Target Authority Score vs Hub Farm Size p
    ax1.plot(df["p_farm_size"], df["hits_score"], label="HITS Authority", color="#D9534F", marker="o")
    ax1.plot(df["p_farm_size"], df["pagerank_score"], label="PageRank Score (x10)", color="#337AB7", marker="s", linestyle="--")
    ax1.plot(df["p_farm_size"], df["salsa_score"], label="SALSA Authority", color="#5CB85C", marker="^", linestyle=":")

    ax1.axvline(x=sigma1_sq, color="#292b2c", linestyle="--", linewidth=2.0, label=rf"Theoretical Threshold $\sigma_1^2 \approx {sigma1_sq:.1f}$")
    ax1.annotate(
        r"Takeover Jump ($p \approx \sigma_1^2$)",
        xy=(sigma1_sq, df["hits_score"].max() * 0.5),
        xytext=(sigma1_sq + 5, df["hits_score"].max() * 0.4),
        arrowprops=dict(facecolor="black", shrink=0.08, width=1.5, headwidth=8),
        fontweight="bold",
        fontsize=12
    )

    ax1.set_title("H2: Spectral Bifurcation / Takeover in HITS", fontweight="bold")
    ax1.set_xlabel("Hub Farm Size $p$ (Fake Nodes & Edges)")
    ax1.set_ylabel("Target Ranking Score")
    ax1.grid(True, linestyle="--", alpha=0.6)
    ax1.legend(loc="upper left")

    # Right: Target Rank vs p
    ax2.plot(df["p_farm_size"], df["hits_rank"], label="HITS Rank", color="#D9534F", marker="o")
    ax2.plot(df["p_farm_size"], df["pagerank_rank"], label="PageRank Rank", color="#337AB7", marker="s", linestyle="--")
    ax2.plot(df["p_farm_size"], df["salsa_rank"], label="SALSA Rank", color="#5CB85C", marker="^", linestyle=":")
    ax2.axvline(x=sigma1_sq, color="#292b2c", linestyle="--", linewidth=2.0)

    ax2.set_title("Target Rank vs Farm Size $p$", fontweight="bold")
    ax2.set_xlabel("Hub Farm Size $p$")
    ax2.set_ylabel("Target Rank (1 = Top Authority)")
    ax2.invert_yaxis()
    ax2.grid(True, linestyle="--", alpha=0.6)
    ax2.legend(loc="lower left")

    out_png = FIGURES_DIR / "h2_spectral_takeover.png"
    plt.savefig(out_png, dpi=300)
    plt.close()
    print(f"[SAVED] {out_png}")


def plot_defenses():
    csv_path = RESULTS_DIR / "defenses_eval.csv"
    if not csv_path.exists():
        print(f"[SKIP] {csv_path} does not exist.")
        return

    df = pd.read_csv(csv_path)

    # Aggregate by defense
    agg = df.groupby("defense").agg({
        "attack_success_reduction": "mean",
        "false_demotion": "first",
        "clean_top20_ndcg": "first"
    }).reset_index()

    fig, ax = plt.subplots(figsize=(10, 6))

    colors = ["#D9534F", "#0275D8", "#5BC0DE", "#5CB85C", "#F0AD4E", "#6F42C1", "#20C997"]

    for i, row in agg.iterrows():
        name = row["defense"].replace("_", " ")
        ax.scatter(
            row["false_demotion"],
            row["attack_success_reduction"] * 100,
            s=180,
            color=colors[i % len(colors)],
            label=name,
            edgecolors="black",
            linewidth=1.5,
            zorder=5
        )
        ax.annotate(
            name,
            (row["false_demotion"] + 0.01, row["attack_success_reduction"] * 100 + 1.2),
            fontsize=11,
            fontweight="bold"
        )

    ax.set_title("Defenses Trade-off: Attack Reduction vs False Demotion", fontweight="bold")
    ax.set_xlabel("Clean Graph False Demotion (1 - Clean Jaccard@20) [Lower = Better]")
    ax.set_ylabel("Attack Success Reduction (%) [Higher = Stronger Defense]")
    ax.set_ylim(-10, 115)
    ax.set_xlim(-0.02, max(0.5, agg["false_demotion"].max() + 0.1))
    ax.grid(True, linestyle="--", alpha=0.6)

    out_png = FIGURES_DIR / "defenses_tradeoff.png"
    plt.savefig(out_png, dpi=300)
    plt.close()
    print(f"[SAVED] {out_png}")


def generate_architecture_diagram():
    """Generates figures/architecture.png and figures/architecture.svg showing the system pipeline."""
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis("off")

    # Colors
    c_built = "#D4EDDA"     # soft green
    c_border_built = "#28A745"
    c_pending = "#FFF3CD"   # soft amber
    c_border_pending = "#FFC107"
    c_header = "#1F2D3D"

    def draw_box(x, y, w, h, title, items, status="BUILT"):
        fill = c_built if status == "BUILT" else c_pending
        border = c_border_built if status == "BUILT" else c_border_pending
        rect = patches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.2,rounding_size=0.3",
            facecolor=fill,
            edgecolor=border,
            linewidth=2,
            zorder=2
        )
        ax.add_patch(rect)
        tag = "[BUILT]" if status == "BUILT" else "[PENDING]"
        tag_color = "#155724" if status == "BUILT" else "#856404"
        ax.text(x + w / 2, y + h - 0.4, title, ha="center", va="center", fontsize=12, fontweight="bold", color=c_header)
        ax.text(x + w - 0.4, y + h - 0.35, tag, ha="right", va="center", fontsize=9, fontweight="bold", color=tag_color)

        for i, item in enumerate(items):
            ax.text(x + 0.25, y + h - 0.8 - (i * 0.32), f"• {item}", ha="left", va="center", fontsize=10, color="#333333")

    # Layer 1: Data
    draw_box(0.5, 4.5, 3.8, 2.8, "1. Data & Generators", [
        "SNAP wiki-Vote (Real)",
        "SNAP web-Stanford (Real)",
        "SNAP web-NotreDame (Real)",
        "WEBSPAM-UK2006 (Labels)",
        "Synthetic: BA, ER, SBM",
    ], status="BUILT")

    # Layer 2: Base Sets & Query
    draw_box(4.9, 4.5, 4.0, 2.8, "2. Base-Set Construction", [
        "Query Root Sampling (|R|=200)",
        "Kleinberg Expansion (out-links)",
        "In-link Capping (max 50/node)",
        "Sub-graph Induction & Mapping",
        "Direct Whole Graph Mode",
    ], status="BUILT")

    # Layer 3: Attacks
    draw_box(9.5, 4.5, 4.0, 2.8, "3. Adversarial Attacks", [
        "A1: Single Fake Hub",
        "A2: Hub Farm (p fake hubs)",
        "A3: Bipartite Block (K_p,q)",
        "A4: Hub Inflation (c top auth)",
        "A5: Cross-Score Coupling",
        "A6: Greedy Gradient (dsigma/dA)",
    ], status="BUILT")

    # Layer 4: Rankers & Defenses
    draw_box(0.5, 0.8, 5.8, 3.0, "4. Rankers & Defenses", [
        "HITS (Sparse Power Iteration, tol 1e-8)",
        "PageRank (alpha=0.85, dangling handling)",
        "SALSA (Bipartite Random Walk)",
        "In-Degree Baseline",
        "D1: Randomized HITS (eps=0.15) & Subspace HITS",
        "D2: Bharat-Henzinger / D3: Hub-Capping (10%)",
        "D4: Wu-Davison / D5: Trust-Based HITS",
    ], status="BUILT")

    # Layer 5: Evaluation
    draw_box(6.8, 0.8, 4.2, 3.0, "5. Evaluation & Statistics", [
        "Rank Gain & Score Amplification",
        "Top-10 / Top-20 Entry Rate",
        "Kendall Tau, Spearman Rho",
        "NDCG@k & Jaccard@k Fidelity",
        "False Demotion vs Attack Cut",
        "Bootstrap 95% CIs & Wilcoxon",
    ], status="BUILT")

    # Layer 6: Pending
    draw_box(11.4, 0.8, 2.2, 3.0, "Pending Extensions", [
        "WEBSPAM webgraph",
        "extract via Java",
        "Game-theoretic",
        "attacker loop",
        "Formal bound proof",
    ], status="PENDING")

    # Connective Arrows
    def draw_arrow(x1, y1, x2, y2):
        ax.annotate(
            "", xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(arrowstyle="-|>", color="#495057", lw=2, mutation_scale=15)
        )

    draw_arrow(4.3, 5.9, 4.9, 5.9)
    draw_arrow(8.9, 5.9, 9.5, 5.9)
    draw_arrow(11.5, 4.5, 11.5, 4.0)
    draw_arrow(11.5, 4.0, 3.4, 4.0)
    draw_arrow(3.4, 4.0, 3.4, 3.8)
    draw_arrow(6.3, 2.3, 6.8, 2.3)

    plt.suptitle("System Architecture: LinkRank Under Attack (IR Project Group 16)", fontsize=16, fontweight="bold", y=0.98)

    # Save SVG and PNG
    out_svg = FIGURES_DIR / "architecture.svg"
    out_png = FIGURES_DIR / "architecture.png"
    plt.savefig(out_svg)
    plt.savefig(out_png, dpi=300)
    plt.close()
    print(f"[SAVED] {out_svg} and {out_png}")


def main():
    print("=== Generating Figures for LinkRank Under Attack Evidence Pack ===")
    plot_cost_curves()
    plot_h2_experiment()
    plot_defenses()
    generate_architecture_diagram()
    print("[ALL FIGURES GENERATED SUCCESSFULLY]")


if __name__ == "__main__":
    main()
