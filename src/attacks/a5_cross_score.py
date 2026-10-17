"""Attack A5: Cross-Score attack with reciprocal cross-links between fake hubs, target, and top authorities."""
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
    """Attack A5: Cross-Score attack.

    Creates fake hubs pointing to both the target and real top authorities,
    plus cross-linking edges among the attacker-controlled cluster to maximize mutual reinforcement.

    Parameters
    ----------
    G : nx.DiGraph
        Clean graph.
    target_node : int
        Target page.
    budget : int
        Total edge budget.
    c_top : int
        Number of real top authorities to target.

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
        clean_top_authorities = [n for n in order if n != target_node][:c_top]
    elif clean_top_authorities is None:
        clean_top_authorities = []

    clean_top_authorities = [n for n in clean_top_authorities if n != target_node][:c_top]

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
