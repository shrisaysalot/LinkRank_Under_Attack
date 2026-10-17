"""Stochastic Approach for Link-Structure Analysis (SALSA) via sparse power iteration."""
import time
from typing import Union
import numpy as np
import scipy.sparse as sp
import networkx as nx

from src.rankers.base import RankResult
from src.config import SALSA_TOL, SALSA_MAX_ITER


def salsa(
    graph_or_adj: Union[nx.DiGraph, sp.spmatrix],
    tol: float = SALSA_TOL,
    max_iter: int = SALSA_MAX_ITER,
    teleport_eps: float = 1e-4
) -> RankResult:
    """Computes SALSA authority and hub scores via bipartite random walk.

    Parameters
    ----------
    graph_or_adj : nx.DiGraph or sp.spmatrix
        Input directed graph or sparse adjacency matrix.
    tol : float
        Convergence tolerance.
    max_iter : int
        Maximum number of power iterations.
    teleport_eps : float
        Small ergodic teleport probability to guarantee convergence across disconnected components.

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

    if n == 0 or A.nnz == 0:
        uniform = np.ones(n, dtype=float) / max(1, n)
        return RankResult(scores=uniform, hub_scores=uniform, iterations=0, converged=True)

    AT = A.T.tocsr()

    in_degrees = np.array(A.sum(axis=0)).flatten()
    out_degrees = np.array(A.sum(axis=1)).flatten()

    has_in = in_degrees > 0
    has_out = out_degrees > 0

    if not np.any(has_in):
        uniform = np.ones(n, dtype=float) / n
        return RankResult(scores=uniform, hub_scores=uniform, iterations=0, converged=True)

    inv_in = np.zeros(n, dtype=float)
    inv_in[has_in] = 1.0 / in_degrees[has_in]

    inv_out = np.zeros(n, dtype=float)
    inv_out[has_out] = 1.0 / out_degrees[has_out]

    # Pre-normalize operators
    # a_next = (1 - eps) * A^T * D_out^-1 * A * (D_in^-1 * a) + eps * uniform_auth
    u_auth = np.zeros(n, dtype=float)
    u_auth[has_in] = 1.0 / np.sum(has_in)

    a = u_auth.copy()
    converged = False
    it = 0

    for it in range(1, max_iter + 1):
        a_prev = a.copy()

        # Step 1: authority -> hub
        step1 = a * inv_in
        step2 = A.dot(step1)

        # Step 2: hub -> authority
        step3 = step2 * inv_out
        step4 = AT.dot(step3)

        # Teleport and renormalize dangling probability mass
        mass = step4.sum()
        if mass > 0:
            a_cand = step4 / mass
            a = (1.0 - teleport_eps) * a_cand + teleport_eps * u_auth
        else:
            a = u_auth.copy()

        if np.sum(np.abs(a - a_prev)) < tol:
            converged = True
            break

    # Corresponding hub scores: h proportional to out-degrees or A * a
    h = A.dot(a)
    h_sum = h.sum()
    if h_sum > 0:
        h = h / h_sum
    else:
        u_hub = np.zeros(n, dtype=float)
        if np.any(has_out):
            u_hub[has_out] = 1.0 / np.sum(has_out)
        else:
            u_hub = np.ones(n) / n
        h = u_hub

    elapsed = time.perf_counter() - start_time
    return RankResult(
        scores=a,
        hub_scores=h,
        iterations=it,
        converged=converged,
        elapsed_time=elapsed
    )
