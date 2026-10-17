"""Attack A6: Greedy gradient edge choice (dsigma/dA[i,j] = h[i]*a[j]) with candidate list re-verification."""
from typing import List, Tuple
import numpy as np
import networkx as nx
import scipy.sparse as sp

from src.attacks.base import AttackResult
from src.rankers.hits import hits


def attack_a6_greedy_gradient(
    G: nx.DiGraph,
    target_node: int,
    budget: int = 10,
    candidate_pool_size: int = 30
) -> AttackResult:
    """Attack A6: Greedily selects edges that maximize dsigma_1/dA[i,j] = h[i]*a[j],
    re-verifying candidate edges by actual target rank / authority gain.

    Parameters
    ----------
    G : nx.DiGraph
        Clean graph.
    target_node : int
        Target page.
    budget : int
        Number of edges to inject.
    candidate_pool_size : int
        Number of top candidate edges to evaluate in the short list.

    Returns
    -------
    AttackResult
        Attacked graph.
    """
    G_att = G.copy()
    added_edges: List[Tuple[int, int]] = []
    added_nodes: List[int] = []

    # If the attacker can also introduce fake hubs when existing hub in-links run out:
    max_node = max(G.nodes()) if len(G) > 0 else -1

    for step in range(budget):
        res = hits(G_att, max_iter=30)
        h = res.hub_scores
        a = res.scores

        # Rank all non-existing edges (u, target_node) by gradient = h[u] * a[target_node]
        # (gradient is proportional to h[u])
        existing_nodes = list(G_att.nodes())
        candidates = []

        for u in existing_nodes:
            if u != target_node and not G_att.has_edge(u, target_node):
                grad = h[u] * a[target_node] if h is not None and u < len(h) else 0.0
                candidates.append((u, target_node, grad))

        # Also consider creating a new fake hub pointing to target
        fake_node = max_node + step + 1
        candidates.append((fake_node, target_node, 0.0))

        # Sort by gradient descending
        candidates.sort(key=lambda x: x[2], reverse=True)
        short_list = candidates[:candidate_pool_size]

        if not short_list:
            break

        # Re-verify on short candidate list: test actual target authority gain
        best_edge = None
        best_gain = -float("inf")
        is_new_node = False

        for u, v, _ in short_list:
            is_new = (u not in G_att)
            if is_new:
                G_att.add_node(u)
            G_att.add_edge(u, v)

            # Fast evaluation
            test_res = hits(G_att, max_iter=20)
            gain = test_res.scores[target_node] if target_node < len(test_res.scores) else 0.0

            # Revert
            G_att.remove_edge(u, v)
            if is_new:
                G_att.remove_node(u)

            if gain > best_gain:
                best_gain = gain
                best_edge = (u, v)
                is_new_node = is_new

        if best_edge is None:
            # Fallback
            best_edge = short_list[0][:2]
            is_new_node = (best_edge[0] not in G_att)

        u, v = best_edge
        if is_new_node:
            G_att.add_node(u)
            added_nodes.append(u)
        G_att.add_edge(u, v)
        added_edges.append((u, v))

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
