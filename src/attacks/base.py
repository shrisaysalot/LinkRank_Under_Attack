"""Base class and verification utilities for link injection attacks."""
from dataclasses import dataclass
from typing import List, Tuple, Union
import numpy as np
import networkx as nx
import scipy.sparse as sp


@dataclass
class AttackResult:
    """Standardized output container for link injection attacks."""
    graph: nx.DiGraph
    adj_matrix: sp.csr_matrix
    target_node: int
    added_nodes: List[int]
    added_edges: List[Tuple[int, int]]
    cost_nodes: int
    cost_edges: int

    def verify_validity(self, original_G: nx.DiGraph) -> bool:
        """Verifies that the attack only added nodes and edges (no deletions)."""
        orig_nodes = set(original_G.nodes())
        orig_edges = set(original_G.edges())

        new_nodes = set(self.graph.nodes())
        new_edges = set(self.graph.edges())

        # Original nodes and edges must be subsets
        if not orig_nodes.issubset(new_nodes):
            return False
        if not orig_edges.issubset(new_edges):
            return False

        # Added edges must match diff
        actual_added_edges = new_edges - orig_edges
        if actual_added_edges != set(self.added_edges):
            return False

        return True
