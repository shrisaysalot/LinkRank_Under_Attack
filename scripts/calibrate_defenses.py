"""Defense Calibration & Parameter Tuning Script.

Performs parameter sweeps on an INDEPENDENT calibration graph (seed 9999)
to tune defense parameters prior to full-scale evaluation, preventing data leakage:
- D1: Random reset probability eps in [0.05, 0.10, 0.15, 0.20, 0.25]
- D3: Hub cap fraction in [0.005, 0.01, 0.02, 0.05, 0.10]
- D4 / D4b: Link farm overlap threshold in [0.3, 0.4, 0.5, 0.6, 0.7]
- D5: Trust seed selection (In-Degree vs Clean PageRank vs Random) and seed count k in [5, 10, 20, 50]

Selects thresholds that maximize attack reduction while maintaining <= 5% clean NDCG@20 loss.
"""
import sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import time
import numpy as np
import pandas as pd
import networkx as nx

from src.data.synthetic import generate_barabasi_albert, generate_erdos_renyi
from src.rankers import hits, pagerank, indegree
from src.rankers.randomized_hits import randomized_hits
from src.defenses.d3_hub_capping import hub_capped_hits
from src.defenses.d4_wu_davison import wu_davison_hits, wu_davison_outlink_jaccard_hits
from src.defenses.d5_trust_hits import trust_based_hits
from src.attacks.a2_hub_farm import attack_a2_hub_farm
from src.attacks.a5_cross_score import attack_a5_cross_score
from src.eval import compute_rank, ndcg_at_k, top_k_jaccard


