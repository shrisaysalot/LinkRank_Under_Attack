"""Attack A1: Single Fake Hub."""
import networkx as nx
import scipy.sparse as sp

from src.attacks.base import AttackResult


def attack_a1_single_fake_hub(
    G: nx.DiGraph,
    target_node: int,
    budget: int = 1
) -> AttackResult:
    """Attack A1: Attacker adds exactly 1 fake page pointing to the target.

    Parameters
    ----------
    G : nx.DiGraph
        Clean graph.
    target_node : int
        Target page whose authority is to be promoted.
    budget : int
        Budget parameter (capped at 1 for single hub).

    Returns
    -------
    AttackResult
        Attacked graph with 1 fake node and 1 added edge.
    """
    G_att = G.copy()
    fake_node = max(G.nodes()) + 1 if len(G) > 0 else 0

    G_att.add_node(fake_node)
    G_att.add_edge(fake_node, target_node)

    adj = nx.adjacency_matrix(G_att, nodelist=range(G_att.number_of_nodes()), dtype=float).tocsr()
    return AttackResult(
        graph=G_att,
        adj_matrix=adj,
        target_node=target_node,
        added_nodes=[fake_node],
        added_edges=[(fake_node, target_node)],
        cost_nodes=1,
        cost_edges=1
    )
