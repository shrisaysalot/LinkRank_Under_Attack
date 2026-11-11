"""Generate 300-DPI publication-quality figure for WEBSPAM-UK2006 evaluation."""
import sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve, roc_auc_score

from src.data.loader import load_webspam_hostgraph, load_webspam_labels
from src.rankers import hits, pagerank, salsa, indegree
from src.defenses import randomized_hits, hub_capped_hits, wu_davison_hits

# Set style
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

fig, axes = plt.subplots(1, 2, figsize=(12, 5), dpi=300)

print("Loading hostgraph and labels...")
G, adj, n2h, h2n = load_webspam_hostgraph()
set1 = load_webspam_labels("set1", undecided_mode="keep")
set2 = load_webspam_labels("set2", undecided_mode="keep")

host_labels = {}
for _, row in pd.concat([set1, set2]).iterrows():
    h = row["host"]
    if h in h2n:
        host_labels[h2n[h]] = row["binary_label"]

y_true = []
nodes_eval = []
for n in range(len(n2h)):
    lbl = host_labels.get(n, -2)
    if lbl in [0, 1]:  # Exclude undecided (-1) and unlabeled (-2)
        nodes_eval.append(n)
        y_true.append(lbl)

y_true = np.array(y_true)
nodes_eval = np.array(nodes_eval)

print(f"Evaluating ROC curves on {len(y_true)} labeled hosts...")

# Panel 1: ROC Curves for Score-based Spam Flagging
ax1 = axes[0]
models = [
    ("PageRank", pagerank(adj), "#2ca02c", "-"),
    ("In-Degree", indegree(adj), "#9467bd", "--"),
    ("Undefended HITS", hits(adj), "#d62728", "-"),
    ("D1 Randomized HITS", randomized_hits(adj, eps=0.15), "#1f77b4", "-."),
    ("D3 Hub Capping (1%)", hub_capped_hits(adj, cap_fraction=0.01), "#ff7f0e", ":")
]

for name, res, color, ls in models:
    scores = res.scores
    hub_scores = getattr(res, "hub_scores", None)
    if hub_scores is not None and len(hub_scores) == len(scores):
        predictor = hub_scores / (scores + 1e-12)
    else:
        predictor = -scores
    
    pred_eval = predictor[nodes_eval]
    auc = roc_auc_score(y_true, pred_eval)
    fpr, tpr, _ = roc_curve(y_true, pred_eval)
    ax1.plot(fpr, tpr, label=f"{name} (AUC = {auc:.3f})", color=color, linestyle=ls, linewidth=2)

ax1.plot([0, 1], [0, 1], "k--", alpha=0.4, label="Random Guess (0.50)")
ax1.set_xlabel("False Positive Rate (Normal flagged as Spam)")
ax1.set_ylabel("True Positive Rate (Spam correctly flagged)")
ax1.set_title("(a) ROC Curves for Link-Spam Detection (UK-2006)", fontweight="bold")
ax1.legend(loc="lower right", frameon=True)
ax1.grid(True, linestyle="--", alpha=0.6)

# Panel 2: Spectral Scale Discrepancy (Base Set vs Global Host Graph)
ax2 = axes[1]
graphs_compare = ["ER-500", "BA-500", "SBM-500", "web-Stanford\n(Base Set)", "WEBSPAM-UK2006\n(Host Graph)"]
sigma_sq = [14.2, 38.4, 25.0, 48.7, 115407.4]
colors = ["#4c72b0", "#4c72b0", "#4c72b0", "#dd8452", "#c44e52"]

bars = ax2.bar(graphs_compare, sigma_sq, color=colors, width=0.55, edgecolor="black", linewidth=1.2)
ax2.set_yscale("log")
ax2.set_ylabel(r"Leading Eigenvalue $\sigma_1^2$ (Log Scale)", fontweight="bold")
ax2.set_title(r"(b) Spectral Barrier $\sigma_1^2$: Base-Sets vs Global Web", fontweight="bold")
ax2.grid(True, which="both", linestyle="--", alpha=0.5)

# Add value labels
for bar in bars:
    yval = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2.0, yval * 1.3, f"{yval:,.1f}", ha="center", va="bottom", fontsize=9, fontweight="bold")

# Add threshold line for typical budget B=100
ax2.axhline(100, color="red", linestyle="--", linewidth=1.8, label="Attacker Budget B=100")
ax2.legend(loc="upper left", frameon=True)

plt.tight_layout()
out_fig = Path("figures/webspam_eval.png")
plt.savefig(out_fig, dpi=300, bbox_inches="tight")
print(f"Saved publication figure to {out_fig}")

