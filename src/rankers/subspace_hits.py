"""Subspace HITS (Ng, Zheng, Jordan 2001) using top-k singular subspace."""
import time
from typing import Union
import numpy as np
import scipy.sparse as sp
import networkx as nx

from src.rankers.base import RankResult
from src.config import SUBSPACE_HITS_K


def subspace_hits(
    graph_or_adj: Union[nx.DiGraph, sp.spmatrix],
    k: int = SUBSPACE_HITS_K,
    weighted_by_singular_values: bool = False
) -> RankResult:
    """Computes Subspace HITS authority and hub scores across top-k singular vectors.

    Parameters
    ----------
    graph_or_adj : nx.DiGraph or sp.spmatrix
        Input directed graph or sparse adjacency matrix.
    k : int
        Subspace dimension (number of singular vectors).
    weighted_by_singular_values : bool
        If True, weights subspace components by sigma_i^2; if False, uses unweighted subspace energy.

    Returns
    -------
    RankResult
        Contains authority scores in .scores, hub scores in .hub_scores,
        and elapsed time.
    """
    start_time = time.perf_counter()

    if isinstance(graph_or_adj, (nx.DiGraph, nx.Graph)):
        n = graph_or_adj.number_of_nodes()
        if n == 0:
            return RankResult(scores=np.array([]), hub_scores=np.array([]), iterations=1, converged=True)
        nodes = list(range(n)) if set(graph_or_adj.nodes()) == set(range(n)) else list(graph_or_adj.nodes())
        A = nx.adjacency_matrix(graph_or_adj, nodelist=nodes, dtype=float).tocsr()
    else:
        A = graph_or_adj.tocsr().astype(float)
        n = A.shape[0]

    if n == 0 or A.nnz == 0:
        uniform = np.ones(n, dtype=float) / max(1, n)
        return RankResult(scores=uniform, hub_scores=uniform, iterations=1, converged=True)

    # Dimensionality constraint
    actual_k = min(k, n - 1, A.nnz)
    if actual_k <= 0:
        uniform = np.ones(n, dtype=float) / n
        return RankResult(scores=uniform, hub_scores=uniform, iterations=1, converged=True)

    eigengap = None
    try:
        # svds returns u, s, vt where vt is k x n right singular vectors (authorities)
        # and u is n x k left singular vectors (hubs)
        u, s, vt = sp.linalg.svds(A, k=actual_k)
        # svds returns singular values in ascending order; reverse to descending
        idx = np.argsort(s)[::-1]
        s = s[idx]
        u = u[:, idx]
        vt = vt[idx, :]

        if len(s) >= 2:
            eigengap = float(s[0]**2 - s[1]**2)

        if weighted_by_singular_values:
            weights = s**2
        else:
            weights = np.ones(actual_k, dtype=float)

        # Authority score = sum_j weights[j] * vt[j, i]^2
        # vt**2 has shape (actual_k, n)
        a_sq = (vt ** 2)  # shape (k, n)
        a = weights.dot(a_sq)

        # Hub score = sum_j weights[j] * u[i, j]^2
        u_sq = (u ** 2)  # shape (n, k)
        h = u_sq.dot(weights)

    except Exception:
        # Fallback to in-degree and out-degree if svds fails
        a = np.array(A.sum(axis=0)).flatten()
        h = np.array(A.sum(axis=1)).flatten()

    a_sum = a.sum()
    h_sum = h.sum()
    a_final = a / a_sum if a_sum > 0 else np.ones(n) / n
    h_final = h / h_sum if h_sum > 0 else np.ones(n) / n

    elapsed = time.perf_counter() - start_time
    return RankResult(
        scores=a_final,
        hub_scores=h_final,
        iterations=actual_k,
        converged=True,
        eigengap=eigengap,
        elapsed_time=elapsed
    )
