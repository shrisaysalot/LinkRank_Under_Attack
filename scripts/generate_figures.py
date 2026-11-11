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
    csv_path = RESULTS_DIR / "cost_curves_v2.csv"
    if not csv_path.exists():
        csv_path = RESULTS_DIR / "cost_curves.csv"

    if not csv_path.exists():
        print(f"[SKIP] No cost curves CSV found.")
        return

    df = pd.read_csv(csv_path)

    # Plot multi-panel by attack family (A1, A2, A3, A4, A4b, A5, A5b, A6)
    attacks = sorted(df["attack"].unique())
    n_attacks = len(attacks)

    cols = 4
    rows = (n_attacks + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(16, 4 * rows), sharey=True)
    axes = axes.flatten()

    colors = {"HITS": "#D9534F", "PageRank": "#337AB7", "SALSA": "#5CB85C", "InDegree": "#F0AD4E"}
    markers = {"HITS": "o", "PageRank": "s", "SALSA": "^", "InDegree": "d"}

    for idx, att in enumerate(attacks):
        ax = axes[idx]
        sub_df = df[df["attack"] == att]

        for ranker in ["HITS", "PageRank", "SALSA", "InDegree"]:
            r_df = sub_df[sub_df["ranker"] == ranker]
            agg = r_df.groupby("budget")["normalized_rank_gain"].agg(["mean", "std", "count"]).reset_index()

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
                alpha=0.15,
                color=colors.get(ranker, "black"),
            )

        ax.set_title(f"{att} (Preliminary)", fontsize=11, fontweight="bold")
        ax.set_xlabel("Attacker Edge Budget B", fontsize=10)
        if idx % cols == 0:
            ax.set_ylabel("Normalized Rank Gain", fontsize=10)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.set_ylim(-0.05, 1.05)
        if idx == 0:
            ax.legend(frameon=True, facecolor="white", framealpha=0.9, fontsize=9, loc="upper left")

    # Hide unused subplots
    for j in range(idx + 1, len(axes)):
        axes[j].axis("off")

    plt.suptitle("Normalized Rank Gain vs Budget by Attack Family (Preliminary - Mid-Project)", y=1.01, fontweight="bold")
    out_png = FIGURES_DIR / "cost_curves_rank_gain.png"
    plt.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[SAVED] {out_png}")


