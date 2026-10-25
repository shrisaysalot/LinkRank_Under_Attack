"""Defense D2: Bharat-Henzinger (1998) edge weighting.

Weights edges inversely proportional to the number of links from the same source
domain/cluster to the destination page:
  weight(u, v) = 1.0 / k
where k is the number of documents in domain(u) that link to document v.
"""
from typing import Dict, Optional, Union
import numpy as np
import networkx as nx
import scipy.sparse as sp

from src.rankers.hits import hits
from src.rankers.base import RankResult


def infer_domain_map(G: nx.DiGraph, domain_map: Optional[Dict[int, str]] = None) -> Dict[int, str]:
    """Infers domain/host groupings for nodes:
    - Explicit domain_map if provided.
    - Node attribute 'domain' or 'community' if present.
    - Block proxy for SNAP / synthetic (blocks of 50 nodes, with injected nodes >= N grouped together).
    """
    if domain_map is not None:
        return dict(domain_map)

    # Check node attributes
    inferred = {}
    has_attr = any('domain' in G.nodes[u] or 'community' in G.nodes[u] for u in G.nodes())
    if has_attr:
        for u in G.nodes():
            inferred[u] = str(G.nodes[u].get('domain', G.nodes[u].get('community', f"block_{u // 50}")))
        return inferred

    # Documented node-ID-block proxy (e.g. 50 nodes per domain/subnet)
    # Detect original vs injected nodes if node IDs have a gap or large values
    nodes = sorted(list(G.nodes()))
    for u in nodes:
        inferred[u] = f"domain_block_{u // 50}"

    return inferred


def bharat_henzinger_hits(
    G: nx.DiGraph,
    domain_map: Optional[Dict[int, str]] = None,
    tol: float = 1e-8,
    max_iter: int = 200
) -> RankResult:
    """Computes HITS with Bharat-Henzinger (1998) domain-to-page edge weighting.

    Each edge (u, v) receives weight 1/k, where k is the number of edges pointing
    to page v from all pages residing in domain(u).

    Parameters
    ----------
    G : nx.DiGraph
        Input directed graph.
    domain_map : dict, optional
        Mapping from node ID to domain/cluster identifier string.
    tol : float
        Convergence tolerance.
    max_iter : int
        Maximum iterations.

    Returns
    -------
    RankResult
        Defended ranking results.
    """
    n = G.number_of_nodes()
    if n == 0:
        return RankResult(scores=np.array([]), hub_scores=np.array([]))

    domains = infer_domain_map(G, domain_map)

    # Count edges from each source domain to each destination page v: k = C[d_source, v]
    domain_to_page_counts: Dict[tuple, int] = {}
    for u, v in G.edges():
        d_u = domains.get(u, f"dom_{u}")
        key = (d_u, v)
        domain_to_page_counts[key] = domain_to_page_counts.get(key, 0) + 1

    # Build weighted adjacency matrix
    nodes = list(range(n)) if set(G.nodes()) == set(range(n)) else list(G.nodes())
    node_to_idx = {node: i for i, node in enumerate(nodes)}

    rows, cols, data = [], [], []
    for u, v in G.edges():
        d_u = domains.get(u, f"dom_{u}")
        k = domain_to_page_counts.get((d_u, v), 1)
        w = 1.0 / float(k)

        rows.append(node_to_idx[u])
        cols.append(node_to_idx[v])
        data.append(w)

    A_weighted = sp.csr_matrix((data, (rows, cols)), shape=(n, n), dtype=float)
    return hits(A_weighted, tol=tol, max_iter=max_iter)
