"""Cost curves experiment: measures rank gain, score amplification, and top-k entry vs attacker budget."""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import time
import numpy as np
import pandas as pd
import networkx as nx

from src.config import RESULTS_DIR, EXPERIMENT_SEEDS
from src.data.synthetic import generate_barabasi_albert, generate_erdos_renyi
from src.data.loader import load_snap_graph
from src.data.base_set import sample_root_set, build_base_set
from src.rankers import hits, pagerank, salsa, indegree
from src.attacks import (
    attack_a1_single_fake_hub,
    attack_a2_hub_farm,
    attack_a3_bipartite_block,
    attack_a4_hub_inflation,
    attack_a6_greedy_gradient,
)
from src.eval.metrics import (
    compute_rank,
    rank_gain,
    score_amplification,
    top_k_jaccard,
    ndcg_at_k,
    kendall_tau,
)


def select_target_nodes(clean_scores: np.ndarray, rng: np.random.RandomState) -> dict:
    """Picks low, medium, and random rank targets."""
    n = len(clean_scores)
    order = np.argsort(-clean_scores)  # sorted by score desc

    med_idx = order[n // 2]
    low_idx = order[int(n * 0.85)]
    rand_idx = rng.choice(order[int(n * 0.3):int(n * 0.9)])

    return {
        "medium_rank": int(med_idx),
        "low_rank": int(low_idx),
        "random_rank": int(rand_idx),
    }


def run_experiment():
    print("=== Running Attack Cost Curves Experiment ===")
    t_start = time.perf_counter()

    # Graphs to evaluate: Synthetic BA and SNAP wiki-Vote
    graphs_to_run = []

    print("Generating Synthetic BA-500 graph...")
    G_ba = generate_barabasi_albert(n=500, m=4, seed=42)
    graphs_to_run.append(("Synthetic_BA_500", G_ba))

    print("Loading SNAP wiki-Vote base set...")
    G_wiki_full, _, _ = load_snap_graph("wiki-Vote")
    root_wiki = sample_root_set(G_wiki_full, seed_node=30, root_size=100)
    base_wiki = build_base_set(G_wiki_full, root_wiki, max_in_links=30)
    graphs_to_run.append(("SNAP_wiki-Vote_BaseSet", base_wiki.graph))

    # Budgets
    budgets = [1, 5, 10, 25, 50, 100, 200]
    seeds = [42, 123, 456]  # 3 distinct random seeds for statistically solid runs

    attacks = {
        "A2_HubFarm": attack_a2_hub_farm,
        "A3_BipartiteBlock": attack_a3_bipartite_block,
        "A4_HubInflation": attack_a4_hub_inflation,
    }

    rankers = {
        "HITS": lambda g: hits(g, max_iter=100),
        "PageRank": lambda g: pagerank(g, alpha=0.85, max_iter=100),
        "SALSA": lambda g: salsa(g, max_iter=100),
        "InDegree": lambda g: indegree(g),
    }

    records = []

    for g_name, G in graphs_to_run:
        print(f"\n--- Graph: {g_name} ({G.number_of_nodes()} nodes, {G.number_of_edges()} edges) ---")

        # Clean baseline for each ranker
        clean_results = {r_name: r_fn(G) for r_name, r_fn in rankers.items()}

        for seed in seeds:
            rng = np.random.RandomState(seed)
            target_dict = select_target_nodes(clean_results["HITS"].scores, rng)

            for target_tier, target_node in target_dict.items():
                clean_ranks = {
                    r_name: compute_rank(clean_results[r_name].scores, target_node)
                    for r_name in rankers
                }

                for att_name, att_fn in attacks.items():
                    for B in budgets:
                        # Perform attack
                        att_res = att_fn(G, target_node=target_node, budget=B)
                        G_attacked = att_res.graph

                        # Evaluate all rankers on attacked graph
                        for r_name, r_fn in rankers.items():
                            t_r0 = time.perf_counter()
                            res_att = r_fn(G_attacked)
                            t_r = time.perf_counter() - t_r0

                            r_clean_scores = clean_results[r_name].scores
                            r_att_scores = res_att.scores

                            gain = rank_gain(r_clean_scores, r_att_scores, target_node)
                            att_rank = compute_rank(r_att_scores, target_node)
                            amp = score_amplification(r_clean_scores, r_att_scores, target_node)
                            jacc = top_k_jaccard(r_clean_scores, r_att_scores, k=20)
                            ndcg = ndcg_at_k(r_clean_scores, r_att_scores, k=20)
                            tau = kendall_tau(r_clean_scores, r_att_scores)

                            rec = {
                                "graph": g_name,
                                "seed": seed,
                                "target_tier": target_tier,
                                "target_node": target_node,
                                "attack": att_name,
                                "budget": B,
                                "ranker": r_name,
                                "clean_rank": clean_ranks[r_name],
                                "attacked_rank": att_rank,
                                "rank_gain": gain,
                                "score_amplification": amp,
                                "top10_entry": int(att_rank <= 10),
                                "top20_entry": int(att_rank <= 20),
                                "jaccard_at_20": jacc,
                                "ndcg_at_20": ndcg,
                                "kendall_tau": tau,
                                "runtime_sec": t_r,
                            }
                            records.append(rec)

        print(f"Graph {g_name} complete: {len(records)} experimental points logged.")

    df = pd.DataFrame(records)
    out_csv = RESULTS_DIR / "cost_curves.csv"
    df.to_csv(out_csv, index=False)
    elapsed = time.perf_counter() - t_start
    print(f"\n[DONE] Saved {len(df)} cost curve results to {out_csv} in {elapsed:.1f}s")


if __name__ == "__main__":
    run_experiment()
