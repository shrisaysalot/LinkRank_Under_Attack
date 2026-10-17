"""Randomized HITS (Ng, Zheng, Jordan 2001) with uniform reset distribution."""
import time
from typing import Union
import numpy as np
import scipy.sparse as sp
import networkx as nx

from src.rankers.base import RankResult
from src.config import HITS_TOL, HITS_MAX_ITER, RANDOMIZED_HITS_EPS


def randomized_hits(
    graph_or_adj: Union[nx.DiGraph, sp.spmatrix],
    eps: float = RANDOMIZED_HITS_EPS,
    tol: float = HITS_TOL,
    max_iter: int = HITS_MAX_ITER,
    compute_eigengap: bool = False
) -> RankResult:
    """Computes Randomized HITS authority and hub scores (Ng et al. 2001).

    At each step:
      a = (1 - eps) * (A^T h / ||A^T h||_1) + eps * u
      h = (1 - eps) * (A a / ||A a||_1) + eps * u

    Parameters
    ----------
    graph_or_adj : nx.DiGraph or sp.spmatrix
        Input directed graph or sparse adjacency matrix.
    eps : float
        Random reset probability (default: 0.15).
    tol : float
        Tolerance for convergence check.
    max_iter : int
        Maximum number of iterations.
    compute_eigengap : bool
        If True, estimates eigengap.

    Returns
    -------
    RankResult
        Contains authority scores in .scores, hub scores in .hub_scores,
        iteration count, and elapsed time.
    """
    start_time = time.perf_counter()

    if isinstance(graph_or_adj, (nx.DiGraph, nx.Graph)):
        n = graph_or_adj.number_of_nodes()
        if n == 0:
            return RankResult(scores=np.array([]), hub_scores=np.array([]), iterations=0, converged=True)
        nodes = list(range(n)) if set(graph_or_adj.nodes()) == set(range(n)) else list(graph_or_adj.nodes())
        A = nx.adjacency_matrix(graph_or_adj, nodelist=nodes, dtype=float).tocsr()
    else:
        A = graph_or_adj.tocsr().astype(float)
        n = A.shape[0]

    if n == 0:
        return RankResult(scores=np.array([]), hub_scores=np.array([]), iterations=0, converged=True)

    AT = A.T.tocsr()
    u = np.ones(n, dtype=float) / n

    h = u.copy()
    a = u.copy()
    converged = False
    it = 0

    for it in range(1, max_iter + 1):
        h_prev = h.copy()
        a_prev = a.copy()

        # Authority step
        a_cand = AT.dot(h)
        a_cand_sum = a_cand.sum()
        if a_cand_sum > 0:
            a_norm = a_cand / a_cand_sum
            a = (1.0 - eps) * a_norm + eps * u
        else:
            a = u.copy()

        # Hub step
        h_cand = A.dot(a)
        h_cand_sum = h_cand.sum()
        if h_cand_sum > 0:
            h_norm = h_cand / h_cand_sum
            h = (1.0 - eps) * h_norm + eps * u
        else:
            h = u.copy()

        diff = np.sum(np.abs(a - a_prev)) + np.sum(np.abs(h - h_prev))
        if diff < tol:
            converged = True
            break

    eigengap = None
    if compute_eigengap and n >= 3 and A.nnz > 0:
        try:
            s = sp.linalg.svds(A, k=min(2, n - 1), return_singular_vectors=False)
            s = np.sort(s)[::-1]
            if len(s) >= 2:
                eigengap = float(s[0]**2 - s[1]**2)
        except Exception:
            eigengap = None

    elapsed = time.perf_counter() - start_time
    return RankResult(
        scores=a,
        hub_scores=h,
        iterations=it,
        converged=converged,
        eigengap=eigengap,
        elapsed_time=elapsed
    )
