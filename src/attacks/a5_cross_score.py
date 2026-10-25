"""Attack A5: Cross-Score / Inflated Hubs.

- Proposal A5 (attack_a5_cross_score): p fake hubs each link to c real top authorities
  AND to the target (no cross-links between hubs).
- A5b (attack_a5b_cross_score): Inflated hubs plus reciprocal cross-links among fake hubs.
"""
from typing import Optional, List
import numpy as np
import networkx as nx
import scipy.sparse as sp

from src.attacks.base import AttackResult
from src.rankers.hits import hits


def attack_a5_cross_score(
    G: nx.DiGraph,
    target_node: int,
    budget: int = 15,
    c_top: int = 3,
    clean_top_authorities: Optional[List[int]] = None
) -> AttackResult:
    """Attack A5 (Proposal Definition): p fake hubs each link to c real top authorities
    AND to the target node. (No inter-hub cross links).

    Parameters
    ----------
    G : nx.DiGraph
        Clean graph.
    target_node : int
        Target page.
    budget : int
        Total edge budget.
    c_top : int
        Number of real top authorities each fake hub points to.
    clean_top_authorities : list of int, optional
        Precomputed top authorities; if None, computed via HITS on G.

    Returns
    -------
    AttackResult
        Attacked graph.
    """
    G_att = G.copy()
    max_node = max(G.nodes()) if len(G) > 0 else -1

    if clean_top_authorities is None and len(G) > 0:
        res = hits(G, max_iter=50)
        order = np.argsort(-res.scores)
        clean_top_authorities = [int(n) for n in order if n != target_node][:c_top]
    elif clean_top_authorities is None:
        clean_top_authorities = []

    clean_top_authorities = [int(n) for n in clean_top_authorities if n != target_node][:c_top]
    c_eff = len(clean_top_authorities)

    # Cost per hub: 1 link to target + c_eff links to real top authorities
    cost_per_hub = 1 + c_eff if c_eff > 0 else 1
    p = max(1, budget // cost_per_hub)
    fake_hubs = [max_node + 1 + i for i in range(p)]

    added_nodes = list(fake_hubs)
    added_edges = []

    for h in fake_hubs:
        G_att.add_node(h)

    # 1. Primary links: each fake hub -> target
    for h in fake_hubs:
        if len(added_edges) < budget and not G_att.has_edge(h, target_node):
            G_att.add_edge(h, target_node)
            added_edges.append((h, target_node))

    # 2. Links to real top authorities: each fake hub -> real authorities
    for h in fake_hubs:
        for auth in clean_top_authorities:
            if len(added_edges) < budget and not G_att.has_edge(h, auth):
                G_att.add_edge(h, auth)
                added_edges.append((h, auth))

    adj = nx.adjacency_matrix(G_att, nodelist=range(G_att.number_of_nodes()), dtype=float).tocsr()
    return AttackResult(
        graph=G_att,
        adj_matrix=adj,
        target_node=target_node,
        added_nodes=added_nodes,
        added_edges=added_edges,
        cost_nodes=len(added_nodes),
        cost_edges=len(added_edges)
    )


def attack_a5b_cross_score(
    G: nx.DiGraph,
    target_node: int,
    budget: int = 15,
    c_top: int = 3,
    clean_top_authorities: Optional[List[int]] = None
) -> AttackResult:
    """Attack A5b: Cross-Score attack with reciprocal cross-links between fake hubs."""
    G_att = G.copy()
    max_node = max(G.nodes()) if len(G) > 0 else -1

    if clean_top_authorities is None and len(G) > 0:
        res = hits(G, max_iter=50)
        order = np.argsort(-res.scores)
        clean_top_authorities = [int(n) for n in order if n != target_node][:c_top]
    elif clean_top_authorities is None:
        clean_top_authorities = []

    clean_top_authorities = [int(n) for n in clean_top_authorities if n != target_node][:c_top]

    # Allocate nodes: p fake hubs
    p = max(2, budget // (len(clean_top_authorities) + 2)) if len(clean_top_authorities) > 0 else max(1, budget // 2)
    fake_hubs = [max_node + 1 + i for i in range(p)]

    added_nodes = list(fake_hubs)
    added_edges = []

    for h in fake_hubs:
        G_att.add_node(h)

    # 1. Primary links: fake hubs -> target
    for h in fake_hubs:
        if len(added_edges) < budget and not G_att.has_edge(h, target_node):
            G_att.add_edge(h, target_node)
            added_edges.append((h, target_node))

    # 2. Inflation links: fake hubs -> real top authorities
    for h in fake_hubs:
        for auth in clean_top_authorities:
            if len(added_edges) < budget and not G_att.has_edge(h, auth):
                G_att.add_edge(h, auth)
                added_edges.append((h, auth))

    # 3. Cross links among fake hubs (h_i -> h_j) to amplify internal scores
    for i, h1 in enumerate(fake_hubs):
        for j, h2 in enumerate(fake_hubs):
            if i != j and len(added_edges) < budget and not G_att.has_edge(h1, h2):
                G_att.add_edge(h1, h2)
                added_edges.append((h1, h2))

    adj = nx.adjacency_matrix(G_att, nodelist=range(G_att.number_of_nodes()), dtype=float).tocsr()
    return AttackResult(
        graph=G_att,
        adj_matrix=adj,
        target_node=target_node,
        added_nodes=added_nodes,
        added_edges=added_edges,
        cost_nodes=len(added_nodes),
        cost_edges=len(added_edges)
    )
