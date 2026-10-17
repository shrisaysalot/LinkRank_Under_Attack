"""Hyperlink-Induced Topic Search (HITS) via sparse power iteration."""
import time
from typing import Union, Optional
import numpy as np
import scipy.sparse as sp
import networkx as nx

from src.rankers.base import RankResult
from src.config import HITS_TOL, HITS_MAX_ITER


def hits(
    graph_or_adj: Union[nx.DiGraph, sp.spmatrix],
    tol: float = HITS_TOL,
    max_iter: int = HITS_MAX_ITER,
    compute_eigengap: bool = False,
    normalize: bool = True
) -> RankResult:
    """Computes HITS authority and hub scores using sparse power iteration.

    Parameters
    ----------
    graph_or_adj : nx.DiGraph or sp.spmatrix
        Input directed graph or sparse adjacency matrix (A[i,j] = 1 if i -> j).
    tol : float
        Tolerance for convergence check (L1 difference between successive iterates).
    max_iter : int
        Maximum number of power iterations.
    compute_eigengap : bool
        If True, computes sigma_1^2 - sigma_2^2 via sparse SVD.
    normalize : bool
        If True, normalizes final scores to sum to 1 (L1 norm).

    Returns
    -------
    RankResult
        Contains authority scores in .scores, hub scores in .hub_scores,
        iteration count, eigengap, and elapsed time.
    """
    start_time = time.perf_counter()

    if isinstance(graph_or_adj, (nx.DiGraph, nx.Graph)):
        n = graph_or_adj.number_of_nodes()
        if n == 0:
            return RankResult(scores=np.array([]), hub_scores=np.array([]), iterations=0, converged=True)
        # Order nodes 0..n-1
        nodes = list(range(n)) if set(graph_or_adj.nodes()) == set(range(n)) else list(graph_or_adj.nodes())
        A = nx.adjacency_matrix(graph_or_adj, nodelist=nodes, dtype=float).tocsr()
    else:
        A = graph_or_adj.tocsr().astype(float)
        n = A.shape[0]

    if n == 0:
        return RankResult(scores=np.array([]), hub_scores=np.array([]), iterations=0, converged=True)

    AT = A.T.tocsr()

    # Initial vectors: uniformly distributed, L2 normalized
    h = np.ones(n, dtype=float) / np.sqrt(n)
    a = np.ones(n, dtype=float) / np.sqrt(n)

    converged = False
    it = 0

    for it in range(1, max_iter + 1):
        h_prev = h.copy()
        a_prev = a.copy()

        # Authority update: a = A^T * h
        a = AT.dot(h)
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

        # Check convergence on both vectors
        diff = np.sum(np.abs(a - a_prev)) + np.sum(np.abs(h - h_prev))
        if diff < tol:
            converged = True
            break

    # Final normalization
    if normalize:
        a_sum = a.sum()
        h_sum = h.sum()
        a_final = a / a_sum if a_sum > 0 else np.ones(n) / n
        h_final = h / h_sum if h_sum > 0 else np.ones(n) / n
    else:
        a_final = a
        h_final = h

    eigengap = None
    if compute_eigengap and n >= 3 and A.nnz > 0:
        try:
            s = sp.linalg.svds(A, k=min(2, n - 1), return_singular_vectors=False)
            s = np.sort(s)[::-1]
            if len(s) >= 2:
                eigengap = float(s[0]**2 - s[1]**2)
            else:
                eigengap = float(s[0]**2)
        except Exception:
            eigengap = None

    elapsed = time.perf_counter() - start_time

    return RankResult(
        scores=a_final,
        hub_scores=h_final,
        iterations=it,
        converged=converged,
        eigengap=eigengap,
        elapsed_time=elapsed
    )
