"""Aggregate statistical metrics from results/cost_curves.csv for PROGRESS_REPORT_FACTS.md."""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd
from src.eval.stats import bootstrap_ci

df = pd.read_csv("results/cost_curves.csv")
print(f"Total experimental runs: {len(df)}")
print(f"Graphs evaluated: {df['graph'].unique()}")
print(f"Budgets evaluated: {df['budget'].unique()}")

# Aggregate across all attacks and targets at budget = 25 and budget = 100
for B in [25, 100]:
    print(f"\n=== SUMMARY AT BUDGET B = {B} ===")
    sub = df[df["budget"] == B]
    for ranker in ["HITS", "PageRank", "SALSA", "InDegree"]:
        r_df = sub[sub["ranker"] == ranker]
        
        gain_m, gain_l, gain_u = bootstrap_ci(r_df["rank_gain"].values)
        t10_m, t10_l, t10_u = bootstrap_ci(r_df["top10_entry"].values)
        t20_m, t20_l, t20_u = bootstrap_ci(r_df["top20_entry"].values)
        jacc_m, jacc_l, jacc_u = bootstrap_ci(r_df["jaccard_at_20"].values)
        ndcg_m, ndcg_l, ndcg_u = bootstrap_ci(r_df["ndcg_at_20"].values)
        tau_m, tau_l, tau_u = bootstrap_ci(r_df["kendall_tau"].values)
        
        print(f"[{ranker:8s}] Rank Gain: {gain_m:.1f} [{gain_l:.1f}, {gain_u:.1f}] | Top-10 Rate: {t10_m*100:.1f}% [{t10_l*100:.1f}%, {t10_u*100:.1f}%] | Top-20: {t20_m*100:.1f}% | Jaccard@20: {jacc_m:.3f} [{jacc_l:.3f}, {jacc_u:.3f}] | NDCG@20: {ndcg_m:.3f} | Tau: {tau_m:.3f}")
