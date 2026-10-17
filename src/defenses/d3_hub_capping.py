"""Defense D3: Hub-Contribution Capping.

Caps the maximum authority contribution that any single hub page can confer
to any target authority node, preventing massive hub inflation attacks.
"""
import time
from typing import Union
import numpy as np
import scipy.sparse as sp
import networkx as nx

from src.rankers.base import RankResult
from src.config import HITS_TOL, HITS_MAX_ITER


def hub_capped_hits(
    graph_or_adj: Union[nx.DiGraph, sp.spmatrix],
    cap_fraction: float = 0.10,
    tol: float = HITS_TOL,
    max_iter: int = HITS_MAX_ITER
) -> RankResult:
    """Computes HITS with hub-contribution capping.

    Parameters
    ----------
    graph_or_adj : nx.DiGraph or sp.spmatrix
        Input directed graph or sparse adjacency matrix.
    cap_fraction : float
        Maximum fraction of total hub score that a single hub can contribute to an authority.
    tol : float
        Convergence tolerance.
    max_iter : int
        Maximum number of iterations.

    Returns
    -------
    RankResult
        Defended HITS scores.
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
    h = np.ones(n, dtype=float) / np.sqrt(n)
    a = np.ones(n, dtype=float) / np.sqrt(n)

    converged = False
    it = 0

    for it in range(1, max_iter + 1):
        h_prev = h.copy()
        a_prev = a.copy()

        # Cap individual hub contribution
        h_sum = h.sum()
        max_allowed_hub = cap_fraction * h_sum if h_sum > 0 else 1.0 / n
        h_capped = np.minimum(h, max_allowed_hub)

        # Authority update with capped hubs: a = A^T * h_capped
        a = AT.dot(h_capped)
        a_norm = np.linalg.norm(a, 2)
        if a_norm > 0:
            a = a / a_norm
        else:
            a = np.ones(n, dtype=float) / np.sqrt(n)

        # Hub update: h = A * a
        h = A.dot(a)
        h_norm = np.linalg.norm(h, 2)
        if h_norm > 0:
            h = h / h_norm
        else:
            h = np.ones(n, dtype=float) / np.sqrt(n)

        diff = np.sum(np.abs(a - a_prev)) + np.sum(np.abs(h - h_prev))
        if diff < tol:
            converged = True
            break

    a_sum = a.sum()
    h_sum = h.sum()
    a_final = a / a_sum if a_sum > 0 else np.ones(n) / n
    h_final = h / h_sum if h_sum > 0 else np.ones(n) / n

    elapsed = time.perf_counter() - start_time
    return RankResult(
        scores=a_final,
        hub_scores=h_final,
        iterations=it,
        converged=converged,
        elapsed_time=elapsed
    )
