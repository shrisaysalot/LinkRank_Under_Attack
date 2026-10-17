"""Defense D5: Trust-Based HITS with TrustRank seed prior."""
import time
from typing import Optional, List, Union
import numpy as np
import scipy.sparse as sp
import networkx as nx

from src.rankers.base import RankResult
from src.config import HITS_TOL, HITS_MAX_ITER, RANDOMIZED_HITS_EPS


def trust_based_hits(
    graph_or_adj: Union[nx.DiGraph, sp.spmatrix],
    trusted_seeds: Optional[List[int]] = None,
    eps: float = RANDOMIZED_HITS_EPS,
    tol: float = HITS_TOL,
    max_iter: int = HITS_MAX_ITER
) -> RankResult:
    """Computes Trust-Based HITS.

    Replaces uniform reset with a trusted seed prior in authority and hub updates:
      a = (1 - eps) * (A^T h / ||A^T h||) + eps * t_prior
      h = (1 - eps) * (A a / ||A a||) + eps * t_prior

    If trusted_seeds is None, uses top-k in-degree nodes as proxy trusted seeds.
    """
    start_time = time.perf_counter()

    if isinstance(graph_or_adj, (nx.DiGraph, nx.Graph)):
        n = graph_or_adj.number_of_nodes()
        nodes = list(range(n)) if set(graph_or_adj.nodes()) == set(range(n)) else list(graph_or_adj.nodes())
        A = nx.adjacency_matrix(graph_or_adj, nodelist=nodes, dtype=float).tocsr()
    else:
        A = graph_or_adj.tocsr().astype(float)
        n = A.shape[0]

    if n == 0:
        return RankResult(scores=np.array([]), hub_scores=np.array([]))

    AT = A.T.tocsr()

    # Build trust prior vector
    t_prior = np.zeros(n, dtype=float)
    if trusted_seeds is not None and len(trusted_seeds) > 0:
        valid_seeds = [s for s in trusted_seeds if s < n]
        if valid_seeds:
            t_prior[valid_seeds] = 1.0 / len(valid_seeds)
        else:
            t_prior[:] = 1.0 / n
    else:
        # Proxy trusted seeds: top 5% by in-degree
        in_degrees = np.array(A.sum(axis=0)).flatten()
        top_k = max(1, int(0.05 * n))
        top_seeds = np.argsort(-in_degrees)[:top_k]
        t_prior[top_seeds] = 1.0 / top_k

    h = t_prior.copy()
    a = t_prior.copy()
    converged = False
    it = 0

    for it in range(1, max_iter + 1):
        h_prev = h.copy()
        a_prev = a.copy()

        # Authority step
        a_cand = AT.dot(h)
        a_sum = a_cand.sum()
        if a_sum > 0:
            a_norm = a_cand / a_sum
            a = (1.0 - eps) * a_norm + eps * t_prior
        else:
            a = t_prior.copy()

        # Hub step
        h_cand = A.dot(a)
        h_sum = h_cand.sum()
        if h_sum > 0:
            h_norm = h_cand / h_sum
            h = (1.0 - eps) * h_norm + eps * t_prior
        else:
            h = t_prior.copy()

        diff = np.sum(np.abs(a - a_prev)) + np.sum(np.abs(h - h_prev))
        if diff < tol:
            converged = True
            break

    elapsed = time.perf_counter() - start_time
    return RankResult(
        scores=a,
        hub_scores=h,
        iterations=it,
        converged=converged,
        elapsed_time=elapsed
    )
