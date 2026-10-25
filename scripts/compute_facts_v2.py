import sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pandas as pd
import numpy as np
from src.eval.stats import bootstrap_ci, wilcoxon_test, holm_bonferroni

print("=== 1. COST CURVES V2 SUMMARY ===")
df1 = pd.read_csv("results/cost_curves_v2.csv")
print(f"Total rows: {len(df1)}")
print("Graphs:", df1["graph"].unique())

for B in [25, 100]:
    print(f"\n--- Budget B = {B} ---")
    sub = df1[df1["budget"] == B]
    for r in ["HITS", "PageRank", "SALSA", "InDegree"]:
        rdf = sub[sub["ranker"] == r]
        g_raw_m, g_raw_l, g_raw_u = bootstrap_ci(rdf["rank_gain"].values)
        g_norm_m, g_norm_l, g_norm_u = bootstrap_ci(rdf["normalized_rank_gain"].values)
        t10_m, t10_l, t10_u = bootstrap_ci(rdf["top10_entry"].values)
        jacc_m, jacc_l, jacc_u = bootstrap_ci(rdf["jaccard_at_20"].values)
        ndcg_m, ndcg_l, ndcg_u = bootstrap_ci(rdf["ndcg_at_20"].values)
        tau_m, tau_l, tau_u = bootstrap_ci(rdf["kendall_tau"].values)
        print(f"[{r:8s}] Raw Gain: {g_raw_m:5.1f} [{g_raw_l:5.1f}, {g_raw_u:5.1f}] | Norm Gain: {g_norm_m:.3f} [{g_norm_l:.3f}, {g_norm_u:.3f}] | Top-10: {t10_m*100:4.1f}% [{t10_l*100:4.1f}%, {t10_u*100:4.1f}%] | Jacc@20: {jacc_m:.3f} | NDCG@20: {ndcg_m:.3f} | Tau: {tau_m:.3f}")

print("\n--- Paired Wilcoxon Tests (HITS vs Baselines at B=100) ---")
sub100 = df1[df1["budget"] == 100]
p_vals = []
baselines = ["PageRank", "SALSA", "InDegree"]
for b in baselines:
    h_vals = sub100[sub100["ranker"] == "HITS"]["normalized_rank_gain"].values
    b_vals = sub100[sub100["ranker"] == b]["normalized_rank_gain"].values
    stat, p = wilcoxon_test(h_vals, b_vals)
    p_vals.append(p)
rej, adj_p = holm_bonferroni(p_vals)
for b, p, ap, r in zip(baselines, p_vals, adj_p, rej):
    print(f"HITS vs {b:8s}: raw p={p:.2e}, Holm adj p={ap:.2e}, rejected={r}")

print("\n=== 2. H2 ROBUSTNESS SUMMARY ===")
df2 = pd.read_csv("results/h2_robustness.csv")
print(f"Total runs: {len(df2)}")
ge_rate = df2["sigma1_sq_ge_max_indeg"].mean() * 100
abrupt_rate = df2["is_hits_jump_abrupt"].mean() * 100
hits_jump = df2["max_hits_step_jump"].mean()
pr_jump = df2["max_pagerank_step_jump"].mean()
print(f"Sigma1^2 >= max in-degree hold rate: {ge_rate:.1f}%")
print(f"HITS jump abruptness rate: {abrupt_rate:.1f}%")
print(f"Mean max single-step rank jump: HITS={hits_jump:.1f}, PageRank={pr_jump:.1f}")

p_ratio_10 = df2["ratio_p_star_10_to_sigma1_sq"].dropna().values
m10, l10, u10 = bootstrap_ci(p_ratio_10)
print(f"p*(10) / sigma1^2: {m10:.3f} [{l10:.3f}, {u10:.3f}] (n={len(p_ratio_10)})")

p_ratio_1 = df2["ratio_p_star_1_to_sigma1_sq"].dropna().values
m1, l1, u1 = bootstrap_ci(p_ratio_1)
print(f"p*(1) / sigma1^2:  {m1:.3f} [{l1:.3f}, {u1:.3f}] (n={len(p_ratio_1)})")

print("\n=== 3. H1 & H3 SUMMARY ===")
df3 = pd.read_csv("results/h1_h3_eval.csv")
h1_df = df3[df3["hypothesis"] == "H1"]
print(f"H1 B*(10) Ratio (HITS / InDegree): mean={h1_df['b_star_ratio'].mean():.2f}")
h3_df = df3[df3["hypothesis"] == "H3"]
for g in h3_df["graph"].unique():
    gdf = h3_df[h3_df["graph"] == g]
    m_s, l_s, u_s = bootstrap_ci(gdf["cost_saving_pct"].dropna().values)
    print(f"  {g}: mean cost saving={m_s:.1f}% [{l_s:.1f}%, {u_s:.1f}%] (n={len(gdf)})")

print("\n=== 4. DEFENSE MATRIX SUMMARY ===")
df4 = pd.read_csv("results/defenses_eval_v2.csv")
print(f"Total rows: {len(df4)}")
for d in df4["defense"].unique():
    ddf = df4[df4["defense"] == d]
    red_m, red_l, red_u = bootstrap_ci(ddf["attack_success_reduction"].values)
    jacc_clean = ddf["clean_top20_jaccard"].mean()
    ndcg_loss = ddf["clean_ndcg_loss"].mean()
    goal_rate = ddf["meets_proposal_goal"].mean() * 100
    print(f"[{d:25s}] Red: {red_m*100:5.1f}% [{red_l*100:5.1f}%, {red_u*100:5.1f}%] | Clean Jacc: {jacc_clean:.3f} | NDCG Loss: {ndcg_loss*100:4.1f}% | Meets Goal: {goal_rate:4.1f}%")
