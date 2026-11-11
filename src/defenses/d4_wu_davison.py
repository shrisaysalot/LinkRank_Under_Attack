"""Defense D4: Wu-Davison (2005) Link Farm Detection and Penalization.

- D4 (wu_davison_hits): True Wu-Davison (2005) link farm detection combining
  both in-link and out-link overlap signals.
- D4b (wu_davison_outlink_jaccard_hits): Out-link Jaccard hub overlap variant,
  computed via full sparse pairwise matrix multiplication (no arbitrary window truncation).
"""
from typing import Dict, Tuple, Optional, Union
import numpy as np
import scipy.sparse as sp
import networkx as nx

from src.rankers.hits import hits
from src.rankers.base import RankResult


def wu_davison_outlink_jaccard_hits(
    graph_or_adj: Union[nx.DiGraph, sp.spmatrix],
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
    if isinstance(graph_or_adj, (nx.DiGraph, nx.Graph)):
        n = graph_or_adj.number_of_nodes()
        if n == 0:
            return RankResult(scores=np.array([]), hub_scores=np.array([]))
        nodes = list(range(n)) if set(graph_or_adj.nodes()) == set(range(n)) else list(graph_or_adj.nodes())
        node_to_idx = {node: i for i, node in enumerate(nodes)}
        rows = [node_to_idx[u] for u, v in graph_or_adj.edges()]
        cols = [node_to_idx[v] for u, v in graph_or_adj.edges()]
        data = np.ones(len(rows), dtype=float)
        A_bin = sp.csr_matrix((data, (rows, cols)), shape=(n, n), dtype=float)
    else:
        A_bin = graph_or_adj.tocsr().astype(float)
        A_bin.data = np.ones_like(A_bin.data)
        n = A_bin.shape[0]
        coo = A_bin.tocoo()
        rows, cols = coo.row, coo.col

    # Out-degrees
    out_degrees = np.array(A_bin.sum(axis=1)).flatten()

    # Exact pairwise intersection: C[i, j] = |Out(i) & Out(j)|
    C = A_bin.dot(A_bin.T).tocoo()

    # Vectorized suspicious hub pairs where Jaccard > overlap_threshold
    mask = C.row < C.col
    r_arr = C.row[mask]
    c_arr = C.col[mask]
    inter_arr = C.data[mask]
    unions = out_degrees[r_arr] + out_degrees[c_arr] - inter_arr
    suspicious = (unions > 0) & ((inter_arr / unions) > overlap_threshold)

    penalized_hubs = set(r_arr[suspicious]).union(set(c_arr[suspicious]))

    hub_weights = np.ones(n, dtype=float)
    for idx in penalized_hubs:
        hub_weights[idx] = penalty_factor

    # Build penalized adjacency matrix
    new_data = [hub_weights[u_idx] for u_idx in rows]
    A_penalized = sp.csr_matrix((new_data, (rows, cols)), shape=(n, n), dtype=float)
    return hits(A_penalized, tol=tol, max_iter=max_iter)


def wu_davison_hits(
    graph_or_adj: Union[nx.DiGraph, sp.spmatrix],
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
    if isinstance(graph_or_adj, (nx.DiGraph, nx.Graph)):
        n = graph_or_adj.number_of_nodes()
        if n == 0:
            return RankResult(scores=np.array([]), hub_scores=np.array([]))
        nodes = list(range(n)) if set(graph_or_adj.nodes()) == set(range(n)) else list(graph_or_adj.nodes())
        node_to_idx = {node: i for i, node in enumerate(nodes)}
        rows = [node_to_idx[u] for u, v in graph_or_adj.edges()]
        cols = [node_to_idx[v] for u, v in graph_or_adj.edges()]
        data = np.ones(len(rows), dtype=float)
        A_bin = sp.csr_matrix((data, (rows, cols)), shape=(n, n), dtype=float)
    else:
        A_bin = graph_or_adj.tocsr().astype(float)
        A_bin.data = np.ones_like(A_bin.data)
        n = A_bin.shape[0]
        coo = A_bin.tocoo()
        rows, cols = coo.row, coo.col

    out_degrees = np.array(A_bin.sum(axis=1)).flatten()
    in_degrees = np.array(A_bin.sum(axis=0)).flatten()

    # Out-link co-occurrence: C_out[i, j] = |Out(i) & Out(j)|
    C_out = A_bin.dot(A_bin.T).tocoo()
    
    # In-link co-occurrence: C_in[i, j] = |In(i) & In(j)|
    C_in = (A_bin.T.dot(A_bin)).tocsr()

    mask = C_out.row < C_out.col
    r_arr = C_out.row[mask]
    c_arr = C_out.col[mask]
    inter_out = C_out.data[mask]
    unions_out = out_degrees[r_arr] + out_degrees[c_arr] - inter_out

    jacc_out = np.zeros_like(inter_out, dtype=float)
    pos_mask = unions_out > 0
    jacc_out[pos_mask] = inter_out[pos_mask] / unions_out[pos_mask]

    # Candidate pairs with high out-link overlap
    cand_idx = np.where(jacc_out > out_threshold)[0]
    penalized_nodes = set()

    for idx in cand_idx:
        jo = jacc_out[idx]
        i = r_arr[idx]
        j = c_arr[idx]
        if jo > 0.6:
            penalized_nodes.add(i)
            penalized_nodes.add(j)
        else:
            inter_in = C_in[i, j]
            union_in = in_degrees[i] + in_degrees[j] - inter_in
            jacc_in = inter_in / union_in if union_in > 0 else 0.0
            if jacc_in > in_threshold:
                penalized_nodes.add(i)
                penalized_nodes.add(j)

    weights = np.ones(n, dtype=float)
    for idx in penalized_nodes:
        weights[idx] = penalty_factor

    new_data = [weights[u_idx] for u_idx in rows]
    A_penalized = sp.csr_matrix((new_data, (rows, cols)), shape=(n, n), dtype=float)
    return hits(A_penalized, tol=tol, max_iter=max_iter)