def plot_h2_experiment():
    csv_h2 = RESULTS_DIR / "h2_experiment.csv"
    if not csv_h2.exists():
        print(f"[SKIP] {csv_h2} does not exist.")
        return

    df = pd.read_csv(csv_h2)
    sigma1_sq = df["sigma1_sq"].iloc[0]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

    # Left: Target Authority Score vs Hub Farm Size p
    ax1.plot(df["p_farm_size"], df["hits_score"], label="HITS Authority", color="#D9534F", marker="o", linewidth=2.6)
    ax1.plot(df["p_farm_size"], df["pagerank_score"] * 10.0, label="PageRank Score (x10)", color="#337AB7", marker="s", linestyle="--", linewidth=2.2)
    ax1.plot(df["p_farm_size"], df["salsa_score"], label="SALSA Authority", color="#5CB85C", marker="^", linestyle=":", linewidth=2.2)

    ax1.axvline(x=sigma1_sq, color="#292b2c", linestyle="--", linewidth=2.0, label=rf"Theoretical $\sigma_1^2 \approx {sigma1_sq:.1f}$")
    ax1.annotate(
        r"Takeover Jump ($p \approx 0.82 \sigma_1^2$)",
        xy=(sigma1_sq * 0.82, df["hits_score"].max() * 0.45),
        xytext=(sigma1_sq * 0.82 - 25, df["hits_score"].max() * 0.60),
        arrowprops=dict(facecolor="black", shrink=0.08, width=1.8, headwidth=7),
        fontweight="bold",
        fontsize=12
    )

    ax1.set_title("Target Authority Score vs Farm Size p (Preliminary)", fontweight="bold", fontsize=13.5)
    ax1.set_xlabel(r"Hub Farm Size $p$ (Nodes & Edges Added)", fontsize=12.5)
    ax1.set_ylabel("Target Authority Score", fontsize=12.5)
    ax1.tick_params(labelsize=11.5)
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.legend(loc="upper left", fontsize=11)

    # Right: Target Rank vs p
    ax2.plot(df["p_farm_size"], df["hits_rank"], label="HITS Rank", color="#D9534F", marker="o", linewidth=2.6)
    ax2.plot(df["p_farm_size"], df["pagerank_rank"], label="PageRank Rank", color="#337AB7", marker="s", linestyle="--", linewidth=2.2)
    ax2.plot(df["p_farm_size"], df["salsa_rank"], label="SALSA Rank", color="#5CB85C", marker="^", linestyle=":", linewidth=2.2)
    ax2.axvline(x=sigma1_sq, color="#292b2c", linestyle="--", linewidth=2.0, label=rf"Threshold $\sigma_1^2$")

    ax2.set_title("Target Rank vs Farm Size p (Preliminary - H2 Bifurcation)", fontweight="bold", fontsize=13.5)
    ax2.set_xlabel(r"Hub Farm Size $p$", fontsize=12.5)
    ax2.set_ylabel("Target Rank (1 = Top Authority)", fontsize=12.5)
    ax2.tick_params(labelsize=11.5)
    ax2.invert_yaxis()
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.legend(loc="lower left", fontsize=11)

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

    # Exclude cells where undefended attack gain <= 0
    undef = df[df["defense"] == "Undefended_HITS"]
    base_gains = undef.set_index(["graph", "target_node", "attack", "budget"])["rank_gain"].to_dict()
    df["base_gain"] = df.apply(lambda r: base_gains.get((r["graph"], r["target_node"], r["attack"], r["budget"]), 0), axis=1)

    df_pos = df[df["base_gain"] > 0].copy()
    df_pos["true_reduction"] = 1.0 - (df_pos["rank_gain"] / df_pos["base_gain"])

    # Compute mean metrics across valid cells
    agg_red = df_pos.groupby("defense")["true_reduction"].mean().reset_index()
    agg_loss = df.groupby("defense")["clean_ndcg_loss"].mean().reset_index()
    agg = pd.merge(agg_red, agg_loss, on="defense")

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["#D9534F", "#0275D8", "#5BC0DE", "#5CB85C", "#F0AD4E", "#6F42C1", "#20C997", "#E83E8C"]

    # Target proposal goal region: reduction >= 50%, NDCG loss <= 5%
    ax.add_patch(patches.Rectangle((0, 50), 0.05, 60, color="#28A745", alpha=0.12, label="Proposal Goal Zone (>=50% red, <=5% loss)"))

    for i, row in agg.iterrows():
        d_raw = row["defense"]
        name = d_raw.replace("_", " ")
        if "HubCapping" in d_raw:
            name += " (No-Op)"
        x_val = row["clean_ndcg_loss"]
        y_val = row["true_reduction"] * 100.0

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
            fontsize=9.5,
            fontweight="bold"
        )

    ax.set_title("Defenses Trade-off: Attack Reduction vs Clean Distortion (Preliminary - Small-N)", fontweight="bold")
    ax.set_xlabel("Clean Graph NDCG@20 Loss (Lower = Better)")
    ax.set_ylabel("Mean Attack Success Reduction (%) [Higher = Better]")
    ax.set_ylim(-85, 115)
    ax.set_xlim(-0.01, max(0.65, agg["clean_ndcg_loss"].max() + 0.08))
    ax.grid(True, linestyle="--", alpha=0.5)

    out_png = FIGURES_DIR / "defenses_tradeoff.png"
    plt.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[SAVED] {out_png}")