def run_defense_calibration():
    print("==================================================================")
    print("=== DEFENSE CALIBRATION ON INDEPENDENT GRAPH (SEED 9999) ===")
    print("==================================================================")
    t0 = time.time()
    calib_seed = 9999
    # Independent Barabasi-Albert graph for calibration
    G_calib = generate_barabasi_albert(n=500, m=4, seed=calib_seed)
    n = G_calib.number_of_nodes()

    # Clean unattacked baseline
    clean_h = hits(G_calib).scores
    clean_pr = pagerank(G_calib).scores
    clean_deg = indegree(G_calib).scores

    # Pick 3 calibration targets
    sorted_idx = np.argsort(clean_h)
    calib_targets = [int(sorted_idx[int(n * f)]) for f in [0.25, 0.50, 0.75]]

    records = []

    # 1. D1 Randomized HITS (eps sweep)
    print("Calibrating D1 (eps sweep)...")
    for eps in [0.05, 0.10, 0.15, 0.20, 0.25]:
        def_clean = randomized_hits(G_calib, eps=eps).scores
        clean_loss = 1.0 - ndcg_at_k(clean_h, def_clean, k=20)
        clean_jacc = top_k_jaccard(clean_h, def_clean, k=20)

        for target in calib_targets:
            c_rank = compute_rank(clean_h, target)
            for B in [25, 100]:
                att = attack_a2_hub_farm(G_calib, target, budget=B)
                undef_rank = compute_rank(hits(att.graph).scores, target)
                def_rank = compute_rank(randomized_hits(att.graph, eps=eps).scores, target)

                base_gain = max(0, c_rank - undef_rank)
                def_gain = max(0, c_rank - def_rank)
                reduction = (1.0 - (def_gain / base_gain)) if base_gain > 0 else 0.0

                records.append({
                    "defense": "D1_RandomizedHITS",
                    "parameter": "eps",
                    "value": eps,
                    "budget": B,
                    "target": target,
                    "clean_ndcg_loss": clean_loss,
                    "clean_jaccard": clean_jacc,
                    "undef_gain": base_gain,
                    "def_gain": def_gain,
                    "reduction": reduction,
                    "meets_goal": bool(reduction >= 0.50 and clean_loss <= 0.05)
                })

    # 2. D3 Hub Capping (cap_fraction sweep)
    print("Calibrating D3 (cap_fraction sweep)...")
    for cap in [0.005, 0.01, 0.02, 0.05, 0.10]:
        def_clean = hub_capped_hits(G_calib, cap_fraction=cap).scores
        clean_loss = 1.0 - ndcg_at_k(clean_h, def_clean, k=20)
        clean_jacc = top_k_jaccard(clean_h, def_clean, k=20)

        for target in calib_targets:
            c_rank = compute_rank(clean_h, target)
            for B in [25, 100]:
                att = attack_a2_hub_farm(G_calib, target, budget=B)
                undef_rank = compute_rank(hits(att.graph).scores, target)
                def_rank = compute_rank(hub_capped_hits(att.graph, cap_fraction=cap).scores, target)

                base_gain = max(0, c_rank - undef_rank)
                def_gain = max(0, c_rank - def_rank)
                reduction = (1.0 - (def_gain / base_gain)) if base_gain > 0 else 0.0

                records.append({
                    "defense": "D3_HubCapping",
                    "parameter": "cap_fraction",
                    "value": cap,
                    "budget": B,
                    "target": target,
                    "clean_ndcg_loss": clean_loss,
                    "clean_jaccard": clean_jacc,
                    "undef_gain": base_gain,
                    "def_gain": def_gain,
                    "reduction": reduction,
                    "meets_goal": bool(reduction >= 0.50 and clean_loss <= 0.05)
                })

    # 3. D4 and D4b Overlap Threshold Sweep
    print("Calibrating D4 and D4b (overlap_threshold sweep)...")
    for thresh in [0.3, 0.4, 0.5, 0.6, 0.7]:
        # D4b Outlink Jaccard
        def_clean_4b = wu_davison_outlink_jaccard_hits(G_calib, overlap_threshold=thresh).scores
        loss_4b = 1.0 - ndcg_at_k(clean_h, def_clean_4b, k=20)
        jacc_4b = top_k_jaccard(clean_h, def_clean_4b, k=20)

        # D4 Mutual
        def_clean_4 = wu_davison_hits(G_calib, out_threshold=thresh).scores
        loss_4 = 1.0 - ndcg_at_k(clean_h, def_clean_4, k=20)
        jacc_4 = top_k_jaccard(clean_h, def_clean_4, k=20)

        for target in calib_targets:
            c_rank = compute_rank(clean_h, target)
            for B in [25, 100]:
                att = attack_a2_hub_farm(G_calib, target, budget=B)
                undef_rank = compute_rank(hits(att.graph).scores, target)
                base_gain = max(0, c_rank - undef_rank)

                # D4b
                def_r_4b = compute_rank(wu_davison_outlink_jaccard_hits(att.graph, overlap_threshold=thresh).scores, target)
                gain_4b = max(0, c_rank - def_r_4b)
                red_4b = (1.0 - (gain_4b / base_gain)) if base_gain > 0 else 0.0
                records.append({
                    "defense": "D4b_WuDavison_OutJaccard",
                    "parameter": "overlap_threshold",
                    "value": thresh,
                    "budget": B,
                    "target": target,
                    "clean_ndcg_loss": loss_4b,
                    "clean_jaccard": jacc_4b,
                    "undef_gain": base_gain,
                    "def_gain": gain_4b,
                    "reduction": red_4b,
                    "meets_goal": bool(red_4b >= 0.50 and loss_4b <= 0.05)
                })

                # D4
                def_r_4 = compute_rank(wu_davison_hits(att.graph, out_threshold=thresh).scores, target)
                gain_4 = max(0, c_rank - def_r_4)
                red_4 = (1.0 - (gain_4 / base_gain)) if base_gain > 0 else 0.0
                records.append({
                    "defense": "D4_WuDavison_Mutual",
                    "parameter": "out_threshold",
                    "value": thresh,
                    "budget": B,
                    "target": target,
                    "clean_ndcg_loss": loss_4,
                    "clean_jaccard": jacc_4,
                    "undef_gain": base_gain,
                    "def_gain": gain_4,
                    "reduction": red_4,
                    "meets_goal": bool(red_4 >= 0.50 and loss_4 <= 0.05)
                })

    # 4. D5 Trust Seed Size and Type Comparison
    print("Calibrating D5 (Trust seed strategy & size)...")
    pr_sorted = np.argsort(-clean_pr)
    deg_sorted = np.argsort(-clean_deg)
    rng = np.random.RandomState(42)

    for seed_strategy, seed_pool in [
        ("CleanPageRank_TopK", pr_sorted),
        ("InDegree_TopK", deg_sorted),
        ("RandomNodes", rng.permutation(n))
    ]:
        for k_seeds in [5, 10, 20, 50]:
            chosen_seeds = list(seed_pool[:k_seeds])
            def_clean = trust_based_hits(G_calib, trusted_seeds=chosen_seeds, eps=0.15).scores
            clean_loss = 1.0 - ndcg_at_k(clean_h, def_clean, k=20)
            clean_jacc = top_k_jaccard(clean_h, def_clean, k=20)

            for target in calib_targets:
                c_rank = compute_rank(clean_h, target)
                for B in [25, 100]:
                    att = attack_a2_hub_farm(G_calib, target, budget=B)
                    undef_rank = compute_rank(hits(att.graph).scores, target)
                    base_gain = max(0, c_rank - undef_rank)

                    def_rank = compute_rank(trust_based_hits(att.graph, trusted_seeds=chosen_seeds, eps=0.15).scores, target)
                    gain_d5 = max(0, c_rank - def_rank)
                    red_d5 = (1.0 - (gain_d5 / base_gain)) if base_gain > 0 else 0.0

                    records.append({
                        "defense": f"D5_TrustHITS_{seed_strategy}",
                        "parameter": "k_seeds",
                        "value": k_seeds,
                        "budget": B,
                        "target": target,
                        "clean_ndcg_loss": clean_loss,
                        "clean_jaccard": clean_jacc,
                        "undef_gain": base_gain,
                        "def_gain": gain_d5,
                        "reduction": red_d5,
                        "meets_goal": bool(red_d5 >= 0.50 and clean_loss <= 0.05)
                    })

    df_calib = pd.DataFrame(records)
    out_csv = Path("results/defense_calibration_sweeps.csv")
    df_calib.to_csv(out_csv, index=False)
    print(f"\n[DONE Calibration] Saved {len(df_calib)} calibration records to {out_csv} in {time.time()-t0:.1f}s")

    # Aggregate by defense and parameter
    print("\n--- Calibration Parameter Recommendations ---")
    agg = df_calib.groupby(["defense", "parameter", "value"]).agg({
        "reduction": "mean",
        "clean_ndcg_loss": "first",
        "clean_jaccard": "first",
        "meets_goal": "mean"
    }).reset_index()

    for d in sorted(agg["defense"].unique()):
        sub = agg[agg["defense"] == d]
        print(f"\n[{d}]")
        print(sub[["value", "reduction", "clean_ndcg_loss", "clean_jaccard", "meets_goal"]].to_string(index=False))

    return df_calib


if __name__ == "__main__":
    run_defense_calibration()

