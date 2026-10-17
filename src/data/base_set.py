"""Kleinberg (1999) Base Set construction from root query sets."""
from dataclasses import dataclass
from typing import List, Set, Dict, Tuple, Optional, Union
import numpy as np
import networkx as nx
import scipy.sparse as sp

from src.config import BASE_SET_ROOT_SIZE, BASE_SET_MAX_IN_LINKS


@dataclass
class BaseSet:
    """Represents an expanded Kleinberg base set subgraph."""
    graph: nx.DiGraph
    adj_matrix: sp.csr_matrix
    root_nodes: List[int]             # Indices in the base set graph
    orig_to_idx: Dict[int, int]
    idx_to_orig: Dict[int, int]
    num_nodes: int
    num_edges: int


def sample_root_set(
    G: nx.DiGraph,
    seed_node: int,
    root_size: int = BASE_SET_ROOT_SIZE,
    rng: Optional[np.random.RandomState] = None
) -> List[int]:
    """Samples a cohesive query root set of size root_size via random walk from seed_node."""
    if rng is None:
        rng = np.random.RandomState(42)

    root: Set[int] = {seed_node}
    current = seed_node

    # Neighborhood / walk expansion
    nodes_list = list(G.nodes())
    if len(nodes_list) <= root_size:
        return nodes_list

    steps = 0
    max_steps = root_size * 20
    while len(root) < root_size and steps < max_steps:
        steps += 1
        # Successors or predecessors
        neighbors = list(G.successors(current)) + list(G.predecessors(current))
        if neighbors and rng.rand() < 0.85:
            current = rng.choice(neighbors)
            root.add(current)
        else:
            # Restart or jump
            if root:
                current = rng.choice(list(root))
            else:
                current = rng.choice(nodes_list)
            root.add(current)

    # Fill if still short
    if len(root) < root_size:
        remaining = list(set(nodes_list) - root)
        needed = root_size - len(root)
        sampled = rng.choice(remaining, size=min(needed, len(remaining)), replace=False)
        root.update(sampled)

    return list(root)


def build_base_set(
    G: nx.DiGraph,
    root_set: List[int],
    max_in_links: int = BASE_SET_MAX_IN_LINKS,
    rng: Optional[np.random.RandomState] = None
) -> BaseSet:
    """Expands a root set into a Kleinberg base set:

    1. Include all pages in the root set R.
    2. Include all pages pointed to by any page in R (out-neighbors).
    3. Include up to max_in_links pages pointing to any page in R (in-neighbors).
    4. Extract induced subgraph and re-index nodes to 0..n-1.
    """
    if rng is None:
        rng = np.random.RandomState(42)

    base_nodes: Set[int] = set(root_set)

    for u in root_set:
        if not G.has_node(u):
            continue
        # Add all out-neighbors
        for v in G.successors(u):
            base_nodes.add(v)

        # Add up to max_in_links in-neighbors
        in_preds = list(G.predecessors(u))
        if len(in_preds) <= max_in_links:
            base_nodes.update(in_preds)
        else:
            sampled_preds = rng.choice(in_preds, size=max_in_links, replace=False)
            base_nodes.update(sampled_preds)

    # Induce subgraph
    subG = G.subgraph(base_nodes).copy()

    # Re-index nodes to 0..|base_nodes|-1
    sorted_nodes = sorted(list(subG.nodes()))
    orig_to_idx = {orig: idx for idx, orig in enumerate(sorted_nodes)}
    idx_to_orig = {idx: orig for idx, orig in enumerate(sorted_nodes)}

    relabeled_G = nx.relabel_nodes(subG, orig_to_idx, copy=True)
    adj = nx.adjacency_matrix(relabeled_G, nodelist=range(len(sorted_nodes)), dtype=float).tocsr()
    root_indices = [orig_to_idx[r] for r in root_set if r in orig_to_idx]

    return BaseSet(
        graph=relabeled_G,
        adj_matrix=adj,
        root_nodes=root_indices,
        orig_to_idx=orig_to_idx,
        idx_to_orig=idx_to_orig,
        num_nodes=relabeled_G.number_of_nodes(),
        num_edges=relabeled_G.number_of_edges()
    )
