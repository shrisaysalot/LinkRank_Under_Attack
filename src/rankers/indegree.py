"""In-degree centrality baseline ranker."""
import time
from typing import Union
import numpy as np
import scipy.sparse as sp
import networkx as nx

from src.rankers.base import RankResult


def indegree(
    graph_or_adj: Union[nx.DiGraph, sp.spmatrix],
    normalize: bool = True
) -> RankResult:
    """Computes normalized in-degree baseline ranking.

    Parameters
    ----------
    graph_or_adj : nx.DiGraph or sp.spmatrix
        Input directed graph or sparse adjacency matrix.
    normalize : bool
        If True, normalizes scores to sum to 1.

    Returns
    -------
    RankResult
        Contains in-degree scores in .scores.
    """
    start_time = time.perf_counter()

    if isinstance(graph_or_adj, (nx.DiGraph, nx.Graph)):
        n = graph_or_adj.number_of_nodes()
        if n == 0:
            return RankResult(scores=np.array([]), iterations=1, converged=True)
        nodes = list(range(n)) if set(graph_or_adj.nodes()) == set(range(n)) else list(graph_or_adj.nodes())
        A = nx.adjacency_matrix(graph_or_adj, nodelist=nodes, dtype=float).tocsr()
    else:
        A = graph_or_adj.tocsr().astype(float)
        n = A.shape[0]

    if n == 0:
        return RankResult(scores=np.array([]), iterations=1, converged=True)

    # In-degree is column sum
    in_deg = np.array(A.sum(axis=0)).flatten()

    if normalize:
        total = in_deg.sum()
        scores = in_deg / total if total > 0 else np.ones(n) / n
    else:
        scores = in_deg

    elapsed = time.perf_counter() - start_time
    return RankResult(
        scores=scores,
        iterations=1,
        converged=True,
        elapsed_time=elapsed
    )
