"""Unit tests for rankers validating correctness against NetworkX on small graphs."""
import numpy as np
import networkx as nx
import pytest

from src.rankers import (
    hits,
    pagerank,
    salsa,
    indegree,
    randomized_hits,
    subspace_hits
)


def create_sample_graphs():
    """Generates a collection of small directed graphs for testing."""
    graphs = []

    # 1. Simple 4-node directed cycle with shortcut
    G1 = nx.DiGraph([(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)])
    graphs.append(("cycle_with_shortcut", G1))

    # 2. Directed star graph (node 0 is hub, nodes 1..4 are authorities)
    G2 = nx.DiGraph([(0, i) for i in range(1, 5)])
    graphs.append(("star_hub", G2))

    # 3. Dense complete bipartite graph K_3,3 directed
    G3 = nx.DiGraph()
    for u in [0, 1, 2]:
        for v in [3, 4, 5]:
            G3.add_edge(u, v)
    graphs.append(("bipartite_k33", G3))

    # 4. Bow-tie graph with dangling node
    G4 = nx.DiGraph([(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 5), (5, 3)])
    graphs.append(("bowtie_dangling", G4))

    return graphs


def test_hits_vs_networkx():
    """Validates our sparse HITS implementation against NetworkX."""
    graphs = create_sample_graphs()

    for name, G in graphs:
        # NetworkX HITS
        nx_h, nx_a = nx.hits(G, max_iter=200, tol=1e-8, normalized=True)
        nodes = list(range(len(G)))
        nx_a_arr = np.array([nx_a[i] for i in nodes])
        nx_h_arr = np.array([nx_h[i] for i in nodes])

        # Our sparse HITS
        res = hits(G, tol=1e-8, max_iter=200, compute_eigengap=True)

        # Compare authority and hub scores
        # Note: NetworkX svds can have arbitrary sign before norm; both are normalized to sum=1 and >=0
        diff_a = np.max(np.abs(res.scores - nx_a_arr))
        diff_h = np.max(np.abs(res.hub_scores - nx_h_arr))

        print(f"[HITS vs NX] Graph: {name} | Max abs diff (auth): {diff_a:.2e} | (hub): {diff_h:.2e}")
        assert diff_a < 1e-4, f"HITS authority difference too high on {name}: {diff_a}"
        assert diff_h < 1e-4, f"HITS hub difference too high on {name}: {diff_h}"
        assert res.converged, f"HITS did not converge on {name}"


def test_pagerank_vs_networkx():
    """Validates our PageRank implementation against NetworkX."""
    graphs = create_sample_graphs()

    for name, G in graphs:
        # NetworkX PageRank
        nx_pr = nx.pagerank(G, alpha=0.85, tol=1e-8, max_iter=200)
        nodes = list(range(len(G)))
        nx_pr_arr = np.array([nx_pr[i] for i in nodes])

        # Our PageRank
        res = pagerank(G, alpha=0.85, tol=1e-8, max_iter=200)

        diff = np.max(np.abs(res.scores - nx_pr_arr))
        print(f"[PageRank vs NX] Graph: {name} | Max abs diff: {diff:.2e}")
        assert diff < 1e-4, f"PageRank difference too high on {name}: {diff}"
        assert res.converged, f"PageRank did not converge on {name}"


def test_salsa_basic():
    """Validates SALSA properties on bipartite and star graphs."""
    graphs = create_sample_graphs()

    for name, G in graphs:
        res = salsa(G)
        assert np.isclose(res.scores.sum(), 1.0, atol=1e-5), f"SALSA auth scores do not sum to 1 on {name}"
        assert np.isclose(res.hub_scores.sum(), 1.0, atol=1e-5), f"SALSA hub scores do not sum to 1 on {name}"
        assert np.all(res.scores >= -1e-8), f"Negative SALSA score found on {name}"


def test_indegree():
    """Validates in-degree ranker matches graph in-degrees."""
    G = nx.DiGraph([(0, 1), (2, 1), (3, 1), (1, 2)])
    res = indegree(G, normalize=True)
    # Node 1 has in-degree 3, node 2 has in-degree 1, total = 4
    expected = np.array([0.0, 3.0 / 4.0, 1.0 / 4.0, 0.0])
    diff = np.max(np.abs(res.scores - expected))
    assert diff < 1e-8, f"In-degree ranker error: {diff}"


def test_randomized_hits_stability():
    """Validates Randomized HITS converges and produces valid probability vector."""
    graphs = create_sample_graphs()
    for name, G in graphs:
        res = randomized_hits(G, eps=0.15)
        assert res.converged, f"Randomized HITS failed to converge on {name}"
        assert np.isclose(res.scores.sum(), 1.0, atol=1e-5)
        assert np.all(res.scores >= 0)


def test_subspace_hits():
    """Validates Subspace HITS returns well-formed scores."""
    graphs = create_sample_graphs()
    for name, G in graphs:
        res = subspace_hits(G, k=2)
        assert np.isclose(res.scores.sum(), 1.0, atol=1e-5)
        assert np.all(res.scores >= 0)
