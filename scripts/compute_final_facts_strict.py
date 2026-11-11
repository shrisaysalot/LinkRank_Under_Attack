"""Compute exact statistics for docs/FINAL_REPORT_FACTS.md strictly from *_final.csv files."""
import pandas as pd
import numpy as np


def bootstrap_ci(arr, n_boot=1000, alpha=0.05, seed=42):
    rng = np.random.default_rng(seed)
    arr = np.asarray(arr)
    arr = arr[~np.isnan(arr)]
    if len(arr) == 0:
        return np.nan, (np.nan, np.nan)
    boot_means = [np.mean(rng.choice(arr, size=len(arr), replace=True)) for _ in range(n_boot)]
    low = np.percentile(boot_means, 100 * (alpha / 2))
    high = np.percentile(boot_means, 100 * (1 - alpha / 2))
    return float(np.mean(arr)), (float(low), float(high))


def main():
    print("=" * 70)
    print("COMPUTING EXACT FINAL FACTS FROM FINAL CSV FILES")
    print("=" * 70)

    # 1. H1 & H3
    h13 = pd.read_csv("results/h1_h3_eval_final.csv")
    h1 = h13[h13["hypothesis"] == "H1"]
    print("\n--- H1 In-Degree vs HITS on ER (n = len(h1)) ---")
    print(f"H1 n = {len(h1)}")
    b10_ind_m, b10_ind_ci = bootstrap_ci(h1["b_star_indeg_k10"])
    b10_hits_m, b10_hits_ci = bootstrap_ci(h1["b_star_hits_k10"])
    r10_m, r10_ci = bootstrap_ci(h1["ratio_k10"])
    print(f"B*(10) InDegree: {b10_ind_m:.2f} [{b10_ind_ci[0]:.2f}, {b10_ind_ci[1]:.2f}]")
    print(f"B*(10) HITS:     {b10_hits_m:.2f} [{b10_hits_ci[0]:.2f}, {b10_hits_ci[1]:.2f}]")
    print(f"B*(10) Ratio:    {r10_m:.3f} [{r10_ci[0]:.3f}, {r10_ci[1]:.3f}]")
    b1_ind_m, b1_ind_ci = bootstrap_ci(h1["b_star_indeg_k1"])
    b1_hits_m, b1_hits_ci = bootstrap_ci(h1["b_star_hits_k1"])
    r1_m, r1_ci = bootstrap_ci(h1["ratio_k1"])
    print(f"B*(1) InDegree:  {b1_ind_m:.2f} [{b1_ind_ci[0]:.2f}, {b1_ind_ci[1]:.2f}]")
    print(f"B*(1) HITS:      {b1_hits_m:.2f} [{b1_hits_ci[0]:.2f}, {b1_hits_ci[1]:.2f}]")
    print(f"B*(1) Ratio:     {r1_m:.3f} [{r1_ci[0]:.3f}, {r1_ci[1]:.3f}]")

    h3 = h13[h13["hypothesis"] == "H3"]
    print("\n--- H3 Community Attachment A2 vs A5 up to B=500 ---")
    for gtype, grp in h3.groupby("graph"):
        saving_m, saving_ci = bootstrap_ci(grp["cost_saving_pct"])
        print(f"Graph {gtype} (n={len(grp)}): Cost Saving: {saving_m*100:.1f}% [{saving_ci[0]*100:.1f}%, {saving_ci[1]*100:.1f}%]")

    # 2. H2 Spectral Takeover
    h2 = pd.read_csv("results/h2_robustness_final.csv")
    print("\n--- H2 Spectral Takeover (n = len(h2)) ---")
    print(f"H2 n = {len(h2)}")
    sigma_holds = h2["sigma1_sq_ge_max_indeg"].mean()
    abrupt_rate = h2["is_hits_jump_abrupt"].mean()
    print(f"sigma1^2 >= max(d_in) holds: {sigma_holds*100:.1f}% ({int(h2['sigma1_sq_ge_max_indeg'].sum())}/{len(h2)})")
    print(f"Abrupt takeover rate:        {abrupt_rate*100:.1f}% ({int(h2['is_hits_jump_abrupt'].sum())}/{len(h2)})")
    p10_m, p10_ci = bootstrap_ci(h2["ratio_p_star_10_to_sigma1_sq"])
    p1_m, p1_ci = bootstrap_ci(h2["ratio_p_star_1_to_sigma1_sq"])
    print(f"p*(10) / sigma1^2: {p10_m:.3f} [{p10_ci[0]:.3f}, {p10_ci[1]:.3f}]")
    print(f"p*(1) / sigma1^2:  {p1_m:.3f} [{p1_ci[0]:.3f}, {p1_ci[1]:.3f}]")
    jump_hits_m, _ = bootstrap_ci(h2["max_hits_step_jump"])
    jump_pr_m, _ = bootstrap_ci(h2["max_pagerank_step_jump"])
    print(f"Mean single-step jump: HITS = {jump_hits_m:.1f} ranks vs PageRank = {jump_pr_m:.1f} ranks")
    # Counterexamples
    non_abrupt = h2[~h2["is_hits_jump_abrupt"]]
    abrupt = h2[h2["is_hits_jump_abrupt"]]
    print(f"Eigengap: Abrupt = {abrupt['eigengap'].mean():.2f} vs Non-Abrupt = {non_abrupt['eigengap'].mean():.2f}")
    print(f"Initial Rank: Abrupt = {abrupt['clean_h_rank'].mean():.1f} vs Non-Abrupt = {non_abrupt['clean_h_rank'].mean():.1f}")

    # 3. Defenses Eval Final (Positive base_gain only)
    def_df = pd.read_csv("results/defenses_eval_final.csv")
    pos_def = def_df[def_df["base_gain"] > 0]
    print("\n--- Defenses Evaluation (Positive Base Gain cells, n per defense) ---")
    def_summary = []
    for d, grp in pos_def.groupby("defense"):
        med_red = grp["attack_reduction"].median()
        mean_red, mean_red_ci = bootstrap_ci(grp["attack_reduction"])
        ndcg_l = grp["clean_ndcg_loss"].mean()
        jacc = grp["clean_jaccard_20"].mean()
        meets = grp["meets_goal"].mean()
        rt = grp["runtime_s"].mean()
        def_summary.append({
            "defense": d, "n": len(grp),
            "med_red": med_red, "mean_red": mean_red, "mean_red_ci": mean_red_ci,
            "ndcg_loss": ndcg_l, "jaccard": jacc, "meets_goal": meets, "runtime": rt
        })
    df_def_sum = pd.DataFrame(def_summary)
    print(df_def_sum[["defense", "n", "med_red", "mean_red", "ndcg_loss", "jaccard", "meets_goal", "runtime"]].to_string())

    # D4 per attack
    d4_pos = pos_def[pos_def["defense"] == "D4_WuDavison_Mutual_0.5"]
    print("\n--- D4 Wu-Davison per Attack ---")
    for att, grp in d4_pos.groupby("attack"):
        print(f"{att:25s} | n={len(grp):2d} | Median Red: {grp['attack_reduction'].median()*100:5.1f}% | Mean Red: {grp['attack_reduction'].mean()*100:5.1f}% | Meets Goal: {grp['meets_goal'].mean()*100:5.1f}%")

    # 4. WEBSPAM Final
    ws_clean = pd.read_csv("results/webspam_clean_ranking_final.csv")
    print("\n--- WEBSPAM Clean Ranking Final Summary (All Labeled, N=10,236) ---")
    ws_all = ws_clean[ws_clean["eval_split"] == "All_Labeled"]
    print(ws_all[["ranker", "spam_at_100", "spam_at_500", "spam_at_1000", "spam_at_2000", "median_spam_rank", "median_norm_rank", "auc_spam_high_score", "prev_aware_f1", "runtime_s"]].to_string())

    ws_att = pd.read_csv("results/webspam_attack_final.csv")
    print("\n--- WEBSPAM Host Graph Attack Final Summary (10 Targets x 3 Budgets x 2 Attacks) ---")
    print(f"Total attack rows: {len(ws_att)}")
    print(f"A2 max rank change: {ws_att[ws_att['attack']=='A2_HubFarm']['rank_change_hits'].max()}")
    print(f"A5 max rank change: {ws_att[ws_att['attack']=='A5_CrossScore']['rank_change_hits'].max()}")
    print(f"HITS Top-100 entry count: {ws_att['top100_entry_hits'].sum()} (0%)")
    print(f"HITS Takeover count:      {ws_att['takeover_occurred_hits'].sum()} (0%)")
    print(f"PageRank Top-100 entry count at B=1000: {(ws_att[ws_att['budget']==1000]['attacked_rank_pagerank'] <= 100).sum()}/{len(ws_att[ws_att['budget']==1000])}")


if __name__ == "__main__":
    main()
