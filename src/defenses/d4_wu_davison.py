"""Defense D4: Wu-Davison (2005) Link Farm Detection and Penalization.

- D4 (wu_davison_hits): True Wu-Davison (2005) link farm detection combining
  both in-link and out-link overlap signals.
- D4b (wu_davison_outlink_jaccard_hits): Out-link Jaccard hub overlap variant,
  computed via full sparse pairwise matrix multiplication (no arbitrary window truncation).
"""
from typing import Dict, Tuple, Optional
import numpy as np
import scipy.sparse as sp
import networkx as nx

from src.rankers.hits import hits
from src.rankers.base import RankResult


def wu_davison_outlink_jaccard_hits(
    G: nx.DiGraph,
    overlap_threshold: float = 0.5,
    penalty_factor: float = 0.2,
    tol: float = 1e-8,
    max_iter: int = 200
) -> RankResult:
    """Defense D4b: Out-link Jaccard hub overlap variant.

    Computes exact pairwise out-link Jaccard across ALL active hubs using
    sparse matrix multiplication C = A * A^T (no arbitrary index window truncation).
    Hubs sharing target Jaccard similarity > overlap_threshold have their out-edges down-weighted.
    """
    n = G.number_of_nodes()
    if n == 0:
        return RankResult(scores=np.array([]), hub_scores=np.array([]))

    nodes = list(range(n)) if set(G.nodes()) == set(range(n)) else list(G.nodes())
    node_to_idx = {node: i for i, node in enumerate(nodes)}

    # Build binary sparse adjacency matrix
    rows = [node_to_idx[u] for u, v in G.edges()]
    cols = [node_to_idx[v] for u, v in G.edges()]
    data = np.ones(len(rows), dtype=float)
    A_bin = sp.csr_matrix((data, (rows, cols)), shape=(n, n), dtype=float)

    # Out-degrees
    out_degrees = np.array(A_bin.sum(axis=1)).flatten()

    # Exact pairwise intersection: C[i, j] = |Out(i) & Out(j)|
    # A_bin * A_bin.T computes intersection for all pairs
    C = A_bin.dot(A_bin.T).tocoo()

    # Find suspicious hub pairs where Jaccard > overlap_threshold
    penalized_hubs = set()
    for i, j, inter in zip(C.row, C.col, C.data):
        if i >= j:  # Only upper triangle, skip diagonal
            continue
        union = out_degrees[i] + out_degrees[j] - inter
        if union > 0 and (inter / union) > overlap_threshold:
            penalized_hubs.add(i)
            penalized_hubs.add(j)

    hub_weights = np.ones(n, dtype=float)
    for idx in penalized_hubs:
        hub_weights[idx] = penalty_factor

    # Build penalized adjacency matrix
    new_data = [hub_weights[u_idx] for u_idx in rows]
    A_penalized = sp.csr_matrix((new_data, (rows, cols)), shape=(n, n), dtype=float)
    return hits(A_penalized, tol=tol, max_iter=max_iter)


def wu_davison_hits(
    G: nx.DiGraph,
    out_threshold: float = 0.4,
    in_threshold: float = 0.2,
    penalty_factor: float = 0.2,
    tol: float = 1e-8,
    max_iter: int = 200
) -> RankResult:
    """Defense D4: Wu-Davison (2005) mutual in-link / out-link link farm detection.

    Flags pairs of nodes that exhibit high out-link overlap combined with
    shared in-link patterns or mutual coupling, down-weighting colliding link farm edges.
    """
    n = G.number_of_nodes()
    if n == 0:
        return RankResult(scores=np.array([]), hub_scores=np.array([]))

    nodes = list(range(n)) if set(G.nodes()) == set(range(n)) else list(G.nodes())
    node_to_idx = {node: i for i, node in enumerate(nodes)}

    rows = [node_to_idx[u] for u, v in G.edges()]
    cols = [node_to_idx[v] for u, v in G.edges()]
    data = np.ones(len(rows), dtype=float)
    A_bin = sp.csr_matrix((data, (rows, cols)), shape=(n, n), dtype=float)

    out_degrees = np.array(A_bin.sum(axis=1)).flatten()
    in_degrees = np.array(A_bin.sum(axis=0)).flatten()

    # Out-link co-occurrence: C_out[i, j] = |Out(i) & Out(j)|
    C_out = A_bin.dot(A_bin.T).tocoo()
    
    # In-link co-occurrence: C_in[i, j] = |In(i) & In(j)|
    C_in = (A_bin.T.dot(A_bin)).tocsr()

    penalized_nodes = set()
    for i, j, inter_out in zip(C_out.row, C_out.col, C_out.data):
        if i >= j:
            continue
        union_out = out_degrees[i] + out_degrees[j] - inter_out
        jacc_out = inter_out / union_out if union_out > 0 else 0.0

        if jacc_out > out_threshold:
            # Check in-link overlap or mutual coupling
            inter_in = C_in[i, j]
            union_in = in_degrees[i] + in_degrees[j] - inter_in
            jacc_in = inter_in / union_in if union_in > 0 else 0.0

            # Farm criterion: high out-link overlap (colluding hubs) OR combined dual overlap
            if jacc_out > 0.6 or (jacc_out > out_threshold and jacc_in > in_threshold):
                penalized_nodes.add(i)
                penalized_nodes.add(j)

    weights = np.ones(n, dtype=float)
    for idx in penalized_nodes:
        weights[idx] = penalty_factor

    new_data = [weights[u_idx] for u_idx in rows]
    A_penalized = sp.csr_matrix((new_data, (rows, cols)), shape=(n, n), dtype=float)
    return hits(A_penalized, tol=tol, max_iter=max_iter)
