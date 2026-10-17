"""Attack A3: Complete Bipartite Block (p fake hubs x q fake authorities including target)."""
import math
import networkx as nx
import scipy.sparse as sp

from src.attacks.base import AttackResult


def attack_a3_bipartite_block(
    G: nx.DiGraph,
    target_node: int,
    budget: int = 16
) -> AttackResult:
    """Attack A3: Creates a bipartite core K_{p, q} of p fake hubs and q authorities,
    where the target is one of the authorities, utilizing up to budget edges.

    Parameters
    ----------
    G : nx.DiGraph
        Clean graph.
    target_node : int
        Target page.
    budget : int
        Total edge budget (p * q <= budget).

    Returns
    -------
    AttackResult
        Attacked graph with planted bipartite block.
    """
    G_att = G.copy()
    max_node = max(G.nodes()) if len(G) > 0 else -1

    # Choose p and q such that p * q <= budget
    p = max(1, int(math.isqrt(budget)))
    q = max(1, budget // p)

    # Fake hubs: p nodes
    fake_hubs = [max_node + 1 + i for i in range(p)]
    # Fake authorities (excluding target which is already an authority): q - 1 nodes
    fake_auths = [max_node + 1 + p + j for j in range(q - 1)]
    all_authorities = [target_node] + fake_auths

    added_nodes = fake_hubs + fake_auths
    added_edges = []

    for h in fake_hubs:
        G_att.add_node(h)
    for a in fake_auths:
        G_att.add_node(a)

    for h in fake_hubs:
        for a in all_authorities:
            if len(added_edges) < budget and not G_att.has_edge(h, a):
                G_att.add_edge(h, a)
                added_edges.append((h, a))

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
