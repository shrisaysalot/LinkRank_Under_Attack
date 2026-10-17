"""Defense D4: Wu-Davison (2005) Link Farm Re-weighting.

Penalizes edges from hubs that share suspiciously high target overlap (Jaccard similarity).
"""
import numpy as np
import scipy.sparse as sp
import networkx as nx

from src.rankers.hits import hits
from src.rankers.base import RankResult


def wu_davison_hits(
    G: nx.DiGraph,
    overlap_threshold: float = 0.5,
    penalty_factor: float = 0.2,
    tol: float = 1e-8,
    max_iter: int = 200
) -> RankResult:
    """Computes HITS with Wu-Davison link farm penalization.

    Hubs sharing target Jaccard similarity > overlap_threshold have their out-edges down-weighted.
    """
    n = G.number_of_nodes()
    if n == 0:
        return RankResult(scores=np.array([]), hub_scores=np.array([]))

    nodes = list(range(n)) if set(G.nodes()) == set(range(n)) else list(G.nodes())
    node_to_idx = {node: i for i, node in enumerate(nodes)}

    # Compute out-targets for each node
    out_sets = {node: set(G.successors(node)) for node in nodes}

    # Find penalized hubs
    hub_weights = np.ones(n, dtype=float)
    hub_list = [u for u in nodes if len(out_sets[u]) > 0]

    # Efficient pairwise comparison for active hubs
    for i in range(len(hub_list)):
        u = hub_list[i]
        set_u = out_sets[u]
        if len(set_u) == 0:
            continue
        for j in range(i + 1, min(len(hub_list), i + 50)):  # localized check
            v = hub_list[j]
            set_v = out_sets[v]
            intersection = len(set_u & set_v)
            union = len(set_u | set_v)
            if union > 0 and (intersection / union) > overlap_threshold:
                hub_weights[node_to_idx[u]] *= penalty_factor
                hub_weights[node_to_idx[v]] *= penalty_factor

    # Build penalized adjacency matrix
    rows, cols, data = [], [], []
    for u, v in G.edges():
        u_idx = node_to_idx[u]
        v_idx = node_to_idx[v]
        rows.append(u_idx)
        cols.append(v_idx)
        data.append(hub_weights[u_idx])

    A_penalized = sp.csr_matrix((data, (rows, cols)), shape=(n, n), dtype=float)
    return hits(A_penalized, tol=tol, max_iter=max_iter)
