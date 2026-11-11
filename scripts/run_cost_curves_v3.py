"""Full-Scale Cost Curves Evaluation Script (v3).

Features:
- Graphs: BA-500, ER-500, SBM-500, web-Stanford BaseSet, web-NotreDame BaseSet
- Seeds: [42, 123, 456, 789, 999] (5 seeds)
- Targets: 6 targets per graph/seed spanning low, medium, random ranks
- Attacks: A1, A2, A3, A4 (proposal inflation), A5 (cross-score), A5b (cross-links), A6 (greedy gradient)
- Budgets: [1, 2, 5, 10, 25, 50, 100, 200]
- Rankers: HITS, PageRank, SALSA, InDegree
- Metrics: normalized_rank_gain, top10_entry, top20_entry, jaccard_at_20, ndcg_at_20,
           kendall_tau, spearman_rho, fake_share, nodes_added, edges_added, runtime
- Resume-safe CSV checkpointing per (graph, seed)
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

from src.config import RESULTS_DIR
from src.data.synthetic import (
    generate_barabasi_albert,
    generate_erdos_renyi,
    generate_planted_bipartite_sbm
)
from src.data.loader import load_snap_graph
from src.data.base_set import sample_root_set, build_base_set
from src.rankers import hits, pagerank, salsa, indegree
from src.attacks import (
    attack_a1_single_fake_hub,
    attack_a2_hub_farm,
    attack_a3_bipartite_block,
    attack_a4_hub_inflation,
    attack_a5_cross_score,
    attack_a5b_cross_score,
    attack_a6_greedy_gradient
)
from src.eval import (
    compute_rank,
    normalized_rank_gain,
    top_k_jaccard,
    ndcg_at_k,
    kendall_tau,
    spearman_rho
)


def run_cost_curves_v3():
    print("==================================================================")
    print("=== FULL-SCALE COST CURVES EVALUATION V3 ===")
    print("==================================================================")
    t_global_start = time.perf_counter()

    seeds = [42, 123, 456, 789, 999]
    budgets = [1, 2, 5, 10, 25, 50, 100, 200]

    out_csv = RESULTS_DIR / "cost_curves_v3.csv"
    existing_df = None
    completed_keys = set()
    if out_csv.exists():
        try:
            existing_df = pd.read_csv(out_csv)
            if not existing_df.empty and "graph" in existing_df.columns and "seed" in existing_df.columns:
                for _, r in existing_df[["graph", "seed"]].drop_duplicates().iterrows():
                    completed_keys.add((r["graph"], int(r["seed"])))
            print(f"Loaded existing checkpoint with {len(existing_df)} rows ({len(completed_keys)} batches completed).")
        except Exception as e:
            print(f"Could not read existing checkpoint, starting fresh: {e}")

    print("Loading SNAP full graphs...")
    G_stan_full, _, _ = load_snap_graph("web-Stanford", max_edges=60000)
    G_nd_full, _, _ = load_snap_graph("web-NotreDame", max_edges=60000)

    graphs = {
        "Synthetic_BA_500": lambda s: generate_barabasi_albert(n=500, m=4, seed=s),
        "Synthetic_ER_500": lambda s: generate_erdos_renyi(n=500, p=0.012, seed=s),
        "Synthetic_SBM_500": lambda s: generate_planted_bipartite_sbm(460, 20, 20, seed=s)[0],
        "SNAP_web-Stanford_BaseSet": lambda s: build_base_set(
            G_stan_full, sample_root_set(G_stan_full, seed_node=int(s % 300) + 1, root_size=70), max_in_links=20
        ).graph,
        "SNAP_web-NotreDame_BaseSet": lambda s: build_base_set(
            G_nd_full, sample_root_set(G_nd_full, seed_node=int(s % 300) + 1, root_size=40), max_in_links=10
        ).graph
    }

    attacks = {
        "A1_SingleHub": lambda g, t, b: attack_a1_single_fake_hub(g, t, budget=b),
        "A2_HubFarm": lambda g, t, b: attack_a2_hub_farm(g, t, budget=b),
        "A3_BipartiteBlock": lambda g, t, b: attack_a3_bipartite_block(g, t, budget=b),
        "A4_ProposalInflation": lambda g, t, b: attack_a4_hub_inflation(g, t, budget=b, c_top=3, use_one_fake_page=False),
        "A5_ProposalCrossScore": lambda g, t, b: attack_a5_cross_score(g, t, budget=b, c_top=3),
        "A5b_CrossScoreLinks": lambda g, t, b: attack_a5b_cross_score(g, t, budget=b, c_top=3),
        "A6_GreedyGradient": lambda g, t, b: attack_a6_greedy_gradient(g, t, budget=b, candidate_pool_size=1)
    }

    rankers = {
        "HITS": lambda g: hits(g, max_iter=60),
        "PageRank": lambda g: pagerank(g, alpha=0.85, max_iter=60),
        "SALSA": lambda g: salsa(g, max_iter=60),
        "InDegree": lambda g: indegree(g)
    }

    for g_name, g_fn in graphs.items():
        for s in seeds:
            batch_key = (g_name, s)
            if batch_key in completed_keys:
                print(f"Skipping completed batch: {g_name} (seed={s})")
                continue

            t_batch_start = time.perf_counter()
            print(f"\nRunning batch: {g_name} | Seed: {s}...")
            G = g_fn(s)
            n_nodes = G.number_of_nodes()

            # Clean baselines
            clean_results = {r_name: r_fn(G) for r_name, r_fn in rankers.items()}
            h_scores = clean_results["HITS"].scores

            # Pick 6 diverse targets across low, medium, random tiers
            sorted_order = np.argsort(h_scores)
            rng = np.random.RandomState(s)
            targets = [
                ("lowest_10pct", int(sorted_order[int(n_nodes * 0.10)])),
                ("low_25pct", int(sorted_order[int(n_nodes * 0.25)])),
                ("medium_50pct", int(sorted_order[int(n_nodes * 0.50)])),
                ("med_high_70pct", int(sorted_order[int(n_nodes * 0.70)])),
                ("high_85pct", int(sorted_order[int(n_nodes * 0.85)])),
                ("random_sample", int(rng.choice(sorted_order[int(n_nodes * 0.2):int(n_nodes * 0.8)])))
            ]

            batch_records = []

            for tier, target_node in targets:
                clean_ranks = {r_name: compute_rank(clean_results[r_name].scores, target_node) for r_name in rankers}

                for att_name, att_fn in attacks.items():
                    for B in budgets:
                        t_att_start = time.perf_counter()
                        att_res = att_fn(G, target_node, B)
                        G_att = att_res.graph
                        n_added = att_res.cost_nodes
                        e_added = att_res.cost_edges
                        total_nodes = G_att.number_of_nodes()
                        fake_share = (n_added / total_nodes) if total_nodes > 0 else 0.0

                        for r_name, r_fn in rankers.items():
                            t_r_start = time.perf_counter()
                            res_att = r_fn(G_att)
                            runtime_r = time.perf_counter() - t_r_start

                            c_scores = clean_results[r_name].scores
                            a_scores = res_att.scores
                            c_rank = clean_ranks[r_name]
                            a_rank = compute_rank(a_scores, target_node)

                            g_raw = c_rank - a_rank
                            g_norm = normalized_rank_gain(c_scores, a_scores, target_node)
                            t10 = int(a_rank <= 10)
                            t20 = int(a_rank <= 20)
                            jacc = top_k_jaccard(c_scores, a_scores, k=20)
                            ndcg = ndcg_at_k(c_scores, a_scores, k=20)
                            tau = kendall_tau(c_scores, a_scores)
                            rho = spearman_rho(c_scores, a_scores)

                            batch_records.append({
                                "graph": g_name,
                                "seed": s,
                                "target_tier": tier,
                                "target_node": target_node,
                                "attack": att_name,
                                "budget": B,
                                "nodes_added": n_added,
                                "edges_added": e_added,
                                "fake_share": fake_share,
                                "ranker": r_name,
                                "clean_rank": c_rank,
                                "attacked_rank": a_rank,
                                "rank_gain": g_raw,
                                "normalized_rank_gain": g_norm,
                                "top10_entry": t10,
                                "top20_entry": t20,
                                "jaccard_at_20": jacc,
                                "ndcg_at_20": ndcg,
                                "kendall_tau": tau,
                                "spearman_rho": rho,
                                "runtime_s": runtime_r
                            })

            # Checkpoint batch to CSV
            batch_df = pd.DataFrame(batch_records)
            if not out_csv.exists() or completed_keys == set():
                batch_df.to_csv(out_csv, index=False)
            else:
                batch_df.to_csv(out_csv, mode="a", header=False, index=False)
            completed_keys.add(batch_key)
            elapsed_batch = time.perf_counter() - t_batch_start
            print(f"Batch {batch_key} completed: {len(batch_df)} rows appended in {elapsed_batch:.1f}s")

    t_global_total = time.perf_counter() - t_global_start
    final_df = pd.read_csv(out_csv)
    print(f"\n[DONE Cost Curves v3] Successfully recorded {len(final_df)} rows in {out_csv} in {t_global_total:.1f}s")
    return final_df


if __name__ == "__main__":
    run_cost_curves_v3()

