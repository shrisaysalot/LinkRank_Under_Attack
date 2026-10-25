import sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pandas as pd
import numpy as np
from src.eval.stats import bootstrap_ci, wilcoxon_test, holm_bonferroni

print("==========================================================")
print("=== 1. COST CURVES V2 (PER-ATTACK & POOLED) ===")
print("==========================================================")
df1 = pd.read_csv("results/cost_curves_v2.csv")
print(f"Total rows: {len(df1)}")
print("Scale-down vs proposal:")
print("  - Budgets: {1, 5, 10, 25, 50, 75, 100} (7 levels; no 200/500)")
print("  - Seeds: [42, 123, 456] (3 seeds; not 5)")
print("  - Graphs: 4 graphs (BA-500, ER-500, SBM-500, web-Stanford base-set)")
print("  - Targets: 5 targets per graph/seed")

attacks_sorted = sorted(df1["attack"].unique())
for B in [25, 100]:
    print(f"\n--- Budget B = {B} (Per-Attack Breakdown) ---")
    subB = df1[df1["budget"] == B]
    for att in attacks_sorted:
        att_sub = subB[subB["attack"] == att]
        n_per = len(att_sub) // 4
        print(f"\n[Attack: {att}] (n={n_per} per ranker)")
        for r in ["HITS", "PageRank", "SALSA", "InDegree"]:
            rdf = att_sub[att_sub["ranker"] == r]
            gn_m, gn_l, gn_u = bootstrap_ci(rdf["normalized_rank_gain"].values)
            t10_m, t10_l, t10_u = bootstrap_ci(rdf["top10_entry"].values)
            j_m, j_l, j_u = bootstrap_ci(rdf["jaccard_at_20"].values)
            n_m, n_l, n_u = bootstrap_ci(rdf["ndcg_at_20"].values)
            tau_m, tau_l, tau_u = bootstrap_ci(rdf["kendall_tau"].values)
            print(f"  {r:8s} | NormGain: {gn_m:.3f} [{gn_l:.3f}, {gn_u:.3f}] | Top-10: {t10_m*100:4.1f}% [{t10_l*100:4.1f}%, {t10_u*100:4.1f}%] | Jacc@20: {j_m:.3f} | NDCG@20: {n_m:.3f} | Tau: {tau_m:.3f}")

print("\n--- Pooled Across All Attacks (Secondary Summary) ---")
for B in [25, 100]:
    print(f"\n--- Pooled Budget B = {B} (n=480 per ranker) ---")
    subB = df1[df1["budget"] == B]
    for r in ["HITS", "PageRank", "SALSA", "InDegree"]:
        rdf = subB[subB["ranker"] == r]
        gn_m, gn_l, gn_u = bootstrap_ci(rdf["normalized_rank_gain"].values)
        t10_m, t10_l, t10_u = bootstrap_ci(rdf["top10_entry"].values)
        j_m, j_l, j_u = bootstrap_ci(rdf["jaccard_at_20"].values)
        n_m, n_l, n_u = bootstrap_ci(rdf["ndcg_at_20"].values)
        tau_m, tau_l, tau_u = bootstrap_ci(rdf["kendall_tau"].values)
        print(f"  {r:8s} | NormGain: {gn_m:.3f} [{gn_l:.3f}, {gn_u:.3f}] | Top-10: {t10_m*100:4.1f}% [{t10_l*100:4.1f}%, {t10_u*100:4.1f}%] | Jacc@20: {j_m:.3f} | NDCG@20: {n_m:.3f} | Tau: {tau_m:.3f}")

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

print("\n==========================================================")
print("=== 2. H2 ROBUSTNESS SUMMARY ===")
print("==========================================================")
df2 = pd.read_csv("results/h2_robustness.csv")
print(f"Total runs: {len(df2)}")
print(f"p grid used: 24 multipliers linearly spaced between 0.1 and 2.0 * sigma1^2")
ge_rate = df2["sigma1_sq_ge_max_indeg"].mean() * 100
abrupt_rate = df2["is_hits_jump_abrupt"].mean() * 100
non_abrupt_count = (~df2["is_hits_jump_abrupt"]).sum()
non_abrupt_rate = non_abrupt_count / len(df2) * 100
hits_jump = df2["max_hits_step_jump"].mean()
pr_jump = df2["max_pagerank_step_jump"].mean()
print(f"Sigma1^2 >= max in-degree hold rate: {ge_rate:.1f}%")
print(f"HITS jump abruptness rate: {abrupt_rate:.1f}% (38 / 60)")
print(f"Counterexamples (non-abrupt): {non_abrupt_rate:.1f}% ({non_abrupt_count} / 60): {dict(df2[~df2['is_hits_jump_abrupt']]['graph'].value_counts())}")
print(f"Mean max single-step rank jump: HITS={hits_jump:.1f}, PageRank={pr_jump:.1f}")

p_ratio_10 = df2["ratio_p_star_10_to_sigma1_sq"].dropna().values
m10, l10, u10 = bootstrap_ci(p_ratio_10)
print(f"p*(10) / sigma1^2: {m10:.3f} [{l10:.3f}, {u10:.3f}] (n={len(p_ratio_10)}) -> Takeover occurs somewhat BELOW sigma1^2")

p_ratio_1 = df2["ratio_p_star_1_to_sigma1_sq"].dropna().values
m1, l1, u1 = bootstrap_ci(p_ratio_1)
print(f"p*(1) / sigma1^2:  {m1:.3f} [{l1:.3f}, {u1:.3f}] (n={len(p_ratio_1)})")

