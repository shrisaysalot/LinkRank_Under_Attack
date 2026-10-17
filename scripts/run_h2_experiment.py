"""Hypothesis H2 experiment: Hub farm takeover threshold p ~ sigma_1^2 in HITS vs smooth PageRank."""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import time
import numpy as np
import pandas as pd
import networkx as nx
import scipy.sparse as sp

from src.config import RESULTS_DIR, DEFAULT_SEED
from src.data.synthetic import generate_barabasi_albert, generate_erdos_renyi
from src.rankers import hits, pagerank, salsa, indegree
from src.attacks.a2_hub_farm import attack_a2_hub_farm
from src.eval.metrics import compute_rank


def run_h2_experiment():
    print("=== Running Hypothesis H2: Spectral Takeover Experiment ===")
    t_start = time.perf_counter()

    # Create synthetic test graph
    n = 300
    G = generate_barabasi_albert(n=n, m=3, seed=DEFAULT_SEED)
    nodes = list(range(n))
    A_clean = nx.adjacency_matrix(G, nodelist=nodes, dtype=float).tocsr()

    # Compute clean singular values to find sigma_1^2
    u, s, vt = sp.linalg.svds(A_clean, k=2)
    s = np.sort(s)[::-1]
    sigma1 = float(s[0])
    sigma1_sq = sigma1 ** 2
    print(f"Clean graph: {n} nodes, {G.number_of_edges()} edges")
    print(f"Dominant singular value sigma_1 = {sigma1:.4f} | sigma_1^2 = {sigma1_sq:.2f}")

    # Pick a low-to-medium rank target node (e.g., in-degree 2 or 3)
    in_degrees = np.array(A_clean.sum(axis=0)).flatten()
    clean_hits = hits(G)
    order = np.argsort(clean_hits.scores)
    # Pick a node with low clean authority
    target_node = int(order[int(n * 0.2)])
    clean_target_rank = compute_rank(clean_hits.scores, target_node)
    clean_target_score = clean_hits.scores[target_node]
    print(f"Target node: {target_node} | Clean HITS rank: {clean_target_rank}/{n} | Score: {clean_target_score:.6f}")

    # Grid of farm size p spanning below, at, and above sigma_1^2
    p_max = int(np.ceil(sigma1_sq * 1.8))
    # Fine grid around sigma_1^2
    p_values = sorted(list(set(
        list(range(1, min(15, p_max), 2)) +
        list(range(max(1, int(sigma1_sq * 0.5)), min(p_max, int(sigma1_sq * 1.5)), 1)) +
        list(range(int(sigma1_sq * 1.5), p_max + 1, 3))
    )))

    print(f"Testing farm sizes p across {len(p_values)} points: min={min(p_values)}, max={max(p_values)}")

    records = []
    for p in p_values:
        # Attacked graph with p fake hubs -> target
        att_res = attack_a2_hub_farm(G, target_node=target_node, budget=p)
        G_att = att_res.graph

        # 1. HITS
        h_res = hits(G_att, max_iter=200, compute_eigengap=True)
        h_rank = compute_rank(h_res.scores, target_node)
        h_score = float(h_res.scores[target_node])

        # 2. PageRank
        pr_res = pagerank(G_att, alpha=0.85, max_iter=200)
        pr_rank = compute_rank(pr_res.scores, target_node)
        pr_score = float(pr_res.scores[target_node])

        # 3. SALSA
        salsa_res = salsa(G_att, max_iter=200)
        salsa_rank = compute_rank(salsa_res.scores, target_node)
        salsa_score = float(salsa_res.scores[target_node])

        # 4. In-degree
        deg_res = indegree(G_att)
        deg_rank = compute_rank(deg_res.scores, target_node)
        deg_score = float(deg_res.scores[target_node])

        rec = {
            "p_farm_size": p,
            "sigma1_sq": sigma1_sq,
            "ratio_p_to_sigma1_sq": float(p / sigma1_sq),
            "hits_score": h_score,
            "hits_rank": h_rank,
            "pagerank_score": pr_score,
            "pagerank_rank": pr_rank,
            "salsa_score": salsa_score,
            "salsa_rank": salsa_rank,
            "indegree_score": deg_score,
            "indegree_rank": deg_rank,
            "hits_is_top1": int(h_rank == 1),
            "pagerank_is_top1": int(pr_rank == 1),
            "salsa_is_top1": int(salsa_rank == 1),
        }
        records.append(rec)

        if p in [1, int(sigma1_sq * 0.5), int(sigma1_sq), int(sigma1_sq * 1.5)]:
            print(f"p={p:3d} (p/sigma^2={p/sigma1_sq:.2f}) | HITS Rank: {h_rank:3d} (score={h_score:.4f}) | PR Rank: {pr_rank:3d} (score={pr_score:.4f})")

    df = pd.DataFrame(records)
    out_csv = RESULTS_DIR / "h2_experiment.csv"
    df.to_csv(out_csv, index=False)
    elapsed = time.perf_counter() - t_start
    print(f"\n[DONE] Saved H2 experiment results to {out_csv} in {elapsed:.2f}s")


if __name__ == "__main__":
    run_h2_experiment()
