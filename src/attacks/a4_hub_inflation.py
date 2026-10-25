"""Attack A4: Hub Inflation.

- Proposal A4 (attack_a4_hub_inflation): The target page (or exactly ONE fake page)
  links directly to the c highest-authority real pages (c edges, no fake hub farm).
- A4b (attack_a4b_multi_hub_inflation): Previous multi-hub variant where p fake hubs
  each link to target AND top legitimate authorities.
"""
from typing import Optional, List
import numpy as np
import networkx as nx
import scipy.sparse as sp

from src.attacks.base import AttackResult
from src.rankers.hits import hits


def attack_a4_hub_inflation(
    G: nx.DiGraph,
    target_node: int,
    budget: int = 10,
    c_top: int = 3,
    use_one_fake_page: bool = False,
    clean_top_authorities: Optional[List[int]] = None
) -> AttackResult:
    """Attack A4 (Proposal Definition): Target (or ONE fake page) links to the
    c highest-authority real pages. No farm of fake hubs is created.

    Parameters
    ----------
    G : nx.DiGraph
        Clean graph.
    target_node : int
        Target page.
    budget : int
        Total edge budget (at most c_top edges added).
    c_top : int
        Number of top authentic authorities to link to.
    use_one_fake_page : bool
        If False, target page itself out-links to real authorities (0 nodes added).
        If True, 1 fake page links to target and real authorities (1 node added).
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

    added_nodes = []
    added_edges = []

    if not use_one_fake_page:
        # Target itself out-links to top authorities (0 fake nodes added)
        for auth in clean_top_authorities:
            if len(added_edges) < budget and not G_att.has_edge(target_node, auth):
                G_att.add_edge(target_node, auth)
                added_edges.append((target_node, auth))
    else:
        # Exactly ONE fake page links to target and top authorities (1 fake node added)
        fake_node = max_node + 1
        G_att.add_node(fake_node)
        added_nodes.append(fake_node)

        # First edge: fake page -> target
        if len(added_edges) < budget:
            G_att.add_edge(fake_node, target_node)
            added_edges.append((fake_node, target_node))

        # Remaining edges: fake page -> top authorities
        for auth in clean_top_authorities:
            if len(added_edges) < budget and not G_att.has_edge(fake_node, auth):
                G_att.add_edge(fake_node, auth)
                added_edges.append((fake_node, auth))

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


def attack_a4b_multi_hub_inflation(
    G: nx.DiGraph,
    target_node: int,
    budget: int = 10,
    c_top: int = 3,
    clean_top_authorities: Optional[List[int]] = None
) -> AttackResult:
    """Attack A4b: Multi-hub inflation variant (p fake hubs each linking to
    target AND top legitimate authorities).
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

    cost_per_hub = 1 + c_eff if c_eff > 0 else 1
    num_hubs = max(1, budget // cost_per_hub)

    added_nodes = []
    added_edges = []
    edge_count = 0

    for i in range(1, num_hubs + 1):
        if edge_count >= budget:
            break
        fake_hub = max_node + i
        G_att.add_node(fake_hub)
        added_nodes.append(fake_hub)

        # Edge to target
        G_att.add_edge(fake_hub, target_node)
        added_edges.append((fake_hub, target_node))
        edge_count += 1

        # Edges to top authorities
        for auth in clean_top_authorities:
            if edge_count < budget and not G_att.has_edge(fake_hub, auth):
                G_att.add_edge(fake_hub, auth)
                added_edges.append((fake_hub, auth))
                edge_count += 1

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