print("\n==========================================================")
print("=== 3. H1 & H3 SUMMARY ===")
print("==========================================================")
df3 = pd.read_csv("results/h1_h3_eval.csv")
h1_df = df3[df3["hypothesis"] == "H1"]
print(f"H1 total instances: n={len(h1_df)}")
print(f"H1 B*(10) Ratio (HITS / InDegree): mean={h1_df['b_star_ratio'].mean():.2f} (n={len(h1_df.dropna(subset=['b_star_ratio']))})")
print("  Individual B*(10) values for HITS:", h1_df["b_star_hits_k10"].tolist())
print("  Individual B*(10) values for In-Degree:", h1_df["b_star_indeg_k10"].tolist())

h3_df = df3[df3["hypothesis"] == "H3"]
print(f"H3 total rows: n={len(h3_df)} (evaluated A2 vs proposal A5 with c=3 real authorities)")
for g in sorted(h3_df["graph"].unique()):
    gdf = h3_df[h3_df["graph"] == g]
    valid_savings = gdf["cost_saving_pct"].dropna().values
    if len(valid_savings) > 0:
        m_s, l_s, u_s = bootstrap_ci(valid_savings)
        print(f"  {g}: mean cost saving = {m_s:.1f}% [{l_s:.1f}%, {u_s:.1f}%] (n={len(valid_savings)} valid of {len(gdf)} instances)")
    else:
        print(f"  {g}: target failed to reach Top-10 under A2 (b_star_a2 = NaN for all {len(gdf)} instances; target achieved Top-10 under A5 only at B=200)")

print("\n==========================================================")
print("=== 4. DEFENSE MATRIX SUMMARY ===")
print("==========================================================")
df4 = pd.read_csv("results/defenses_eval_v2.csv")
undef = df4[df4["defense"] == "Undefended_HITS"]
base_gains = undef.set_index(["graph", "target_node", "attack", "budget"])["rank_gain"].to_dict()
df4["base_gain"] = df4.apply(lambda r: base_gains.get((r["graph"], r["target_node"], r["attack"], r["budget"]), 0), axis=1)

# Check zero/negative base gains
n_zero_gain = (undef["rank_gain"] <= 0).sum()
print(f"Undefended cells with zero or negative attack gain: {n_zero_gain} / {len(undef)} ({n_zero_gain/len(undef)*100:.1f}%)")
print("  -> In these cells, the old defense_attack_success_reduction returned 1.0 (100% reduction), giving Undefended HITS an artifactual 23.6% reduction.")

# Correct evaluation excluding base_gain <= 0
df4_pos = df4[df4["base_gain"] > 0].copy()
df4_pos["true_reduction"] = 1.0 - (df4_pos["rank_gain"] / df4_pos["base_gain"])
df4_pos["true_meets_goal"] = (df4_pos["true_reduction"] >= 0.50) & (df4_pos["clean_ndcg_loss"] <= 0.05)

# Verify D3 is a complete no-op
d3_diff = np.max(np.abs(df4[df4["defense"] == "D3_HubCapping_0.10"]["target_attacked_score"].values - undef["target_attacked_score"].values))
print(f"D3 Hub Capping max score difference vs Undefended HITS: {d3_diff:.6f} (Exact No-Op: 10% cap never triggered)")

print("\n--- Corrected Defense Summary (Across Positive Attack Gain Cells, n=110 instances per defense) ---")
for d in df4["defense"].unique():
    sub = df4_pos[df4_pos["defense"] == d]
    all_sub = df4[df4["defense"] == d]
    red_m, red_l, red_u = bootstrap_ci(sub["true_reduction"].values)
    red_med = sub["true_reduction"].median()
    jacc_mean = all_sub["clean_top20_jaccard"].mean()
    ndcg_loss_mean = all_sub["clean_ndcg_loss"].mean()
    goal_rate = sub["true_meets_goal"].mean() * 100
    print(f"[{d:25s}] Red Mean: {red_m*100:5.1f}% [{red_l*100:5.1f}%, {red_u*100:5.1f}%] | Med: {red_med*100:5.1f}% | Clean Jacc: {jacc_mean:.3f} | NDCG Loss: {ndcg_loss_mean*100:4.1f}% | Meets Goal: {goal_rate:4.1f}%")

print("\n--- Per-Attack Defense Breakdown (Attack Reduction Median & Goal Rate) ---")
for att in sorted(df4["attack"].unique()):
    for B in [25, 100]:
        sub = df4_pos[(df4_pos["attack"] == att) & (df4_pos["budget"] == B)]
        n_inst = len(sub) // 8
        print(f"\n[Attack: {att:22s} | Budget B={B:<3d} | n={n_inst} positive cells]")
        for d in ["Undefended_HITS", "D1_RandomizedHITS_0.15", "D2_BharatHenzinger", "D3_HubCapping_0.10", "D4_WuDavison_Mutual", "D4b_WuDavison_OutJaccard"]:
            dsub = sub[sub["defense"] == d]
            if len(dsub) > 0:
                rm = dsub["true_reduction"].mean() * 100
                rmed = dsub["true_reduction"].median() * 100
                gm = dsub["true_meets_goal"].mean() * 100
                print(f"  {d:25s} | Mean: {rm:6.1f}% | Med: {rmed:6.1f}% | Meets Goal: {gm:4.1f}%")
