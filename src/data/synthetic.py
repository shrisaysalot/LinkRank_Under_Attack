"""Synthetic graph generators: Barabasi-Albert, Erdos-Renyi, and SBM with Planted Bipartite Core."""
from typing import Tuple, List
import numpy as np
import networkx as nx
import scipy.sparse as sp


def generate_barabasi_albert(
    n: int = 1000,
    m: int = 4,
    seed: int = 42
) -> nx.DiGraph:
    """Generates a scale-free directed Barabasi-Albert graph.

    Edges are oriented from newer nodes to older nodes with probability 0.5,
    and older to newer with probability 0.5 to produce a directed network.
    """
    rng = np.random.RandomState(seed)
    undirected_G = nx.barabasi_albert_graph(n=n, m=m, seed=seed)
    G = nx.DiGraph()
    G.add_nodes_from(range(n))

    for u, v in undirected_G.edges():
        # Orient edges with equal probability, or both
        coin = rng.rand()
        if coin < 0.45:
            G.add_edge(u, v)
        elif coin < 0.90:
            G.add_edge(v, u)
        else:
            G.add_edge(u, v)
            G.add_edge(v, u)

    return G


def generate_erdos_renyi(
    n: int = 1000,
    p: float = 0.005,
    seed: int = 42
) -> nx.DiGraph:
    """Generates an Erdos-Renyi directed random graph G(n, p)."""
    return nx.erdos_renyi_graph(n=n, p=p, seed=seed, directed=True)


def generate_planted_bipartite_sbm(
    n_background: int = 800,
    n_planted_hubs: int = 20,
    n_planted_authorities: int = 20,
    p_sparse: float = 0.004,
    p_dense: float = 0.85,
    seed: int = 42
) -> Tuple[nx.DiGraph, List[int], List[int]]:
    """Generates a graph with a planted dense bipartite community (TKC / community farm).

    Parameters
    ----------
    n_background : int
        Number of background web pages.
    n_planted_hubs : int
        Number of nodes in the planted hub community.
    n_planted_authorities : int
        Number of nodes in the planted authority community.
    p_sparse : float
        Background connection probability.
    p_dense : float
        Link density inside the planted bipartite community.
    seed : int
        Random seed.

    Returns
    -------
    G : nx.DiGraph
        Total graph of size n_background + n_planted_hubs + n_planted_authorities.
    hub_nodes : list of int
        Indices of planted hubs.
    authority_nodes : list of int
        Indices of planted authorities.
    """
    rng = np.random.RandomState(seed)
    n_total = n_background + n_planted_hubs + n_planted_authorities
    G = nx.DiGraph()
    G.add_nodes_from(range(n_total))

    hub_nodes = list(range(n_background, n_background + n_planted_hubs))
    auth_nodes = list(range(n_background + n_planted_hubs, n_total))

    # 1. Background edges (Erdos-Renyi style)
    bg_nodes = list(range(n_background))
    for u in bg_nodes:
        # Sample background out-edges
        targets = rng.choice(bg_nodes, size=rng.binomial(n_background, p_sparse), replace=False)
        for v in targets:
            if u != v:
                G.add_edge(u, v)

    # 2. Planted dense bipartite community: hub_nodes -> auth_nodes
    for h in hub_nodes:
        for a in auth_nodes:
            if rng.rand() < p_dense:
                G.add_edge(h, a)

    # 3. Sparse cross-links connecting community to background
    for h in hub_nodes:
        bg_targets = rng.choice(bg_nodes, size=max(1, int(n_background * p_sparse)), replace=False)
        for v in bg_targets:
            G.add_edge(h, v)

    for v in bg_nodes:
        if rng.rand() < p_sparse * 2:
            a = rng.choice(auth_nodes)
            G.add_edge(v, a)

    return G, hub_nodes, auth_nodes
