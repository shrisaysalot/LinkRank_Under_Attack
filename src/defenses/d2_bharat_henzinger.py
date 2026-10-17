"""Defense D2: Bharat-Henzinger (1998) edge weighting.

Weights edges inversely proportional to the number of links between the source
and destination clusters/domains to mitigate link farm collusion.
"""
from typing import Dict, Optional, Union
import numpy as np
import networkx as nx
import scipy.sparse as sp

from src.rankers.hits import hits
from src.rankers.base import RankResult


def bharat_henzinger_hits(
    G: nx.DiGraph,
    domain_map: Optional[Dict[int, str]] = None,
    tol: float = 1e-8,
    max_iter: int = 200
) -> RankResult:
    """Computes HITS with Bharat-Henzinger edge weights.

    If domain_map is provided, edge (u, v) weight is 1 / (links from domain(u) to domain(v)).
    If domain_map is not provided, uses weakly connected component / community grouping.
    """
    n = G.number_of_nodes()
    if n == 0:
        return RankResult(scores=np.array([]), hub_scores=np.array([]))

    # Determine domain / cluster for each node
    if domain_map is None:
        # Fallback: group by 2-hop neighborhood hash or community
        domain_map = {}
        for idx, comp in enumerate(nx.weakly_connected_components(G)):
            for u in comp:
                domain_map[u] = f"comp_{idx}"

    # Count edges between domains: C[d_source, d_target]
    inter_domain_counts: Dict[tuple, int] = {}
    for u, v in G.edges():
        d_u = domain_map.get(u, str(u))
        d_v = domain_map.get(v, str(v))
        key = (d_u, d_v)
        inter_domain_counts[key] = inter_domain_counts.get(key, 0) + 1

    # Build weighted adjacency matrix
    rows, cols, data = [], [], []
    nodes = list(range(n)) if set(G.nodes()) == set(range(n)) else list(G.nodes())
    node_to_idx = {node: i for i, node in enumerate(nodes)}

    for u, v in G.edges():
        d_u = domain_map.get(u, str(u))
        d_v = domain_map.get(v, str(v))
        count = inter_domain_counts.get((d_u, d_v), 1)
        w = 1.0 / count

        rows.append(node_to_idx[u])
        cols.append(node_to_idx[v])
        data.append(w)

    A_weighted = sp.csr_matrix((data, (rows, cols)), shape=(n, n), dtype=float)

    # Run sparse power iteration on weighted adjacency
    return hits(A_weighted, tol=tol, max_iter=max_iter)
