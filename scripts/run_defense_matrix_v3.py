"""Defense Evaluation Matrix Script (v3).

Evaluates the full Defense x Attack matrix with calibrated thresholds:
- Defenses:
  - Undefended HITS
  - D1: Randomized HITS (eps=0.15)
  - D1-sub: Subspace HITS (top k singular vectors)
  - D2: Bharat-Henzinger domain weighting
  - D3: Hub Capping (cap=0.01 / 1%)
  - D4: Wu-Davison Mutual (threshold=0.5)
  - D4b: Wu-Davison Out-Link Jaccard (threshold=0.5)
  - D5: Trust-Based HITS (PageRank clean seeds, k=20)
  - D5-indeg: Trust-Based HITS (In-Degree proxy seeds, k=20)
  - Combined D4 + D1
  - Combined D4 + D5
- Attacks:
  - A2: Hub Farm
  - A3: Bipartite Block
  - A4: Proposal Hub Inflation
  - A5: Proposal Cross-Score
  - A6: Greedy Gradient
  - Camouflaged Farm (r=2, r=5, r=10)
- Graphs: BA-500, ER-500, SBM-500
- Budgets: 25, 100
- Targets: 5 per graph/seed, 3 seeds [42, 123, 456]
- Metrics: attack reduction (only positive undefended cells), clean NDCG@20 loss, clean Jaccard@20, runtime, n
- Goal check: reduction >= 50% AND clean NDCG loss <= 5%
"""
import sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import time
import numpy as np
import pandas as pd
import scipy.sparse as sp
import networkx as nx

from src.config import RESULTS_DIR
from src.data.synthetic import (
    generate_barabasi_albert,
    generate_erdos_renyi,
    generate_planted_bipartite_sbm
)
from src.rankers import hits, pagerank, indegree
from src.rankers.randomized_hits import randomized_hits
from src.rankers.subspace_hits import subspace_hits
from src.defenses.d2_bharat_henzinger import bharat_henzinger_hits
from src.defenses.d3_hub_capping import hub_capped_hits
from src.defenses.d4_wu_davison import wu_davison_hits, wu_davison_outlink_jaccard_hits
from src.defenses.d5_trust_hits import trust_based_hits
from src.attacks import (
    attack_a2_hub_farm,
    attack_a3_bipartite_block,
    attack_a4_hub_inflation,
    attack_a5_cross_score,
    attack_a6_greedy_gradient
)
from src.eval import compute_rank, ndcg_at_k, top_k_jaccard


