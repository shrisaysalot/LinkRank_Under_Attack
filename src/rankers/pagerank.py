"""PageRank via sparse power iteration."""
import time
from typing import Union
import numpy as np
import scipy.sparse as sp
import networkx as nx

from src.rankers.base import RankResult
from src.config import PAGERANK_ALPHA, PAGERANK_TOL, PAGERANK_MAX_ITER


def pagerank(
    graph_or_adj: Union[nx.DiGraph, sp.spmatrix],
    alpha: float = PAGERANK_ALPHA,
    tol: float = PAGERANK_TOL,
    max_iter: int = PAGERANK_MAX_ITER,
    personalization: Union[np.ndarray, None] = None
) -> RankResult:
    """Computes PageRank using sparse power iteration.

    Parameters
    ----------
    graph_or_adj : nx.DiGraph or sp.spmatrix
        Input directed graph or sparse adjacency matrix.
    alpha : float
        Damping parameter (default: 0.85).
    tol : float
        Tolerance for convergence (L1 difference).
    max_iter : int
        Maximum number of iterations.
    personalization : np.ndarray, optional
        Custom teleport distribution (default: uniform 1/n).

    Returns
    -------
    RankResult
        Contains PageRank scores in .scores, iteration count, and elapsed time.
    """
    start_time = time.perf_counter()

    if isinstance(graph_or_adj, (nx.DiGraph, nx.Graph)):
        n = graph_or_adj.number_of_nodes()
        if n == 0:
            return RankResult(scores=np.array([]), iterations=0, converged=True)
        nodes = list(range(n)) if set(graph_or_adj.nodes()) == set(range(n)) else list(graph_or_adj.nodes())
        A = nx.adjacency_matrix(graph_or_adj, nodelist=nodes, dtype=float).tocsr()
    else:
        A = graph_or_adj.tocsr().astype(float)
        n = A.shape[0]

    if n == 0:
        return RankResult(scores=np.array([]), iterations=0, converged=True)

    if personalization is None:
        p_teleport = np.ones(n, dtype=float) / n
    else:
        p_teleport = personalization / personalization.sum()

    # Out-degrees
    out_degrees = np.array(A.sum(axis=1)).flatten()
    dangling = (out_degrees == 0)

    # Invert degrees for row normalization: D_out^-1
    inv_out = np.zeros(n, dtype=float)
    inv_out[~dangling] = 1.0 / out_degrees[~dangling]

    # Create normalized transition matrix AT_norm = (D^-1 A)^T = A^T D^-1
    # For A[i, j] > 0, normalized is A[i, j] / out_degree[i]
    D_inv = sp.diags(inv_out, format="csr")
    AT_norm = (D_inv.dot(A)).T.tocsr()

    # Initial probability vector
    p = np.ones(n, dtype=float) / n
    converged = False
    it = 0

    for it in range(1, max_iter + 1):
        p_prev = p.copy()

        # Dangling sum
        dangling_sum = p[dangling].sum()

        # Update: alpha * AT_norm * p + (alpha * dangling_sum + (1 - alpha)) * p_teleport
        p = alpha * AT_norm.dot(p) + (alpha * dangling_sum + (1.0 - alpha)) * p_teleport

        # Check convergence
        err = np.sum(np.abs(p - p_prev))
        if err < tol:
            converged = True
            break

    elapsed = time.perf_counter() - start_time
    return RankResult(
        scores=p,
        iterations=it,
        converged=converged,
        elapsed_time=elapsed
    )
