"""Block 0 Housekeeping & Audit Verification Script.

Fixes & verifies:
a. A4 vs A4b vs A5 duplicate analysis
b. D3 Hub Capping sensitivity sweep (cap_fraction in 0.5%, 1%, 2%, 5%, 10%)
c. A4 budget-limited verification
d. Per-attack Wilcoxon tests aggregated over seeds per (graph, target) with Holm correction
"""
import sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd
import scipy.sparse as sp
import networkx as nx

from src.eval.stats import bootstrap_ci, wilcoxon_test, holm_bonferroni
from src.data.synthetic import generate_barabasi_albert, generate_erdos_renyi, generate_planted_bipartite_sbm
from src.rankers.hits import hits
from src.defenses.d3_hub_capping import hub_capped_hits
from src.attacks.a2_hub_farm import attack_a2_hub_farm


def audit_a4_a5_construction():
    print("=================================================================")
    print("--- 1. AUDIT A4 vs A4b vs A5 DUPLICATION ANALYSIS ---")
    print("=================================================================")
    print("Summary of code inspection:")
    print("  - A4 (Proposal): Single node (target or 1 fake) links to top c authorities.")
    print("    Max edges spent = c. Flat curve above budget c is by construction, NOT failure.")
    print("  - A4b (Multi-hub): p fake hubs each link to target and c authorities.")
    print("  - A5 (Proposal): p fake hubs each link to target and c authorities.")
    print("  -> A4b and A5 have identical graph topology and edge sets.")
    print("  -> Recommendation: De-duplicate by retaining A4 (proposal single/target-hub) and")
    print("     A5 (cross-score multi-hub), testing A5b (cross-links) as the multi-hub extension.")


def audit_d3_hub_capping():
    print("\n=================================================================")
    print("--- 2. D3 HUB CAPPING SENSITIVITY SWEEP & MECHANISM ANALYSIS ---")
    print("=================================================================")
    graphs = {
        "BA-500": generate_barabasi_albert(500, seed=42),
        "ER-500": generate_erdos_renyi(500, seed=42),
        "SBM-500": generate_planted_bipartite_sbm(460, 20, 20, seed=42)[0]
    }

    caps = [0.005, 0.01, 0.02, 0.05, 0.10]
    sweep_results = []

    for gname, G in graphs.items():
        h_clean = hits(G)
        clean_hub_share = h_clean.hub_scores / h_clean.hub_scores.sum()
        max_clean_hub = np.max(clean_hub_share)
        pct99_clean = np.percentile(clean_hub_share, 99)

        # Attacked with A2 at B=50
        att_res = attack_a2_hub_farm(G, target_node=10, budget=50)
        h_att = hits(att_res.graph)
        att_hub_share = h_att.hub_scores / h_att.hub_scores.sum()
        max_att_hub = np.max(att_hub_share)
        pct99_att = np.percentile(att_hub_share, 99)

        print(f"Graph: {gname:8s} | Clean max hub share: {max_clean_hub*100:5.2f}% (99th: {pct99_clean*100:5.2f}%) "
              f"| Attacked (A2 B=50) max hub: {max_att_hub*100:5.2f}%")

        for cap in caps:
            def_clean = hub_capped_hits(G, cap_fraction=cap)
            diff_clean = np.max(np.abs(def_clean.scores - h_clean.scores))
            binds_clean = diff_clean > 1e-7

            def_att = hub_capped_hits(att_res.graph, cap_fraction=cap)
            diff_att = np.max(np.abs(def_att.scores - h_att.scores))
            binds_att = diff_att > 1e-7

            sweep_results.append({
                "graph": gname,
                "cap_fraction": cap,
                "max_clean_hub_pct": max_clean_hub * 100,
                "max_att_hub_pct": max_att_hub * 100,
                "binds_clean": binds_clean,
                "diff_clean": diff_clean,
                "binds_att": binds_att,
                "diff_att": diff_att
            })

    sweep_df = pd.DataFrame(sweep_results)
    print("\n--- Cap Sensitivity Sweep Results ---")
    print(sweep_df.to_string(index=False))
    sweep_df.to_csv("results/d3_sensitivity_sweep.csv", index=False)
    print("Saved results to results/d3_sensitivity_sweep.csv")


def audit_per_attack_wilcoxon():
    print("\n=================================================================")
    print("--- 3. PER-ATTACK WILCOXON TESTS (AGGREGATED BY GRAPH & TARGET) ---")
    print("=================================================================")
    df = pd.read_csv("results/cost_curves_v2.csv")
    sub100 = df[df["budget"] == 100].copy()

    # Aggregate over seeds first per (graph, target_node, attack, ranker)
    agg = sub100.groupby(["graph", "target_node", "attack", "ranker"])["normalized_rank_gain"].mean().reset_index()

    attacks = sorted(agg["attack"].unique())
    baselines = ["PageRank", "SALSA", "InDegree"]

    all_test_records = []
    raw_p_values = []

    for att in attacks:
        att_df = agg[agg["attack"] == att]
        # Pivot by ranker
        piv = att_df.pivot(index=["graph", "target_node"], columns="ranker", values="normalized_rank_gain").dropna()
        n_obs = len(piv)

        for b in baselines:
            if b in piv.columns and "HITS" in piv.columns:
                h_vals = piv["HITS"].values
                b_vals = piv[b].values
                stat, p_val = wilcoxon_test(h_vals, b_vals)
                h_mean, _, _ = bootstrap_ci(h_vals)
                b_mean, _, _ = bootstrap_ci(b_vals)
                diff_mean = h_mean - b_mean
                raw_p_values.append(p_val)
                all_test_records.append({
                    "attack": att,
                    "baseline": b,
                    "n_independent_units": n_obs,
                    "hits_mean_gain": h_mean,
                    "baseline_mean_gain": b_mean,
                    "diff_mean": diff_mean,
                    "stat": stat,
                    "raw_p": p_val
                })

    rej, adj_p = holm_bonferroni(raw_p_values)
    for i, r in enumerate(all_test_records):
        r["holm_adj_p"] = adj_p[i]
        r["rejected"] = rej[i]

    res_df = pd.DataFrame(all_test_records)
    print(res_df.to_string(index=False))
    res_df.to_csv("results/wilcoxon_per_attack_v2.csv", index=False)
    print("Saved independent per-attack Wilcoxon tests to results/wilcoxon_per_attack_v2.csv")


if __name__ == "__main__":
    audit_a4_a5_construction()
    audit_d3_hub_capping()
    audit_per_attack_wilcoxon()