def attack_camouflaged_farm(G: nx.DiGraph, target_node: int, budget: int = 25, r_camouflage: int = 5):
    from src.attacks.base import AttackResult
    G_att = G.copy()
    max_node = max(G.nodes()) if len(G) > 0 else -1
    all_real_nodes = [n for n in G.nodes() if n != target_node]

    cost_per_hub = 1 + r_camouflage
    num_hubs = max(1, budget // cost_per_hub)
    added_nodes = []
    added_edges = []

    rng = np.random.RandomState(42)
    edge_count = 0

    for i in range(1, num_hubs + 1):
        if edge_count >= budget:
            break
        fake_hub = max_node + i
        G_att.add_node(fake_hub)
        added_nodes.append(fake_hub)

        G_att.add_edge(fake_hub, target_node)
        added_edges.append((fake_hub, target_node))
        edge_count += 1

        if all_real_nodes and r_camouflage > 0:
            camo_targets = rng.choice(all_real_nodes, size=min(r_camouflage, len(all_real_nodes)), replace=False)
            for ct in camo_targets:
                if edge_count < budget:
                    G_att.add_edge(fake_hub, ct)
                    added_edges.append((fake_hub, ct))
                    edge_count += 1

    adj = nx.adjacency_matrix(G_att, nodelist=range(G_att.number_of_nodes()), dtype=float).tocsr()
    return AttackResult(
        graph=G_att,
        adj_matrix=adj,
        target_node=target_node,
        added_nodes=added_nodes,
        added_edges=added_edges,
        cost_nodes=len(added_nodes),
        cost_edges=len(added_edges)
    )


def combined_d4_d1_hits(graph_or_adj, overlap_threshold=0.5, eps=0.15):
    """Combined defense D4 (Wu-Davison) + D1 (Randomized HITS reset)."""
    # First apply D4 link farm penalization
    if isinstance(graph_or_adj, (nx.DiGraph, nx.Graph)):
        G = graph_or_adj
        n = G.number_of_nodes()
        nodes = list(range(n))
        A_bin = nx.adjacency_matrix(G, nodelist=nodes, dtype=float).tocsr()
    else:
        A_bin = graph_or_adj.tocsr().astype(float)
        n = A_bin.shape[0]

    out_degrees = np.array(A_bin.sum(axis=1)).flatten()
    C = A_bin.dot(A_bin.T).tocoo()
    mask = C.row < C.col
    r_arr, c_arr, inter_arr = C.row[mask], C.col[mask], C.data[mask]
    unions = out_degrees[r_arr] + out_degrees[c_arr] - inter_arr
    suspicious = (unions > 0) & ((inter_arr / unions) > overlap_threshold)
    penalized_hubs = set(r_arr[suspicious]).union(set(c_arr[suspicious]))

    coo = A_bin.tocoo()
    weights = np.ones(n, dtype=float)
    for idx in penalized_hubs:
        weights[idx] = 0.2
    new_data = [weights[u] for u in coo.row]
    A_pen = sp.csr_matrix((new_data, (coo.row, coo.col)), shape=(n, n), dtype=float)

    # Then run Randomized HITS on penalized graph
    return randomized_hits(A_pen, eps=eps)


def combined_d4_d5_hits(graph_or_adj, trusted_seeds, overlap_threshold=0.5, eps=0.15):
    """Combined defense D4 (Wu-Davison) + D5 (Trust-Based HITS reset)."""
    if isinstance(graph_or_adj, (nx.DiGraph, nx.Graph)):
        G = graph_or_adj
        n = G.number_of_nodes()
        nodes = list(range(n))
        A_bin = nx.adjacency_matrix(G, nodelist=nodes, dtype=float).tocsr()
    else:
        A_bin = graph_or_adj.tocsr().astype(float)
        n = A_bin.shape[0]

    out_degrees = np.array(A_bin.sum(axis=1)).flatten()
    C = A_bin.dot(A_bin.T).tocoo()
    mask = C.row < C.col
    r_arr, c_arr, inter_arr = C.row[mask], C.col[mask], C.data[mask]
    unions = out_degrees[r_arr] + out_degrees[c_arr] - inter_arr
    suspicious = (unions > 0) & ((inter_arr / unions) > overlap_threshold)
    penalized_hubs = set(r_arr[suspicious]).union(set(c_arr[suspicious]))

    coo = A_bin.tocoo()
    weights = np.ones(n, dtype=float)
    for idx in penalized_hubs:
        weights[idx] = 0.2
    new_data = [weights[u] for u in coo.row]
    A_pen = sp.csr_matrix((new_data, (coo.row, coo.col)), shape=(n, n), dtype=float)

    return trust_based_hits(A_pen, trusted_seeds=trusted_seeds, eps=eps)


def run_defense_matrix_v3():
    print("==================================================================")
    print("=== DEFENSE EVALUATION MATRIX V3 ===")
    print("==================================================================")
    t_start = time.perf_counter()

    seeds = [42, 123, 456]
    budgets = [25, 100]

    graphs = {
        "Synthetic_BA_500": lambda s: generate_barabasi_albert(n=500, m=4, seed=s),
        "Synthetic_ER_500": lambda s: generate_erdos_renyi(n=500, p=0.012, seed=s),
        "Synthetic_SBM_500": lambda s: generate_planted_bipartite_sbm(460, 20, 20, seed=s)[0]
    }

    attacks = {
        "A2_HubFarm": lambda g, t, b: attack_a2_hub_farm(g, t, budget=b),
        "A3_BipartiteBlock": lambda g, t, b: attack_a3_bipartite_block(g, t, budget=b),
        "A4_ProposalInflation": lambda g, t, b: attack_a4_hub_inflation(g, t, budget=b, c_top=3, use_one_fake_page=False),
        "A5_ProposalCrossScore": lambda g, t, b: attack_a5_cross_score(g, t, budget=b, c_top=3),
        "A6_GreedyGradient": lambda g, t, b: attack_a6_greedy_gradient(g, t, budget=b, candidate_pool_size=1),
        "Camouflaged_Farm_r2": lambda g, t, b: attack_camouflaged_farm(g, t, budget=b, r_camouflage=2),
        "Camouflaged_Farm_r5": lambda g, t, b: attack_camouflaged_farm(g, t, budget=b, r_camouflage=5),
        "Camouflaged_Farm_r10": lambda g, t, b: attack_camouflaged_farm(g, t, budget=b, r_camouflage=10)
    }

    records = []

    for g_name, g_fn in graphs.items():
        for s in seeds:
            print(f"Processing defense matrix for {g_name} | Seed {s}...")
            G = g_fn(s)
            n_nodes = G.number_of_nodes()

            clean_h = hits(G, max_iter=60).scores
            clean_pr = pagerank(G, max_iter=60).scores
            clean_deg = indegree(G).scores

            # Precompute high-quality trusted seeds: top-20 PageRank on clean graph
            pr_seeds = list(np.argsort(-clean_pr)[:20])
            deg_seeds = list(np.argsort(-clean_deg)[:20])

            defenses = {
                "Undefended_HITS": lambda g: hits(g, max_iter=60),
                "D1_RandomizedHITS_0.15": lambda g: randomized_hits(g, eps=0.15, max_iter=60),
                "D1_SubspaceHITS": lambda g: subspace_hits(g, k=5),
                "D2_BharatHenzinger": lambda g: bharat_henzinger_hits(g, max_iter=60),
                "D3_HubCapping_0.01": lambda g: hub_capped_hits(g, cap_fraction=0.01, max_iter=60),
                "D4_WuDavison_Mutual_0.5": lambda g: wu_davison_hits(g, out_threshold=0.5, max_iter=60),
                "D4b_WuDavison_OutJaccard_0.5": lambda g: wu_davison_outlink_jaccard_hits(g, overlap_threshold=0.5, max_iter=60),
                "D5_TrustHITS_PageRankSeeds": lambda g: trust_based_hits(g, trusted_seeds=pr_seeds, eps=0.15, max_iter=60),
                "D5_TrustHITS_InDegreeSeeds": lambda g: trust_based_hits(g, trusted_seeds=deg_seeds, eps=0.15, max_iter=60),
                "Combined_D4_plus_D1": lambda g: combined_d4_d1_hits(g, overlap_threshold=0.5, eps=0.15),
                "Combined_D4_plus_D5": lambda g: combined_d4_d5_hits(g, trusted_seeds=pr_seeds, overlap_threshold=0.5, eps=0.15)
            }

            # Precompute clean defense baselines
            clean_def_scores = {}
            clean_ndcg_losses = {}
            clean_jaccards = {}
            for d_name, d_fn in defenses.items():
                res_clean_d = d_fn(G)
                d_scores = res_clean_d.scores
                clean_def_scores[d_name] = d_scores
                loss = 1.0 - ndcg_at_k(clean_h, d_scores, k=20)
                jacc = top_k_jaccard(clean_h, d_scores, k=20)
                clean_ndcg_losses[d_name] = loss
                clean_jaccards[d_name] = jacc

            # 5 diverse targets
            sorted_order = np.argsort(clean_h)
            targets = [int(sorted_order[int(n_nodes * f)]) for f in [0.20, 0.35, 0.50, 0.65, 0.80]]

            for target in targets:
                clean_h_rank = compute_rank(clean_h, target)

                for att_name, att_fn in attacks.items():
                    for B in budgets:
                        att_res = att_fn(G, target, B)
                        G_att = att_res.graph

                        # First compute undefended rank to establish base gain
                        undef_res = hits(G_att, max_iter=60)
                        undef_rank = compute_rank(undef_res.scores, target)
                        base_gain = clean_h_rank - undef_rank

                        for d_name, d_fn in defenses.items():
                            t_def_start = time.perf_counter()
                            res_def = d_fn(G_att)
                            runtime_d = time.perf_counter() - t_def_start

                            def_rank = compute_rank(res_def.scores, target)
                            def_gain = clean_h_rank - def_rank

                            # True attack reduction only defined when base_gain > 0
                            if base_gain > 0:
                                reduction = 1.0 - (max(0, def_gain) / base_gain)
                            else:
                                reduction = 0.0

                            meets_goal = bool(reduction >= 0.50 and clean_ndcg_losses[d_name] <= 0.05)

                            records.append({
                                "graph": g_name,
                                "seed": s,
                                "target_node": target,
                                "attack": att_name,
                                "budget": B,
                                "defense": d_name,
                                "clean_rank": clean_h_rank,
                                "undefended_rank": undef_rank,
                                "defended_rank": def_rank,
                                "base_gain": base_gain,
                                "defended_gain": def_gain,
                                "attack_reduction": reduction,
                                "clean_ndcg_loss": clean_ndcg_losses[d_name],
                                "clean_jaccard_20": clean_jaccards[d_name],
                                "meets_goal": meets_goal,
                                "runtime_s": runtime_d
                            })

    df = pd.DataFrame(records)
    out_csv = RESULTS_DIR / "defenses_eval_v3.csv"
    df.to_csv(out_csv, index=False)
    elapsed = time.perf_counter() - t_start
    print(f"\n[DONE Defense Matrix v3] Saved {len(df)} rows to {out_csv} in {elapsed:.1f}s")
    return df


if __name__ == "__main__":
    run_defense_matrix_v3()
