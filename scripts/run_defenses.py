"""Defense evaluation experiment: Evaluates D1-D5 attack-success reduction and clean graph false demotion."""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import time
import numpy as np
import pandas as pd
import networkx as nx

from src.config import RESULTS_DIR, DEFAULT_SEED
from src.data.synthetic import generate_barabasi_albert
from src.rankers import hits
from src.attacks.a2_hub_farm import attack_a2_hub_farm
from src.attacks.a4_hub_inflation import attack_a4_hub_inflation
from src.defenses import (
    randomized_hits,
    subspace_hits,
    bharat_henzinger_hits,
    hub_capped_hits,
    wu_davison_hits,
    trust_based_hits,
)
from src.eval.metrics import (
    compute_rank,
    rank_gain,
    top_k_jaccard,
    ndcg_at_k,
    defense_attack_success_reduction,
)


def run_defenses_experiment():
    print("=== Running Defenses Evaluation Experiment (D1-D5) ===")
    t_start = time.perf_counter()

    n = 400
    G_clean = generate_barabasi_albert(n=n, m=4, seed=DEFAULT_SEED)

    # Clean HITS baseline
    clean_hits_res = hits(G_clean)
    clean_hits_scores = clean_hits_res.scores

    # Pick a low-to-medium rank target
    order = np.argsort(clean_hits_scores)
    target_node = int(order[int(n * 0.3)])
    clean_target_rank = compute_rank(clean_hits_scores, target_node)
    print(f"Graph: {n} nodes, {G_clean.number_of_edges()} edges")
    print(f"Target node: {target_node} | Clean HITS rank: {clean_target_rank}/{n}")

    defenses = {
        "Undefended_HITS": lambda g: hits(g),
        "D1_RandomizedHITS_0.15": lambda g: randomized_hits(g, eps=0.15),
        "D1_SubspaceHITS_k5": lambda g: subspace_hits(g, k=5),
        "D2_BharatHenzinger": lambda g: bharat_henzinger_hits(g),
        "D3_HubCapping_0.10": lambda g: hub_capped_hits(g, cap_fraction=0.10),
        "D4_WuDavison": lambda g: wu_davison_hits(g),
        "D5_TrustHITS": lambda g: trust_based_hits(g),
    }

    # 1. Evaluate clean fidelity (False Demotion / Distortion on unattacked graph)
    print("\n--- Evaluating Clean Graph Fidelity (False Demotion) ---")
    clean_records = {}
    for def_name, def_fn in defenses.items():
        res_clean = def_fn(G_clean)
        jacc = top_k_jaccard(clean_hits_scores, res_clean.scores, k=20)
        ndcg = ndcg_at_k(clean_hits_scores, res_clean.scores, k=20)
        c_rank = compute_rank(res_clean.scores, target_node)
        clean_records[def_name] = {
            "clean_top20_jaccard": jacc,
            "clean_top20_ndcg": ndcg,
            "clean_target_rank": c_rank,
            "false_demotion": 1.0 - jacc,
        }
        print(f"[{def_name:24s}] Clean Jaccard@20: {jacc:.4f} | NDCG@20: {ndcg:.4f} | False Demotion: {1.0 - jacc:.4f}")

    # 2. Evaluate under attacks
    attacks = {
        "A2_HubFarm_B25": lambda g, t: attack_a2_hub_farm(g, t, budget=25),
        "A2_HubFarm_B50": lambda g, t: attack_a2_hub_farm(g, t, budget=50),
        "A4_HubInflation_B25": lambda g, t: attack_a4_hub_inflation(g, t, budget=25, c_top=3),
        "A4_HubInflation_B50": lambda g, t: attack_a4_hub_inflation(g, t, budget=50, c_top=3),
    }

    results = []

    for att_name, att_fn in attacks.items():
        print(f"\n--- Attacking with {att_name} ---")
        att_res = att_fn(G_clean, target_node)
        G_att = att_res.graph

        # Baseline undefended gain
        base_att_res = hits(G_att)
        base_gain = rank_gain(clean_hits_scores, base_att_res.scores, target_node)
        base_rank = compute_rank(base_att_res.scores, target_node)

        for def_name, def_fn in defenses.items():
            t0 = time.perf_counter()
            d_res = def_fn(G_att)
            t_elapsed = time.perf_counter() - t0

            c_rank = clean_records[def_name]["clean_target_rank"]
            d_rank = compute_rank(d_res.scores, target_node)
            d_gain = c_rank - d_rank
            reduction = defense_attack_success_reduction(base_gain, d_gain)

            rec = {
                "attack": att_name,
                "defense": def_name,
                "clean_rank": c_rank,
                "attacked_rank": d_rank,
                "rank_gain": d_gain,
                "attack_success_reduction": reduction,
                "clean_top20_jaccard": clean_records[def_name]["clean_top20_jaccard"],
                "clean_top20_ndcg": clean_records[def_name]["clean_top20_ndcg"],
                "false_demotion": clean_records[def_name]["false_demotion"],
                "runtime_sec": t_elapsed,
            }
            results.append(rec)
            print(f"[{def_name:24s}] Attacked Rank: {d_rank:3d} | Gain: {d_gain:3d} | Gain Reduction: {reduction*100:.1f}%")

    df = pd.DataFrame(results)
    out_csv = RESULTS_DIR / "defenses_eval.csv"
    df.to_csv(out_csv, index=False)
    elapsed = time.perf_counter() - t_start
    print(f"\n[DONE] Saved defense evaluation results to {out_csv} in {elapsed:.2f}s")


if __name__ == "__main__":
    run_defenses_experiment()
