"""Attack A2: Hub Farm (p fake pages pointing to the target)."""
import networkx as nx
import scipy.sparse as sp

from src.attacks.base import AttackResult


def attack_a2_hub_farm(
    G: nx.DiGraph,
    target_node: int,
    budget: int = 10
) -> AttackResult:
    """Attack A2: Attacker creates a farm of p = budget fake hub pages,
    each adding a direct incoming link to the target node.

    Parameters
    ----------
    G : nx.DiGraph
        Clean graph.
    target_node : int
        Target page.
    budget : int
        Number of fake hub pages to create.

    Returns
    -------
    AttackResult
        Attacked graph with p fake nodes and p added edges.
    """
    G_att = G.copy()
    max_node = max(G.nodes()) if len(G) > 0 else -1

    added_nodes = []
    added_edges = []

    for i in range(1, budget + 1):
        fake_node = max_node + i
        G_att.add_node(fake_node)
        G_att.add_edge(fake_node, target_node)
        added_nodes.append(fake_node)
        added_edges.append((fake_node, target_node))

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
