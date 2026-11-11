"""Final Evidence Pack Aggregator: Computes exact figures, tables, CIs, and metrics for FINAL_REPORT_FACTS.md."""
import sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd

from src.eval.stats import bootstrap_ci, wilcoxon_test, holm_bonferroni


def compute_all_final_facts():
    print("==================================================================")
    print("=== FINAL EVIDENCE PACK COMPUTATION ===")
    print("==================================================================")

    # 1. H1 & H3 Facts
    print("\n--- 1. H1 & H3 FACTS (results/h1_h3_eval_v3.csv) ---")
    df_h1h3 = pd.read_csv("results/h1_h3_eval_v3.csv")
    df_h1 = df_h1h3[df_h1h3["hypothesis"] == "H1"]
    print(f"H1 Total Instances: n={len(df_h1)} across 5 ER random graph seeds")
    m_h10, l_h10, u_h10 = bootstrap_ci(df_h1["b_star_hits_k10"].values)
    m_d10, l_d10, u_d10 = bootstrap_ci(df_h1["b_star_indeg_k10"].values)
    m_r10, l_r10, u_r10 = bootstrap_ci(df_h1["ratio_k10"].values)
    stat10, p10 = wilcoxon_test(df_h1["b_star_hits_k10"].values, df_h1["b_star_indeg_k10"].values)
    print(f"  H1 B*(10) HITS: {m_h10:.2f} [{l_h10:.2f}, {u_h10:.2f}] | In-Degree: {m_d10:.2f} [{l_d10:.2f}, {u_d10:.2f}]")
    print(f"  H1 B*(10) Cost Ratio: {m_r10:.3f} [{l_r10:.3f}, {u_r10:.3f}] | Wilcoxon p={p10:.2e}")

    m_h1, l_h1, u_h1 = bootstrap_ci(df_h1["b_star_hits_k1"].values)
    m_d1, l_d1, u_d1 = bootstrap_ci(df_h1["b_star_indeg_k1"].values)
    m_r1, l_r1, u_r1 = bootstrap_ci(df_h1["ratio_k1"].values)
    stat1, p1 = wilcoxon_test(df_h1["b_star_hits_k1"].values, df_h1["b_star_indeg_k1"].values)
    print(f"  H1 B*(1)  HITS: {m_h1:.2f} [{l_h1:.2f}, {u_h1:.2f}] | In-Degree: {m_d1:.2f} [{l_d1:.2f}, {u_d1:.2f}]")
    print(f"  H1 B*(1)  Cost Ratio: {m_r1:.3f} [{l_r1:.3f}, {u_r1:.3f}] | Wilcoxon p={p1:.2e}")

    df_h3 = df_h1h3[df_h1h3["hypothesis"] == "H3"]
    print(f"\nH3 Total Instances: n={len(df_h3)} (15 SBM Planted, 15 ER Control)")
    for g in ["SBM_Planted", "ER_Control"]:
        sub = df_h3[df_h3["graph"] == g]
        m_s, l_s, u_s = bootstrap_ci(sub["cost_saving_pct"].dropna().values)
        print(f"  H3 {g:12s} Cost Savings (A5 vs A2): {m_s:.1f}% [{l_s:.1f}%, {u_s:.1f}%] (n={len(sub)})")

    # 2. H2 Facts
    print("\n--- 2. H2 SPECTRAL TAKEOVER FACTS (results/h2_robustness_v3.csv) ---")
    df_h2 = pd.read_csv("results/h2_robustness_v3.csv")
    print(f"H2 Total Instances: n={len(df_h2)} (5 graphs x 5 seeds x 5 targets)")
    ge_rate = df_h2["sigma1_sq_ge_max_indeg"].mean() * 100.0
    abrupt_rate = df_h2["is_hits_jump_abrupt"].mean() * 100.0
    m_rat10, l_rat10, u_rat10 = bootstrap_ci(df_h2["ratio_p_star_10_to_sigma1_sq"].dropna().values)
    m_rat1, l_rat1, u_rat1 = bootstrap_ci(df_h2["ratio_p_star_1_to_sigma1_sq"].dropna().values)
    print(f"  Property sigma1^2 >= max in-degree: {ge_rate:.1f}% ({df_h2['sigma1_sq_ge_max_indeg'].sum()}/{len(df_h2)})")
    print(f"  Abrupt Spectral Takeover Rate: {abrupt_rate:.1f}% ({df_h2['is_hits_jump_abrupt'].sum()}/{len(df_h2)})")
    print(f"  Counterexamples: {(100.0-abrupt_rate):.1f}% ({(~df_h2['is_hits_jump_abrupt']).sum()}/{len(df_h2)})")
    print(f"  Mean max rank jump: HITS={df_h2['max_hits_step_jump'].mean():.1f} ranks vs PageRank={df_h2['max_pagerank_step_jump'].mean():.1f} ranks")
    print(f"  p*(10) / sigma1^2: {m_rat10:.3f} [{l_rat10:.3f}, {u_rat10:.3f}]")
    print(f"  p*(1)  / sigma1^2: {m_rat1:.3f} [{l_rat1:.3f}, {u_rat1:.3f}]")

    abrupt_cases = df_h2[df_h2["is_hits_jump_abrupt"]]
    counter_cases = df_h2[~df_h2["is_hits_jump_abrupt"]]
    print(f"  Diagnostic: Abrupt mean eigengap = {abrupt_cases['eigengap'].mean():.2f} vs Counterexample mean eigengap = {counter_cases['eigengap'].mean():.2f}")

    # 3. WEBSPAM Facts
    print("\n--- 3. WEBSPAM-UK2006 FACTS (results/webspam_eval.csv) ---")
    df_web = pd.read_csv("results/webspam_eval.csv")
    print(df_web[["algorithm", "spam@10", "spam@20", "spam@50", "spam@100", "test_set2_auc", "test_set2_f1"]].to_string(index=False))

    # 4. Defenses Facts
    print("\n--- 4. DEFENSE MATRIX FACTS (results/defenses_eval_v3.csv) ---")
    df_def = pd.read_csv("results/defenses_eval_v3.csv")
    df_pos = df_def[df_def["base_gain"] > 0]
    for d in df_def["defense"].unique():
        sub = df_pos[df_pos["defense"] == d]
        all_sub = df_def[df_def["defense"] == d]
        m_r, l_r, u_r = bootstrap_ci(sub["attack_reduction"].values)
        med_r = sub["attack_reduction"].median() * 100.0
        m_loss, _, _ = bootstrap_ci(all_sub["clean_ndcg_loss"].values)
        m_jacc, _, _ = bootstrap_ci(all_sub["clean_jaccard_20"].values)
        gm = sub["meets_goal"].mean() * 100.0
        print(f"  {d:30s} | Red Med: {med_r:5.1f}% | Mean: {m_r*100:5.1f}% [{l_r*100:5.1f}%, {u_r*100:5.1f}%] | NDCG Loss: {m_loss*100:4.1f}% | Jacc: {m_jacc:.3f} | Meets Goal: {gm:4.1f}%")

    # 5. Stretch Facts
    print("\n--- 5. STRETCH OBJECTIVES FACTS ---")
    df_reg = pd.read_csv("results/empirical_bound_regression.csv")
    print("Empirical Spectral Bound Regressions:")
    print(df_reg.to_string(index=False))

    df_loop = pd.read_csv("results/attacker_defender_loop.csv")
    print("\n3-Round Attacker-Defender Game Loop:")
    print(df_loop.to_string(index=False))


if __name__ == "__main__":
    compute_all_final_facts()