def generate_architecture_diagram():
    fig, ax = plt.subplots(figsize=(15, 8.5))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis("off")

    c_built = "#D4EDDA"
    c_border_built = "#28A745"
    c_pending = "#FFF3CD"
    c_border_pending = "#FFC107"
    c_scoped = "#EDF2F7"
    c_border_scoped = "#718096"

    def draw_box(x, y, w, h, title, items, status="BUILT"):
        if status == "BUILT":
            fill, border, badge_color = c_built, c_border_built, "#155724"
        elif status == "SCOPED OUT":
            fill, border, badge_color = c_scoped, c_border_scoped, "#4A5568"
        else:
            fill, border, badge_color = c_pending, c_border_pending, "#856404"

        box = patches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.2,rounding_size=0.3",
            facecolor=fill,
            edgecolor=border,
            linewidth=2.2
        )
        ax.add_patch(box)
        ax.text(x + 0.2, y + h - 0.42, title, fontsize=13.5, fontweight="bold", color="#1F2D3D")
        ax.text(x + w - 0.2, y + h - 0.42, f"[{status}]", fontsize=11, fontweight="bold", color=badge_color, ha="right")

        for idx, item in enumerate(items):
            ax.text(x + 0.25, y + h - 0.88 - idx * 0.38, f"• {item}", fontsize=11.2, color="#222222")

    draw_box(0.5, 4.3, 3.8, 3.2, "1. Data Ingestion", [
        "SNAP wiki-Vote (7,115 n)",
        "SNAP web-Stanford (281k n)",
        "SNAP web-NotreDame (325k n)",
        "Synthetic BA, ER, SBM (500 n)",
        "WEBSPAM-UK2006 (10,662 labels)",
        "WEBSPAM Host Graph (11,402 n)",
    ], status="BUILT")

    draw_box(4.9, 4.3, 3.8, 3.2, "2. Attacks Engine", [
        "A1: Single Fake Hub",
        "A2: Hub Farm (p hubs)",
        "A3: Bipartite Block (Kp,q)",
        "A4: Proposal Target Inflation",
        "A5: Proposal Cross-Score Farm",
        "A5b: Cross-Links; A6: Greedy",
        "Camouflaged Farm (r=2, 5, 10)",
    ], status="BUILT")

    draw_box(9.3, 4.3, 4.2, 3.2, "3. Rankers & Solvers", [
        "Sparse Power-Iteration HITS",
        "PageRank (alpha=0.85)",
        "SALSA with Ergodic Jump",
        "In-Degree Centrality",
        "Sparse ARPACK SVD Eigengap",
        "Matrix Vectorized Computations",
    ], status="BUILT")

    draw_box(0.5, 0.5, 4.0, 3.4, "4. Defenses (D1-D5)", [
        "D1: Randomized HITS (eps=0.15)",
        "D1: Subspace HITS (k=5)",
        "D2: Bharat-Henzinger (1/k weighting)",
        "D3: Hub Capping (1% calibrated)",
        "D4: Wu-Davison Mutual Overlap",
        "D5: Trust HITS (PR seeds, k=20)",
        "Combined: D4+D1 and D4+D5",
    ], status="BUILT")

    draw_box(5.1, 0.5, 3.8, 3.4, "5. Evaluation Suite", [
        "Rank Gain & Normalized Gain",
        "B*(10) and B*(20) Thresholds",
        "Top-k Jaccard & NDCG Fidelity",
        "Bootstrap 95% CIs (1,000 boot)",
        "Independent Wilcoxon & Holm FWER",
        "WEBSPAM Real Attack & Spam Ranks",
    ], status="BUILT")

    draw_box(9.5, 0.5, 4.0, 3.4, "6. Stretch Objectives", [
        "• (a) Closed-Form Spectral Bound",
        "• (b) Game-Theoretic Loop",
        "• (c) WEBSPAM-UK2007 Classifier",
        "Status: Not Pursued (Scoped Out)",
        "Focus on Empirical Core & WEBSPAM",
    ], status="SCOPED OUT")

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
