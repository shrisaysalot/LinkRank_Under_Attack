"""Clean baselines evaluation across synthetic and real SNAP graphs."""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import time
import tracemalloc
import numpy as np
import pandas as pd
import networkx as nx

from src.config import RESULTS_DIR, DEFAULT_SEED
from src.data.synthetic import (
    generate_barabasi_albert,
    generate_erdos_renyi,
    generate_planted_bipartite_sbm,
)
from src.data.loader import load_snap_graph
from src.data.base_set import sample_root_set, build_base_set
from src.rankers import (
    hits,
    pagerank,
    salsa,
    indegree,
    randomized_hits,
    subspace_hits,
)


def evaluate_graph_clean(graph_name: str, G: nx.DiGraph) -> list:
    """Runs all rankers on clean graph, measuring time, memory, iterations, and eigengap."""
    n_nodes = G.number_of_nodes()
    n_edges = G.number_of_edges()
    print(f"\n--- Evaluating Clean Graph: {graph_name} ({n_nodes} nodes, {n_edges} edges) ---")

    rankers = {
        "HITS": lambda g: hits(g, compute_eigengap=True),
        "PageRank": lambda g: pagerank(g, alpha=0.85),
        "SALSA": lambda g: salsa(g),
        "InDegree": lambda g: indegree(g),
        "RandomizedHITS": lambda g: randomized_hits(g, eps=0.15, compute_eigengap=True),
        "SubspaceHITS": lambda g: subspace_hits(g, k=5),
    }

    records = []

    for r_name, r_fn in rankers.items():
        tracemalloc.start()
        t0 = time.perf_counter()

        res = r_fn(G)

        t_elapsed = time.perf_counter() - t0
        _, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        peak_mb = peak_mem / (1024 * 1024)

        rec = {
            "graph": graph_name,
            "num_nodes": n_nodes,
            "num_edges": n_edges,
            "ranker": r_name,
            "iterations": res.iterations,
            "converged": res.converged,
            "eigengap": res.eigengap if res.eigengap is not None else np.nan,
            "elapsed_sec": t_elapsed,
            "peak_mem_mb": peak_mb,
            "top1_node": int(res.top_k_indices(1)[0]) if len(res.scores) > 0 else -1,
            "top1_score": float(np.max(res.scores)) if len(res.scores) > 0 else 0.0,
        }
        records.append(rec)
        print(f"[{r_name:15s}] Iter: {res.iterations:3d} | Conv: {str(res.converged):5s} | Gap: {rec['eigengap']:.4f} | Time: {t_elapsed:.4f}s | Mem: {peak_mb:.2f}MB")

    return records


def main():
    print("=== Running Clean Baselines Evaluation ===")
    all_records = []

    # 1. Synthetic BA
    G_ba = generate_barabasi_albert(n=1000, m=4, seed=DEFAULT_SEED)
    all_records.extend(evaluate_graph_clean("Synthetic_BA_1000", G_ba))

    # 2. Synthetic ER
    G_er = generate_erdos_renyi(n=1000, p=0.005, seed=DEFAULT_SEED)
    all_records.extend(evaluate_graph_clean("Synthetic_ER_1000", G_er))

    # 3. Synthetic SBM with planted dense bipartite community
    G_sbm, _, _ = generate_planted_bipartite_sbm(
        n_background=800, n_planted_hubs=20, n_planted_authorities=20, seed=DEFAULT_SEED
    )
    all_records.extend(evaluate_graph_clean("Synthetic_Planted_SBM", G_sbm))

    # 4. Real SNAP: wiki-Vote
    G_wiki, _, _ = load_snap_graph("wiki-Vote")
    all_records.extend(evaluate_graph_clean("SNAP_wiki-Vote", G_wiki))

    # 5. Real SNAP: web-Stanford Base Set
    print("\nBuilding web-Stanford base set from query root...")
    G_stan_full, _, _ = load_snap_graph("web-Stanford", max_edges=100000)
    root = sample_root_set(G_stan_full, seed_node=1, root_size=150)
    base_set = build_base_set(G_stan_full, root, max_in_links=50)
    all_records.extend(evaluate_graph_clean("SNAP_web-Stanford_BaseSet", base_set.graph))

    df = pd.DataFrame(all_records)
    out_csv = RESULTS_DIR / "clean_baselines.csv"
    df.to_csv(out_csv, index=False)
    print(f"\n[DONE] Saved clean baselines to {out_csv}")


if __name__ == "__main__":
    main()
